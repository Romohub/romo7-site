# Experimental local Ollama connection

Owner: Codex. Priority: normal. Deadline: none. Status: implemented; live MiroFish client probe pending device connectivity.

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

Eight tests exercise the actual patched upstream LLMClient and Config with a
local HTTP fixture, lightweight package loading, and a stub dotenv loader/logger.
They do not run a live model, the full MiroFish dependency stack, or a social
simulation. The original model-free readiness workflow is preserved.

Previously verified: one direct Ollama response on the user's device.
Not yet verified: live response through the patched MiroFish client; downstream
simulation model plumbing; a complete simulation; output quality or buyer demand.
Next action: when the existing device is reachable, exercise the patched client
against its installed local Ollama model, then assess the remaining full-pipeline
requirements before launching any simulation.
New paid API charges: zero. Electricity not measured.
