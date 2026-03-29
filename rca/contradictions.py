from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ContradictionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ContradictionType(str, Enum):
    MissingTrace = "MissingTrace"
    UncorrelatedAnomaly = "UncorrelatedAnomaly"
    UnverifiedDeploy = "UnverifiedDeploy"
    WeakTopology = "WeakTopology"
    AlertVsHealthClaim = "AlertVsHealthClaim"

class Contradiction(BaseModel):
    type: ContradictionType
    scope: str
    severity: ContradictionSeverity
    description: str
    evidence_refs: List[str]

def detect_contradictions(events: Dict[str, Any], topo: Dict[str, Any], signals: Dict[str, Any], tss_data: tuple) -> List[Contradiction]:
    """
    Detects contradictions in the current telemetry pass.
    """
    tss_score, missing_signals = tss_data
    contradictions = []
    
    # 0. AlertVsHealthClaim (New: Basic CEF rule)
    alerting_services = {a.get("service") for a in events.get("alerts", []) if a.get("service")}
    for svc in alerting_services:
        # Check if we have logs or metrics that would otherwise claim health
        has_health_logs = any(l.get("service") == svc and l.get("level") in ["INFO", "DEBUG"] for l in events.get("logs", []))
        if has_health_logs:
            contradictions.append(Contradiction(
                type=ContradictionType.AlertVsHealthClaim,
                scope=svc,
                severity=ContradictionSeverity.HIGH,
                description=f"Service '{svc}' has active alerts but continues to emit success logs, suggesting a partial failure or mask.",
                evidence_refs=["alerts", "logs"]
            ))

    # 1. MissingTraceContradiction
    if "distributed_traces" in missing_signals:
        anomalies = signals.get("anomalies", [])
        if anomalies:
            contradictions.append(Contradiction(
                type=ContradictionType.MissingTrace,
                scope="Global/Dependencies",
                severity=ContradictionSeverity.HIGH,
                description="Anomalies detected in logs/metrics, but distributed traces are absent, preventing causal verification.",
                evidence_refs=anomalies
            ))

    # 2. UncorrelatedAnomalyContradiction
    if "correlation_ids_in_logs" in missing_signals:
        metrics = events.get("metrics", [])
        if any(m.get("value", 0) > 0.5 for m in metrics): # Heuristic spike
             contradictions.append(Contradiction(
                type=ContradictionType.UncorrelatedAnomaly,
                scope="Service Logs",
                severity=ContradictionSeverity.MEDIUM,
                description="Metric spikes detected without corresponding correlation IDs in logs.",
                evidence_refs=["metrics"]
            ))

    # 3. UnverifiedDeployContradiction
    changes = events.get("changes", [])
    deploys = [c for c in changes if c.get("type") == "deploy"]
    if deploys:
        # Check for post-deploy logs/metrics
        for deploy in deploys:
            svc = deploy.get("service")
            has_logs = any(l.get("service") == svc for l in events.get("logs", []))
            if not has_logs:
                contradictions.append(Contradiction(
                    type=ContradictionType.UnverifiedDeploy,
                    scope=svc,
                    severity=ContradictionSeverity.HIGH,
                    description=f"Deployment detected for '{svc}', but no subsequent log evidence verifies health.",
                    evidence_refs=[f"deploy_id:{deploy.get('version', 'unknown')}"]
                ))

    # 4. WeakTopologyContradiction
    topo_conf = topo.get("confidence", 0.0)
    if topo_conf < 0.6:
        contradictions.append(Contradiction(
            type=ContradictionType.WeakTopology,
            scope="Global Topology",
            severity=ContradictionSeverity.MEDIUM,
            description=f"Topology confidence ({topo_conf}) is low while evaluating incident, weakening causal claims.",
            evidence_refs=["topo_summary"]
        ))

    return contradictions
