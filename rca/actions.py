from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ActionCategory(str, Enum):
    ANALYTIC_PROBE = "AnalyticProbe"      # Changes how we analyze telemetry
    VERIFICATION_PROBE = "VerificationProbe" # Active check or experiment
    ESCALATION = "Escalation"            # Human or system-level alert

class ActionProbe(BaseModel):
    id: str
    category: ActionCategory
    description: str
    params: Dict[str, Any] = {}
    risk_level: str = "LOW"

# Taxonomy Mapping (Existing AOGC Actions -> New Probes)
TAXONOMY = {
    "C_LOOKBACK_30M": ActionProbe(
        id="C_LOOKBACK_30M",
        category=ActionCategory.ANALYTIC_PROBE,
        description="Expand analysis window to 30 minutes.",
        params={"lookback_minutes": 30}
    ),
    "C_NEIGHBORS_2HOP": ActionProbe(
        id="C_NEIGHBORS_2HOP",
        category=ActionCategory.ANALYTIC_PROBE,
        description="Expand topology search to 2-hop neighbors.",
        params={"neighbor_hops": 2}
    ),
    "B_LOGSIG_30M_1HOP_ADD_OVERLOAD": ActionProbe(
        id="B_LOGSIG_30M_1HOP_ADD_OVERLOAD",
        category=ActionCategory.ANALYTIC_PROBE,
        description="Log-heavy analysis with overload fallbacks.",
        params={"mode": "LOG_SIGNATURE_ONLY", "lookback_minutes": 30, "add_overload_fallbacks": True}
    ),
    "PROBE_DEEP_TRACE": ActionProbe(
        id="PROBE_DEEP_TRACE",
        category=ActionCategory.VERIFICATION_PROBE,
        description="Request deeper sampling for specific trace IDs.",
        params={"sampling_rate": 1.0},
        risk_level="LOW"
    ),
    "ESCALATE_SRE": ActionProbe(
        id="ESCALATE_SRE",
        category=ActionCategory.ESCALATION,
        description="Escalate unverified contradiction to SRE.",
        params={"channel": "pagerduty"}
    )
}

def apply_action_to_strategy(base_strategy: dict, action_id: str) -> dict:
    """Refactored strategy mutation using the new taxonomy."""
    s = dict(base_strategy)
    
    # Handle legacy mapping or direct lookup
    probe = TAXONOMY.get(action_id)
    if not probe:
        # Fallback to legacy string-based logic if not in taxonomy
        return _legacy_apply(s, action_id)

    if probe.category == ActionCategory.ANALYTIC_PROBE:
        s.update(probe.params)
    
    return s

def _legacy_apply(s: dict, action: str) -> dict:
    # Preserve legacy logic for backward compatibility
    if action == "A_TRACE_CAUSAL":
        s["mode"] = "TRACE_CAUSAL"
    elif action == "A_LOG_METRIC_CORR":
        s["mode"] = "LOG_METRIC_CORRELATION"
    elif action == "C_LOOKBACK_30M":
        s["lookback_minutes"] = 30
    return s

def get_action_details(action_id: str) -> Optional[ActionProbe]:
    return TAXONOMY.get(action_id)
