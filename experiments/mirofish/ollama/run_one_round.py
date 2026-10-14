import asyncio, importlib.util, json, os, random, sqlite3, sys, time, traceback
from pathlib import Path
from datetime import datetime, timezone
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
upstream=root/"upstream"
evidence=root/"evidence"
if (evidence/"reddit_simulation.db").exists():
    raise SystemExit("Existing experiment database preserved; use a fresh experiment root.")
os.environ.update(LLM_PROVIDER="ollama",OLLAMA_MODEL="qwen3.5:4b",OLLAMA_BASE_URL="http://127.0.0.1:11434",OASIS_CLI_SEMAPHORE="1")
sys.path.insert(0,str(upstream))
random.seed(7)
result={"started_at":datetime.now(timezone.utc).isoformat(),"status":"RUNNING","engine":"pinned MiroFish RedditSimulationRunner / OASIS","upstream_ref":"3e98e776cdfc9556c12ace82a60e9d3da5bd41e7","adapter_ref":"e342084d599be9e566769c5aac962bcb194f3bed","synthetic_agents":1,"max_rounds":1,"real_simulation_completed":False,"full_pipeline_completed":False,"new_paid_api_charges_usd":0,"external_post_published":False}
target=evidence/"engine-result.json"
target.write_text(json.dumps(result,indent=2),encoding="utf-8")
t=time.monotonic()
async def run():
    spec=importlib.util.spec_from_file_location("romo_reddit_engine",upstream/"scripts/run_reddit_simulation.py")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod._shutdown_event=asyncio.Event()
    mod.RedditSimulationRunner.AVAILABLE_ACTIONS=[mod.ActionType.CREATE_POST]
    config=json.loads((evidence/"simulation_config.json").read_text(encoding="utf-8"))
    if "controlled_post_content" in config:
        from controlled_task import make_controlled_action
        from oasis.social_agent.agent import SocialAgent
        SocialAgent.perform_action_by_llm=make_controlled_action(config["controlled_post_content"])
    runner=mod.RedditSimulationRunner(str(evidence/"simulation_config.json"),wait_for_commands=False)
    await asyncio.wait_for(runner.run(max_rounds=1),timeout=300)
try:
    asyncio.run(run())
    db=evidence/"reddit_simulation.db"
    if not db.exists(): raise RuntimeError("Engine returned without a database")
    conn=sqlite3.connect(str(db))
    names=[row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    counts={}
    samples={}
    for name in names:
        escaped=name.replace('"','""')
        counts[name]=conn.execute('SELECT COUNT(*) FROM "'+escaped+'"').fetchone()[0]
        if name.lower() in ("post","posts","trace","actions"):
            cursor=conn.execute('SELECT * FROM "'+escaped+'" LIMIT 3')
            cols=[d[0] for d in cursor.description]
            samples[name]=[dict(zip(cols,row)) for row in cursor.fetchall()]
    conn.close()
    result.update(status="ENGINE_RETURNED",table_counts=counts,sample_local_actions=samples,elapsed_seconds=round(time.monotonic()-t,2))
    # An exit without a recorded post is not counted as a successful LLM action.
    posts=sum(counts.get(name,0) for name in ("post","posts"))
    if posts>0:
        result.update(status="ENGINE_ROUND_PASS",real_simulation_completed=True,rounds_completed=1,recorded_posts=posts)
    else:
        result.update(status="NO_RECORDED_POST",rounds_completed_unknown=True)
    task=json.loads((evidence/"simulation_config.json").read_text(encoding="utf-8"))
    if "controlled_post_content" in task:
        result["exact_content_pass"]=(posts==1 and samples.get("post", [{}])[0].get("content")==task["controlled_post_content"])
        if not result["exact_content_pass"]:
            result["status"]="CONTENT_FIDELITY_FAILED"
except BaseException as exc:
    result.update(status="FAILED",error_type=type(exc).__name__,error=str(exc),elapsed_seconds=round(time.monotonic()-t,2))
    (evidence/"engine-traceback.txt").write_text(traceback.format_exc(),encoding="utf-8")
target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
sys.exit(0 if result["status"]=="ENGINE_ROUND_PASS" else 1)
