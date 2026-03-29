from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Manifest(BaseModel):
    run_id: str
    scenario: Optional[str] = None
    variant: Optional[str] = None
    telemetry_gaps: Optional[List[str]] = None

class RunData(BaseModel):
    """Input payload representing a raw or normalized telemetry run."""
    manifest: Manifest
    alerts: List[Dict[str, Any]] = []
    logs: List[Dict[str, Any]] = []
    metrics: List[Dict[str, Any]] = []
    traces: List[Dict[str, Any]] = []
    changes: List[Dict[str, Any]] = []
    truth: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None

class Hypothesis(BaseModel):
    name: str
    confidence: float
    actions: Optional[List[str]] = []
    
    model_config = {"extra": "allow"}

class TopologySummary(BaseModel):
    confidence: float
    edge_count: int
    avg_edge_conf: float

class Inventory(BaseModel):
    evidence_diversity: float
    # Allows adding dynamically inferred services or assets
    model_config = {"extra": "allow"}

class MEPP(BaseModel):
    """Minimal Evidence Proof Pack"""
    hypothesis: str
    confidence: float
    minimal_evidence: Dict[str, Any]
    recommended_action: Optional[str] = None

class HealthClaim(BaseModel):
    """Future extensibility: Explicit assertion of health."""
    service: str
    type: str
    evidence: str
    confidence: float

class Contradiction(BaseModel):
    """Future extensibility: Conflict between a health claim and an anomaly."""
    service: str
    description: str
    severity: str
    resolved: bool

class EpistemicState(BaseModel):
    """Continuous epistemic falsification state."""
    health_claims: List[HealthClaim] = []
    contradictions: List[Contradiction] = []
    reliability_graph_nodes: List[str] = []

class PipelineResult(BaseModel):
    """The result of a single pipeline run."""
    run_id: str
    incident_id: str
    mode: str
    top3: List[Hypothesis]
    tss: float
    missing: List[str]
    inventory: Inventory
    topology_summary: TopologySummary
    architecture_flags: Dict[str, bool]
    mepp: List[MEPP]
    epistemic_state: Optional[EpistemicState] = None
    debug: Optional[Dict[str, Any]] = None

class RCABundle(BaseModel):
    """The full evaluation bundle (Baseline + Optional Rerun = Final)."""
    baseline: PipelineResult
    rerun: Optional[PipelineResult] = None
    final: PipelineResult
    action: Optional[str] = None
    kept: str
    deltas: Dict[str, Any] = {}
    
    # CEF Extensions
    forecasting: Optional[Dict[str, Any]] = None
    probes: Optional[List[Dict[str, Any]]] = []
