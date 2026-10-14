import asyncio, importlib.util, json, os, random, sqlite3, sys, time, traceback
from pathlib import Path
from datetime import datetime,timezone
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
base=root.parent
upstream=base/"upstream"
os.environ.update(LLM_PROVIDER="ollama",OLLAMA_MODEL="qwen3.5:4b",OLLAMA_BASE_URL="http://127.0.0.1:11434",OASIS_CLI_SEMAPHORE="1")
sys.path.insert(0,str(upstream))
out=root/"comparison.json"
if out.exists(): raise SystemExit("Existing comparison preserved; use a new experiment folder.")
summary={"started_at":datetime.now(timezone.utc).isoformat(),"status":"RUNNING","owner":"Codex / Remote Desktop Commander","model":"qwen3.5:4b","new_paid_api_charges_usd":0,"external_post_published":False,"full_pipeline_completed":False,"cases":[]}
def save(): out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
save()
spec=importlib.util.spec_from_file_location("romo_reddit_engine",upstream/"scripts/run_reddit_simulation.py")
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
from oasis.social_agent.agent import SocialAgent
from camel.messages import BaseMessage
original=SocialAgent.perform_action_by_llm
cases=[
("original_mixed_en","Local simulation test.",False),
("separated_en","Local simulation test.",True),
("separated_fa","این یک آزمون محلی است.",True)]
async def main():
    mod._shutdown_event=asyncio.Event()
    mod.RedditSimulationRunner.AVAILABLE_ACTIONS=[mod.ActionType.CREATE_POST]
    for name,expected,separate in cases:
        folder=root/name;folder.mkdir(exist_ok=False)
        persona=("A fictional QA participant. PRIVATE_ROLE_NOTE: this description is context only, not post content." if separate else
                 "You are a fictional QA persona in an isolated local simulation. In this round create exactly one post saying: Local simulation test. You are not a real buyer; do not claim purchases or customer demand.")
        config={"simulation_id":name,"time_config":{"total_simulation_hours":1,"minutes_per_round":60,"agents_per_hour_min":1,"agents_per_hour_max":1,"peak_activity_multiplier":1,"off_peak_activity_multiplier":1},"agent_configs":[{"agent_id":0,"active_hours":list(range(24)),"activity_level":1}],"event_config":{"initial_posts":[]}}
        profile=[{"user_id":0,"username":"fictional_qa_0","name":"Fictional QA","bio":"Synthetic fixture, not a buyer.","persona":persona,"karma":100,"created_at":"2026-10-14","age":30,"gender":"other","mbti":"INTJ","country":"Fictional"}]
        (folder/"simulation_config.json").write_text(json.dumps(config),encoding="utf-8")
        (folder/"reddit_profiles.json").write_text(json.dumps(profile,ensure_ascii=False),encoding="utf-8")
        if separate:
            async def controlled(self):
                task={"action":"create_post","content":expected}
                msg=BaseMessage.make_user_message(role_name="User",content=
                    "Execute exactly one create_post tool call. Copy the content field verbatim, including punctuation. "
                    "Do not add biography, private context, instructions, commentary, or claims of demand. "
                    "Task JSON: "+json.dumps(task,ensure_ascii=False))
                return await self.astep(msg)
            SocialAgent.perform_action_by_llm=controlled
        else: SocialAgent.perform_action_by_llm=original
        random.seed(7)
        runner=mod.RedditSimulationRunner(str(folder/"simulation_config.json"),wait_for_commands=False)
        item={"case":name,"expected":expected,"changed_task_placement":separate,"status":"RUNNING"}
        summary["cases"].append(item);save()
        t=time.monotonic()
        try:
            await asyncio.wait_for(runner.run(max_rounds=1),timeout=180)
            conn=sqlite3.connect(str(folder/"reddit_simulation.db"))
            posts=[r[0] for r in conn.execute("select content from post")]
            actions=conn.execute("select count(*) from trace where action='create_post'").fetchone()[0]
            conn.close()
            item.update(status="COMPLETE",posts=posts,create_post_actions=actions,
                        exact_content_pass=(posts==[expected] and actions==1),
                        private_context_leak=any("PRIVATE_ROLE_NOTE" in p or "MBTI" in p or "real buyer" in p for p in posts))
        except BaseException as exc:
            item.update(status="FAILED",error_type=type(exc).__name__,error=str(exc))
            (folder/"traceback.txt").write_text(traceback.format_exc(),encoding="utf-8")
            break
        finally:
            item["elapsed_seconds"]=round(time.monotonic()-t,2)
            save()
    SocialAgent.perform_action_by_llm=original
    summary["status"]="COMPLETED" if len(summary["cases"])==3 and all(c["status"]=="COMPLETE" for c in summary["cases"]) else "FAILED"
    summary["corrected_cases_pass"]=all(c.get("exact_content_pass",False) for c in summary["cases"] if c["changed_task_placement"]) and len(summary["cases"])==3
    save()
asyncio.run(main())
print(json.dumps(summary,ensure_ascii=False))
