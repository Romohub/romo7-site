# Verified local OASIS engine round

Owner: Codex. One synthetic persona, one round, CREATE_POST only.

The pinned MiroFish RedditSimulationRunner executed against the local qwen3.5:4b model using the native CAMEL Ollama backend. The run returned, the environment closed, and an independent SQLite check found one post plus one create_post trace action. Total process time including cold imports was 138.76 seconds; the engine loop reported 24.2 seconds.

Engine execution: PASS. Exact post-content fidelity: FAIL. The generated post incorporated persona/instruction text beyond the requested sentence. This does not validate output quality, buyer demand, or sales predictions.

Full ontology/graph/profile-generation/report pipeline: not run. No external post was published. New paid API charges: zero; electricity not measured.

The isolated engine environment and uv cache are on D:\RomoExperiments\MiroFish-20261014. Replay with the saved harness by passing that experiment root as its first argument; config/profiles are recorded on the device. The engine script removes its experiment database when starting, so use a fresh root to preserve prior evidence.
