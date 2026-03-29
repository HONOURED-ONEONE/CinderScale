from fastapi import FastAPI, HTTPException
from typing import Optional
import uvicorn

from rca.schemas import RunData, RCABundle
from rca.orchestrator import run_with_aogc
from rca.incidents import build_one_incident
from rca.pipeline_core import run_pipeline_once

app = FastAPI(
    title="RCA Copilot Analytical Engine",
    description="Python analytical engine exposing the core pipeline for a production control plane.",
    version="1.1.0"
)

@app.get("/health")
def health_check():
    """Simple health check for orchestrator polling."""
    return {"status": "ok"}

import time
import logging
from rca.history import HistoryStore

logger = logging.getLogger("rca_api")
logging.basicConfig(level=logging.INFO)
history_store = HistoryStore()

@app.post("/analyze/run", response_model=RCABundle)
def analyze_run(run_data: RunData, model_path: Optional[str] = "policy/model.joblib"):
    """
    Executes the RCA pipeline and Epistemic Falsifier continuously 
    over the incoming raw run bundle, running normalization and AOGC adaptation.
    """
    start_time = time.time()
    try:
        # Pydantic dump for compatibility with the existing dictionary-based Python engine
        raw_dict = run_data.model_dump()
        bundle_dict = run_with_aogc(raw_dict, model_path=model_path)
        
        # --- Task 1/11: Record History and Structured Log ---
        bundle = RCABundle(**bundle_dict)
        history_store.record_pass(run_data.manifest.run_id, bundle.final.model_dump(), bundle.final.epistemic_state.model_dump() if bundle.final.epistemic_state else None)
        
        duration = (time.time() - start_time) * 1000
        logger.info(f"AnalysisComplete: run_id={run_data.manifest.run_id} duration_ms={duration:.2f} tss={bundle.final.tss:.2f}")
        
        return bundle
    except Exception as e:
        logger.error(f"AnalysisFailed: run_id={run_data.manifest.run_id} error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/normalized", response_model=RCABundle)
def analyze_normalized(run_data: RunData, strategy: dict):
    """
    Executes the pipeline ONCE directly over pre-normalized events,
    bypassing AOGC adaptation and loader logic.
    """
    try:
        events = run_data.model_dump()
        incident = build_one_incident(events)
        result = run_pipeline_once(events, incident, strategy)
        
        # Wrap single run result in an RCABundle structure
        return RCABundle(
            baseline=result,
            final=result,
            kept="baseline"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
