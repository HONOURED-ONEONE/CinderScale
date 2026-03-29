import json
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class GraphNode(BaseModel):
    name: str
    first_seen: str
    last_seen: str
    observation_count: int = 1
    implicated_count: int = 0
    low_confidence_count: int = 0
    anomaly_associated_count: int = 0

class GraphEdge(BaseModel):
    source: str
    target: str
    confidence_history: List[float] = []
    observation_count: int = 1

class ReliabilityGraph(BaseModel):
    nodes: Dict[str, GraphNode] = {}
    edges: Dict[str, GraphEdge] = {}

class GraphManager:
    def __init__(self, storage_path: str = "reliability_graph.json"):
        self.storage_path = storage_path
        self.graph = self._load()

    def _load(self) -> ReliabilityGraph:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return ReliabilityGraph.model_validate_json(f.read())
        return ReliabilityGraph()

    def save(self):
        with open(self.storage_path, "w") as f:
            f.write(self.graph.model_dump_json(indent=2))

    def update_graph(self, current_topo: Dict[str, Any], timestamp: str):
        # Update Nodes
        for node_name in current_topo.get("nodes", []):
            if node_name not in self.graph.nodes:
                self.graph.nodes[node_name] = GraphNode(
                    name=node_name,
                    first_seen=timestamp,
                    last_seen=timestamp
                )
            else:
                node = self.graph.nodes[node_name]
                node.last_seen = timestamp
                node.observation_count += 1
                
                # Check for low confidence in the pass
                if current_topo.get("confidence", 1.0) < 0.6:
                    node.low_confidence_count += 1

        # Update Edges
        for edge in current_topo.get("edges", []):
            src, tgt = edge.get("src"), edge.get("dst")
            if not src or not tgt: continue
            edge_key = f"{src}->{tgt}"
            conf = edge.get("conf", 0.0)
            
            if edge_key not in self.graph.edges:
                self.graph.edges[edge_key] = GraphEdge(
                    source=src,
                    target=tgt,
                    confidence_history=[conf]
                )
            else:
                g_edge = self.graph.edges[edge_key]
                g_edge.observation_count += 1
                g_edge.confidence_history.append(conf)

    def associate_anomalies(self, contradictions: List[Dict[str, Any]]):
        for contradiction in contradictions:
            svc = contradiction.get("scope")
            if svc in self.graph.nodes:
                self.graph.nodes[svc].anomaly_associated_count += 1
    
    def associate_implication(self, top3_hypotheses: List[Dict[str, Any]]):
        for h in top3_hypotheses:
            # Assume hypothesis name might contain service name
            for node_name in self.graph.nodes:
                if node_name.lower() in h.get("name", "").lower():
                    self.graph.nodes[node_name].implicated_count += 1
