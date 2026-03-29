from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Recommendation(BaseModel):
    action_id: str
    target: str
    priority: float # 0.0 to 1.0
    rationale: str

def recommend_probes(claims: List[Dict[str, Any]], contradictions: List[Dict[str, Any]], topo: Dict[str, Any]) -> List[Recommendation]:
    """
    Deterministic rule-based probe recommendation engine.
    Ranks next best low-risk analytic or verification actions.
    """
    recs = []
    
    # 1. Address High-Severity Contradictions first
    for ct in contradictions:
        if ct.get("severity") == "HIGH":
            # If missing traces, recommend deep trace probe
            if "traces" in ct.get("description", "").lower():
                recs.append(Recommendation(
                    action_id="PROBE_DEEP_TRACE",
                    target=ct.get("service", "Global"),
                    priority=0.9,
                    rationale=f"Contradiction: {ct['description']}"
                ))
            else:
                recs.append(Recommendation(
                    action_id="C_LOOKBACK_30M",
                    target=ct.get("service", "Global"),
                    priority=0.8,
                    rationale="Expanding lookback to resolve state conflict."
                ))

    # 2. Address Weakly Verified claims with high forecast risk
    for claim in claims:
        # Pydantic or dict check
        svc = claim.get("service") if isinstance(claim, dict) else claim.service
        state = claim.get("state") if isinstance(claim, dict) else claim.state
        risk = claim.get("forecast_risk", 0.0) if isinstance(claim, dict) else claim.forecast_risk
        
        if state == "WeaklyVerified" and risk > 0.6:
            recs.append(Recommendation(
                action_id="C_NEIGHBORS_2HOP",
                target=svc,
                priority=0.7,
                rationale=f"High verifiability risk ({risk}) for weakly verified service."
            ))

    # Sort by priority desc
    recs.sort(key=lambda x: x.priority, reverse=True)
    return recs

def orchestrate_probes(contradictions: List[Dict[str, Any]], topo: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Backward compatibility wrapper for the legacy orchestrator."""
    recs = recommend_probes([], contradictions, topo)
    return [r.model_dump() for r in recs]
