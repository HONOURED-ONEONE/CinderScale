from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RCAKernels(ABC):
    """
    Abstract interface for CPU-bound RCA kernels.
    Accelerated implementations (Mojo, C++, etc.) must follow this interface.
    """
    
    @abstractmethod
    def normalize_telemetry(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes raw logs, metrics, traces, and alerts."""
        pass

    @abstractmethod
    def infer_topology(self, events: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Derives dependency graph from telemetry."""
        pass

    @abstractmethod
    def score_signals(self, events: Dict[str, Any], topo: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts and scores anomalies from telemetry."""
        pass
