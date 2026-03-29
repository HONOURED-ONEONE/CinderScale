import json
import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class LedgerEntry(BaseModel):
    timestamp: str
    run_id: str
    claim_evaluations: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    probe_action: Optional[str] = None
    outcome: Optional[str] = None

class FalsificationLedger:
    def __init__(self, storage_path: str = "ledger.jsonl"):
        self.storage_path = storage_path

    def append_entry(self, entry: LedgerEntry):
        with open(self.storage_path, "a") as f:
            f.write(entry.model_dump_json() + "\n")

    def list_recent(self, limit: int = 10) -> List[LedgerEntry]:
        entries = []
        try:
            with open(self.storage_path, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    entries.append(LedgerEntry.model_validate_json(line))
        except FileNotFoundError:
            pass
        return entries

    def get_claim_history(self, service: str) -> List[Dict[str, Any]]:
        history = []
        try:
            with open(self.storage_path, "r") as f:
                for line in f:
                    entry = LedgerEntry.model_validate_json(line)
                    for claim in entry.claim_evaluations:
                        if claim.get("service") == service:
                            history.append({
                                "timestamp": entry.timestamp,
                                "run_id": entry.run_id,
                                "state": claim.get("state"),
                                "confidence": claim.get("confidence")
                            })
        except FileNotFoundError:
            pass
        return history
