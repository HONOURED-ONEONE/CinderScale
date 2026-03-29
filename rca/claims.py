from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ClaimState(str, Enum):
    VerifiedHealthy = "VerifiedHealthy"
    WeaklyVerified = "WeaklyVerified"
    EpistemicallyUnverified = "EpistemicallyUnverified"
    Contradicted = "Contradicted"
    PreIncidentEscalated = "PreIncidentEscalated"

class ClaimEvidenceSummary(BaseModel):
    has_metrics: bool
    has_logs: bool
    has_traces: bool
    topology_confidence: float
    anomaly_count: int

class ClaimEvaluationResult(BaseModel):
    service: str
    state: ClaimState
    confidence: float
    evidence: ClaimEvidenceSummary
    rationale: str
    # CEF Prioritization extensions
    forecast_risk: float = 0.0
    priority_boost: float = 0.0
    forecast_metadata: Optional[Dict[str, Any]] = None

def evaluate_service_claims(events: Dict[str, Any], topo: Dict[str, Any], signals: Dict[str, Any], tss_data: tuple) -> List[ClaimEvaluationResult]:
    """
    Derives initial health claims for all services seen in the topology or events,
    incorporating forecasted risk for prioritization.
    """
    from rca.forecasting import get_forecast # Deferred import to avoid circular dep
    
    tss_score, missing_signals = tss_data
    results = []
    
    # Identify all services
    services = set(topo.get("nodes", [])) # Assuming topo nodes are service names
    if not services:
        # Fallback to services seen in logs/metrics
        services.update(set(l.get("service") for l in events.get("logs", []) if l.get("service")))
        services.update(set(m.get("service") for m in events.get("metrics", []) if m.get("service")))

    anomalies = signals.get("anomalies", [])
    
    for svc in services:
        # 1. Heuristic evidence gathering
        has_metrics = any(m.get("service") == svc for m in events.get("metrics", []))
        has_logs = any(l.get("service") == svc for l in events.get("logs", []))
        has_traces = any(any(s.get("service") == svc for s in t.get("spans", [])) for t in events.get("traces", []))
        
        svc_anomalies = [a for a in anomalies if svc in str(a)]
        anomaly_count = len(svc_anomalies)
        
        topo_conf = topo.get("confidence", 0.0)
        
        evidence = ClaimEvidenceSummary(
            has_metrics=has_metrics,
            has_logs=has_logs,
            has_traces=has_traces,
            topology_confidence=topo_conf,
            anomaly_count=anomaly_count
        )
        
        # 2. Heuristic State Determination
        state = ClaimState.EpistemicallyUnverified
        confidence = 0.5
        rationale = "No telemetry observed."
        
        if not (has_metrics or has_logs or has_traces):
            state = ClaimState.EpistemicallyUnverified
            confidence = 0.0
        elif anomaly_count > 0:
            state = ClaimState.Contradicted
            confidence = 0.9
            rationale = f"Detected {anomaly_count} anomalies."
        elif tss_score > 0.8 and topo_conf > 0.8:
            state = ClaimState.VerifiedHealthy
            confidence = 0.95
            rationale = "Strong telemetry and topology confidence with no anomalies."
        elif has_metrics or has_logs:
            state = ClaimState.WeaklyVerified
            confidence = 0.6
            rationale = "Partial telemetry observed with no anomalies."

        # 3. Forecast-Aware Prioritization
        forecast = get_forecast(scope=svc)
        risk = forecast.get("risk_score", 0.0)
        boost = 0.0
        if risk > 0.5:
            boost = risk * 0.5 # Scale priority based on verifiability risk
            rationale += f" [Forecast: High verifiability risk +{boost}]"
            
        results.append(ClaimEvaluationResult(
            service=svc,
            state=state,
            confidence=confidence,
            evidence=evidence,
            rationale=rationale,
            forecast_risk=risk,
            priority_boost=boost,
            forecast_metadata=forecast
        ))
        
    return results
