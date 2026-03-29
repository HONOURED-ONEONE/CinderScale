# RCA Copilot (Hybrid Architecture)

This repository contains a hybrid RCA analytical system combining a high-performance Python engine with a .NET control plane.

## Architecture Overview

1.  **Python Analytical Engine (`api.py`)**: FastAPI service that executes the core RCA pipeline, AOGC adaptation, and Continuous Epistemic Falsification (CEF).
2.  **NET Control Plane (`services/control-plane/`)**: Production orchestrator that polls a shared telemetry folder and delegates analysis to the Python API.
3.  **Streamlit Dashboard (`app.py`)**: UI for visualizing RCA results, health claims, contradictions, and the falsification ledger.

## Startup Order (Local Development)

To run the full hybrid system:

1.  **Start Python Analytical Engine**:
    ```bash
    # From project root
    python api.py
    ```
    API will be available at `http://localhost:8000`.

2.  **Start .NET Control Plane**:
    ```bash
    cd services/control-plane
    dotnet run
    ```
    Control Plane will be available at `http://localhost:5000`.

3.  **Start Streamlit Dashboard**:
    ```bash
    # From project root
    streamlit run app.py
    ```
    UI will be available at `http://localhost:8501`.

## End-to-End Smoke Verification

A local smoke test is provided to verify the analytical engine, history recording, and persistent graph population.

```bash
python tests/reproduce_smoke.py
```

This script:
1.  Loads a sample run from `shared_demo_root/current/`.
2.  Executes the full AOGC + CEF pipeline.
3.  Verifies that `rca_history.jsonl` and `reliability_graph.json` are populated.

## Testing

### Python Tests
```bash
pytest
```

### .NET Tests
```bash
cd services/control-plane/ControlPlane.Tests
dotnet test
```

## Telemetry Input Specification

The control plane watches `shared_demo_root/current/` for:
- `READY`: Marker file indicating a complete dataset.
- `manifest.json`: Metadata (run_id, scenario, variant).
- `alerts.jsonl`, `logs.jsonl`, `metrics.jsonl`, `traces.jsonl`, `changes.jsonl`: Telemetry data in JSONL format.
