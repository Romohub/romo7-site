# Experimental local Ollama connection

Owner: Codex. Priority: normal. Deadline: none. Status: live LLMClient response verified; full simulation pending.

This is an isolated compatibility patch for GianniDerieuw/mirofish commit
3e98e776cdfc9556c12ace82a60e9d3da5bd41e7. It modifies Config, LLMClient, and the
doctor's executable lookup in a separate checkout, and copies a stdlib Ollama
adapter into app/utils. It does not change the external upstream repository.

Prepare a pristine pinned checkout:

```sh
python experiments/mirofish/ollama/install_adapter.py /path/to/pinned-checkout
```

Use LLM_PROVIDER=ollama, OLLAMA_MODEL=qwen3.5:4b and
OLLAMA_BASE_URL=http://127.0.0.1:11434. Only this verified local model and
loopback HTTP endpoints are permitted. Proxy environment and HTTP redirects
are disabled; requests have a 90-second timeout, a 2048-token output ceiling,
and no automatic retry. Incomplete, empty, mismatched-model, and truncated
responses fail rather than being counted as completed.

Validation:

```sh
python experiments/mirofish/ollama/test_adapter.py /path/to/pristine-pinned-checkout
```

Ten tests exercise the actual patched upstream LLMClient and Config with a
local HTTP fixture, lightweight package loading, and a stub dotenv loader/logger; the routing test substitutes a CAMEL constructor.
They do not run a live model, the full MiroFish dependency stack, or a social
simulation. The original model-free readiness workflow is preserved.

Verified: one live JSON response through the patched MiroFish LLMClient. A direct native Ollama tool-call probe returned the expected tool but omitted a required final period in its text argument; exact fidelity failed.
The OASIS provider path now selects native CAMEL OllamaModel rather than the CLI bridge which ignores tool schemas. A separate CI test exercises the real CAMEL/OpenAI SDK against an HTTP fixture and checks preservation of tool schemas and returned tool calls.
Not yet verified: live CAMEL model response, a complete simulation, output quality or buyer demand.
Next action: prepare a separate full-engine environment and verify a bounded synthetic round. Dependencies were missing in the default uv Python environment probed on the device; other environments were not inventoried.
New paid API charges: zero. Electricity not measured.
