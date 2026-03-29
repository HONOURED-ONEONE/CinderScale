import math
from typing import List, Dict, Any
from pydantic import BaseModel
from rca.persistent_graph import GraphNode, ReliabilityGraph

class HotspotResult(BaseModel):
    name: str
    score: float
    hotspot_class: str
    rationale: str

def calculate_hotspots(graph: ReliabilityGraph) -> List[HotspotResult]:
    """
    Scores nodes in the reliability graph to identify recurring fail points.
    """
    hotspots = []
    
    for name, node in graph.nodes.items():
        # Heuristic Formula
        raw_score = (node.implicated_count * 2.0) + \
                    (node.anomaly_associated_count * 1.5) + \
                    (node.low_confidence_count * 0.5)
        
        # Normalize by observations to avoid favoring old nodes too much
        norm_factor = math.log(node.observation_count + 1)
        score = raw_score / norm_factor if norm_factor > 0 else 0
        
        hotspot_class = "Normal"
        if score > 10.0:
            hotspot_class = "Critical Hotspot"
        elif score > 5.0:
            hotspot_class = "Frequent Failure Node"
        elif score > 2.0:
            hotspot_class = "Developing Hotspot"
            
        rationale = f"Implicated {node.implicated_count} times, {node.anomaly_associated_count} anomaly associations."
        
        hotspots.append(HotspotResult(
            name=name,
            score=round(score, 2),
            hotspot_class=hotspot_class,
            rationale=rationale
        ))
        
    # Sort by score descending
    hotspots.sort(key=lambda x: x.score, reverse=True)
    return hotspots

def print_top_hotspots(graph: ReliabilityGraph, limit: int = 5):
    hotspots = calculate_hotspots(graph)
    print(f"\n--- Top {limit} Reliability Hotspots ---")
    for h in hotspots[:limit]:
        print(f"[{h.hotspot_class}] {h.name}: Score {h.score}")
        print(f"  Rationale: {h.rationale}\n")
