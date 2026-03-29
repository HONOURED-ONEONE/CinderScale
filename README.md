# RCA Copilot (Demo)

## Run

```bash
cd ~/RCA-copilot
pip install -r requirements.txt
streamlit run app.py
```

## Expected input (from TelemetryStorm)

RCA Copilot watches a shared folder (default `shared_demo_root/current`).
TelemetryStorm should atomically swap a fully generated dataset into `current/`.

`current/` must contain:
- `READY` marker file
- `manifest.json` (written last)
- `alerts.jsonl`, `logs.jsonl`, `metrics.jsonl`, `changes.jsonl`
- `traces.jsonl` optional (variant dependent)

Optional:
- `truth.json` for accuracy display (not required)
- `stats.json` for quick UI info

## Policy model

If `policy/model.joblib` exists, AOGC uses it to choose one adaptation action and reruns once.
If missing, a rule-based fallback action is used so the demo still works.

---

## Analytical Engine API Boundaries

The Python codebase has been refactored to cleanly separate the runtime orchestrator, the UI, and the analytical core:

1. **`app.py`**: Now purely a Streamlit UI layer.
2. **`rca/runtime.py`**: A new orchestrator module encapsulating directory polling and analysis invocation.
3. **`api.py`**: A standalone FastAPI service wrapping the core analytical pipeline (`run_pipeline_once` and `run_with_aogc`), decoupled from folder-polling logic.
4. **`rca/schemas.py`**: Typed, explicit Pydantic models for incoming telemetry and output RCA bundles, including forward-compatibility structures for continuous Epistemic Falsification (Health Claims and Contradictions).

### Running the .NET Control Plane

The `.NET` Control Plane service is located under `services/control-plane`. It acts as the production orchestrator, polling the shared folder and delegating analysis to the Python API.

To run it locally:
```bash
cd services/control-plane
dotnet run
```
It runs an ASP.NET Core API on ports `http://localhost:5000` (or 5xxx depending on your environment).
You can hit endpoints like `GET /control/status` or `GET /control/latest-analysis`.
