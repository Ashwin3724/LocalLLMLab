# LocalLLMLab audit

This is a self-audit, not an independent security, model-quality or privacy audit.

## Checks and corrections

- Identified that a local Ollama endpoint may forward to cloud models. UI and README now require disabling Ollama cloud for local-only operation, and filter common :cloud/-cloud names. Aliases and server configuration cannot be proven local by this app.
- Did not bundle or claim any live model results. Automated provider tests and browser integration used fake Ollama responses; no real model or live Ollama inference was tested.
- Validated category/priority schema and JSON. Non-stop completion reasons do not count as valid/exact. Request failures are surfaced, not counted as valid outcomes.
- Corrected token throughput to include only cases with both valid token and duration counters. Throughput uses Ollama generation duration, while mean wall time includes local HTTP overhead and potential cold loads.
- Captured model tags, reported metadata, settings, platform and prompt in JSON export. Documented that model digests, full hardware details, memory, warm-ups, repeated runs and statistical uncertainty are missing.
- Clarified that two model sizes are not a fair quantization-only comparison; the app neither quantizes nor trains models.
- Model tags come from the local server, not free-form command execution; there is no shell invocation or user-controlled provider URL. Known cloud-name filtering is only a heuristic.
- Added table scroll hints and a JSON download. The frontend renders untrusted model output via textContent, not as HTML. The app binds to loopback and rejects cross-origin/Host requests, but has no authentication and is not a public service.
- Fifteen automated tests cover schema validation, result math, completion truncation, model selection and error paths; browser smoke tests used a fake Ollama server. No performance claim should be made from mock output.

## Remaining issues

Six synthetic task cases, fixed order and one run are inadequate for meaningful evaluation. No warm-up, peak memory, real model download, repeated trial, model digest or real benchmark was tested. A failed call aborts the benchmark. The API uses a 180-second per-call timeout; total benchmark time can be much longer. Ollama cloud settings must be configured separately. Linux was tested; Windows was not. Versions are ranged, not locked.
