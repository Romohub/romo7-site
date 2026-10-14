# Controlled task placement comparison

Owner: Codex. Completed three real one-round local OASIS cases using qwen3.5:4b.

| Case | Exact content | Persona/instruction copied |
|---|---|---|
| Original task inside persona | Fail | Yes |
| Separate user task, English | Pass | No |
| Separate user task, Persian | Pass | No |

SQLite was independently read for both corrected cases. Persona and task placement both changed, so this comparison demonstrates a practical input correction rather than isolating a single causal factor. Only two corrected examples were tested; broader reliability is unknown. Time comparisons are not a benchmark because model/cache warmness differs.

The controlled task helper preserves quotes, newlines, and Unicode through JSON encoding. Set controlled_post_content in the experiment config and keep persona descriptive. This explicitly overrides organic action prompting for scripted QA; it must not be presented as a prediction of buyer behavior. The one-round harness refuses to replace an existing experiment database and marks content mismatch as failure.

No external publication, no paid API charge. Electricity not measured. Full MiroFish pipeline still untested.
