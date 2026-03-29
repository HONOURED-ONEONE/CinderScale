from rca.claims import evaluate_service_claims
from rca.contradictions import detect_contradictions
from rca.tss import compute_tss

def extract_epistemic_state(events, signals, incident, topo=None):
    """
    Extracts continuous epistemic states from the environment using modular evaluators.
    """
    if topo is None:
        topo = {"nodes": [], "edges": [], "confidence": 0.0}
        
    tss_data = compute_tss(events, topo, incident)
    
    # 1. Evaluate Health Claims for all services
    claims = evaluate_service_claims(events, topo, signals, tss_data)
    
    # 2. Detect Contradictions between telemetry and claims
    contradictions = detect_contradictions(events, topo, signals, tss_data)
    
    # 3. Format for EpistemicState schema
    final_claims = []
    for c in claims:
        final_claims.append({
            "service": c.service,
            "type": c.state.value,
            "evidence": c.rationale,
            "confidence": c.confidence
        })
        
    final_contradictions = []
    for ct in contradictions:
        final_contradictions.append({
            "service": ct.scope,
            "description": ct.description,
            "severity": ct.severity.value,
            "resolved": False
        })
            
    return {
        "health_claims": final_claims,
        "contradictions": final_contradictions,
        "reliability_graph_nodes": [c.service for c in claims]
    }
