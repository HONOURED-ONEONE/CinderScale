import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class HistoryEntry(BaseModel):
    timestamp: str
    run_id: str
    scope: str  # service name or 'system'
    tss: float
    missing_traces: int
    missing_corr_ids: int
    missing_metrics: int
    missing_changes: int
    topology_conf: float
    edge_count: int
    avg_edge_conf: float
    evidence_diversity: float
    anomaly_count: int
    is_deploy: int
    contradiction_count: int
    hotspot_score: float = 0.0

class HistoryStore:
    def __init__(self, storage_path: str = "rca_history.jsonl"):
        self.storage_path = storage_path

    def record_pass(self, run_id: str, pipeline_result: Dict[str, Any], epistemic_state: Optional[Dict[str, Any]] = None):
        """Records features from a single pipeline pass."""
        timestamp = datetime.now().isoformat()
        
        # System-level entry
        system_entry = HistoryEntry(
            timestamp=timestamp,
            run_id=run_id,
            scope="system",
            tss=pipeline_result.get("tss", 0.0),
            missing_traces=1 if "distributed_traces" in pipeline_result.get("missing", []) else 0,
            missing_corr_ids=1 if "correlation_ids_in_logs" in pipeline_result.get("missing", []) else 0,
            missing_metrics=1 if "key_metrics" in pipeline_result.get("missing", []) else 0,
            missing_changes=1 if "change_events" in pipeline_result.get("missing", []) else 0,
            topology_conf=pipeline_result.get("topology_summary", {}).get("confidence", 0.0),
            edge_count=pipeline_result.get("topology_summary", {}).get("edge_count", 0),
            avg_edge_conf=pipeline_result.get("topology_summary", {}).get("avg_edge_conf", 0.0),
            evidence_diversity=pipeline_result.get("inventory", {}).get("evidence_diversity", 0.0),
            anomaly_count=len(pipeline_result.get("debug", {}).get("signals", {}).get("anomalies", [])),
            is_deploy=1 if pipeline_result.get("architecture_flags", {}).get("is_deploy", False) else 0,
            contradiction_count=len(epistemic_state.get("contradictions", [])) if epistemic_state else 0
        )
        self._write_entry(system_entry)

        # Per-service entries (derived from health claims if available)
        if epistemic_state and "health_claims" in epistemic_state:
            for claim in epistemic_state["health_claims"]:
                svc = claim["service"]
                # Filter contradictions for this service
                svc_contradictions = [c for c in epistemic_state.get("contradictions", []) if c.get("service") == svc]
                
                entry = HistoryEntry(
                    timestamp=timestamp,
                    run_id=run_id,
                    scope=svc,
                    tss=pipeline_result.get("tss", 0.0), # Global TSS for now
                    missing_traces=system_entry.missing_traces,
                    missing_corr_ids=system_entry.missing_corr_ids,
                    missing_metrics=system_entry.missing_metrics,
                    missing_changes=system_entry.missing_changes,
                    topology_conf=system_entry.topology_conf,
                    edge_count=system_entry.edge_count,
                    avg_edge_conf=system_entry.avg_edge_conf,
                    evidence_diversity=system_entry.evidence_diversity,
                    anomaly_count=1 if any(svc in str(a) for a in pipeline_result.get("debug", {}).get("signals", {}).get("anomalies", [])) else 0,
                    is_deploy=1 if any(svc == c.get("service") for c in pipeline_result.get("debug", {}).get("events", {}).get("changes", []) if c.get("type") == "deploy") else 0,
                    contradiction_count=len(svc_contradictions)
                )
                self._write_entry(entry)

    def _write_entry(self, entry: HistoryEntry):
        with open(self.storage_path, "a") as f:
            f.write(entry.model_dump_json() + "\n")

    def export_to_csv(self, csv_path: str):
        if not os.path.exists(self.storage_path):
            return
        
        with open(self.storage_path, "r") as f_in, open(csv_path, "w", newline='') as f_out:
            writer = None
            for line in f_in:
                data = json.loads(line)
                if not writer:
                    writer = csv.DictWriter(f_out, fieldnames=data.keys())
                    writer.writeheader()
                writer.writerow(data)

    def load_history(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.storage_path):
            return []
        entries = []
        with open(self.storage_path, "r") as f:
            for line in f:
                entries.append(json.loads(line))
        return entries
