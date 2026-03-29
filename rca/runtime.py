import time
from typing import Optional, Dict, Any

from rca.loader import load_run
from rca.orchestrator import run_with_aogc


class RCARuntime:
    """
    Encapsulates the runtime logic for polling the shared directory and running the RCA pipeline.
    This separates the orchestration and analysis invocation from the UI rendering layer.
    """
    def __init__(self, current_dir: str, model_path: str):
        self.current_dir = current_dir
        self.model_path = model_path
        self.last_run_id: Optional[str] = None
        self.last_loaded_at: Optional[str] = None
        self.run_data: Optional[Dict[str, Any]] = None
        self.result_bundle: Optional[Dict[str, Any]] = None

    def poll_once(self) -> bool:
        """
        Polls the shared directory once. 
        Returns True if a new run was loaded and analyzed, False otherwise.
        """
        run = load_run(self.current_dir)
        if run is None:
            self.run_data = None
            self.result_bundle = None
            return False

        run_id = run["manifest"].get("run_id")
        if run_id != self.last_run_id:
            self.last_run_id = run_id
            self.last_loaded_at = time.strftime("%Y-%m-%d %H:%M:%S")
            self.run_data = run
            self.result_bundle = run_with_aogc(run, model_path=self.model_path)
            return True
        return False
