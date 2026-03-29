from typing import Dict, Any
from rca.kernels.base import RCAKernels
from rca.normalize import normalize_all
from rca.topology import infer_topology
from rca.signals import extract_signals

class PythonRCAKernels(RCAKernels):
    """
    Pure-Python implementation of RCA kernels.
    Current baseline using existing codebase.
    """
    
    def normalize_telemetry(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return normalize_all(raw_data)

    def infer_topology(self, events: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        # incident ID not always needed for kernel logic if events are already filtered
        return infer_topology(events, {}, strategy)

    def score_signals(self, events: Dict[str, Any], topo: Dict[str, Any]) -> Dict[str, Any]:
        return extract_signals(events, {}, topo, {"mode": "TRACE_CAUSAL"})
