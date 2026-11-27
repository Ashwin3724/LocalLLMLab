# LocalLLMLab — Local Model Benchmark

Preview image is included in encoded form; run `python restore_assets.py` to restore `docs/screenshot.png` locally.
A small local benchmarking dashboard for comparing **two Ollama model tags** on six fictional support-message classification cases. It records JSON validity, exact-match task outcomes, per-case wall time and, when Ollama provides it, generation throughput. It does not train or quantize models, prove one model is generally better, or measure RAM. The project does not bundle Ollama or any model weights.

> **Live inference was not tested in the development environment.** Automated tests and a browser integration test used a fake Ollama server. Real model behavior, availability, latency, memory requirements and compatibility must be tested on your own computer.

## Set up on Windows

1. Install Python 3.11–3.13 and [Ollama for Windows](https://docs.ollama.com/windows). Start Ollama. Ollama normally serves `127.0.0.1:11434`.
2. **Disable Ollama cloud features** if you want local-only inference. Ollama can forward cloud models through its local API, so localhost by itself is not a privacy guarantee. Follow the [official local-only instructions](https://docs.ollama.com/faq#how-do-i-disable-ollamas-cloud-features) and restart Ollama. For example, set `disable_ollama_cloud: true` in the existing Ollama `server.json` as the documentation explains; don't overwrite unrelated settings. The app filters common `:cloud` and `-cloud` tags but cannot prove that custom model aliases are local.
3. Download two local model tags that your computer can run. For a concrete starting example, check the license and your hardware first, then use Command Prompt:

   ```cmd
   ollama pull llama3.2:1b
   ollama pull llama3.2:3b
   ```

   At the time of writing the [Ollama model page](https://ollama.com/library/llama3.2) lists these at roughly 1.3 GB and 2.0 GB to download, respectively. Storage and RAM needs, availability and licenses vary. These are **different model sizes**, not two quantizations of the same model. Select appropriate local quantized tags separately if you want a quantization experiment, and verify model identity and metadata yourself.
4. Extract this ZIP. In the `LocalLLMLab` folder, type `cmd` in the File Explorer address bar and press Enter. Run:

   ```cmd
   python run.py
   ```

   Use `py run.py` if needed. Internet is required to install the Python packages on first launch. Open http://127.0.0.1:8040/ after the app is ready. Keep the window open; Ctrl+C stops the dashboard. On macOS/Linux use `python3 run.py`. If the port is occupied, in Windows run `set PORT=8041` and then `python run.py`.
5. Click **Refresh installed models**, choose two different installed local tags, and run the benchmark. Twelve calls run sequentially; CPU inference can take several minutes. Download results using the JSON button.

Model installation is separate from this ZIP and may require substantial storage, RAM, internet and acceptance of model-specific terms. Inference can run offline only after packages and local models have been installed and cloud features are disabled. This app has no provider API key field; a separately configured Ollama instance can still use cloud features if not disabled.

## Measurement methodology

- Six fixed, fictional text requests with hand-authored category (`billing`, `access`, `bug`, `other`) and priority (`high`, `normal`) labels. The model receives task instructions and a request, not the answer labels.
- Each model is called sequentially once per example via Ollama `/api/generate`, with JSON output requested, temperature 0, seed 42 and `num_predict` 128. A response must be valid JSON containing exactly the allowed two keys and values, and not report a non-stop completion reason, to be counted valid. Exact match requires both fields to match the label.
- Mean wall time includes HTTP and server overhead; it is measured in the app with a monotonic timer. Throughput sums paired Ollama `eval_count` tokens and `eval_duration` nanoseconds, then divides tokens by seconds. See [Ollama usage documentation](https://docs.ollama.com/api/usage).
- Fixed order, six cases, one repeat and **no warm-up** mean load and cache effects can confound comparisons. No peak RAM, energy, safety, statistically meaningful accuracy, or tokenization fairness measurement is included. JSON export records outputs, task settings, time, platform and reported model metadata where available, but not complete hardware details. Record those yourself.
- Model tags and quantization labels come from Ollama; verify whether two tags have the same base model and different quantizations. The application does not create quantized models.

Expand the held-out task dataset, check labels, run multiple repetitions with alternating order and controlled warm-ups, record hardware and model digests, and report distributions before drawing conclusions. Never publish results from the fake server as model performance.

## Code and tests

`app/benchmark.py` owns cases, provider calls and metrics; `app/main.py` exposes local API endpoints; `app/static/` is the UI. `docs/AUDIT.md` explains the system and limitations. API docs are at http://127.0.0.1:8040/docs.

Windows tests after starting the app once:

```cmd
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
```

On macOS/Linux use `.venv/bin/python`. Tests use a mocked provider; passing does not verify real Ollama or model inference. This local single-user server has no login; do not expose it to a network. Code and documentation were AI-assisted. Learn, test and modify it, and present only your own work on a CV. Project code is MIT; Ollama and models have their own terms.
