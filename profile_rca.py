import time
import random
import logging
from rca.normalize import normalize_all
from rca.topology import infer_topology
from rca.signals import extract_signals
from rca.hotspots import calculate_hotspots
from rca.contradictions import detect_contradictions
from rca.forecasting import get_forecast
from rca.persistent_graph import ReliabilityGraph, GraphNode

logging.basicConfig(level=logging.ERROR)

def generate_large_payload(n=1000):
    """Generates a large dummy payload for profiling."""
    services = [f"svc_{i}" for i in range(10)]
    logs = []
    for i in range(n):
        logs.append({
            "ts": "2024-03-29T10:00:00Z",
            "service": random.choice(services),
            "level": "INFO",
            "message": f"User login success for user_{i}. Hint: jdbc connection timeout."
        })
    
    metrics = []
    for i in range(n):
        metrics.append({
            "ts": "2024-03-29T10:00:00Z",
            "service": random.choice(services),
            "name": "cpu_usage",
            "value": random.random()
        })
        
    traces = []
    for i in range(n // 10):
        traces.append({
            "ts": "2024-03-29T10:00:00Z",
            "trace_id": f"trace_{i}",
            "spans": [{"service": random.choice(services), "parent": None}, 
                      {"service": random.choice(services), "parent": "api"}]
        })
        
    return {
        "manifest": {"run_id": "prof-1"},
        "alerts": [{"service": "svc_1", "type": "Err", "ts": "2024-03-29T10:00:00Z"}],
        "logs": logs,
        "metrics": metrics,
        "traces": traces,
        "changes": []
    }

def profile_path():
    payload = generate_large_payload(5000)
    incident = {"id": "inc-1"}
    strategy = {"mode": "TRACE_CAUSAL"}
    
    print("--- RCA Profiling (5000 records) ---")
    
    # 1. Normalization
    start = time.time()
    events = normalize_all(payload)
    norm_time = (time.time() - start) * 1000
    print(f"Normalization: {norm_time:.2f} ms")
    
    # 2. Topology Inference
    start = time.time()
    topo = infer_topology(events, incident, strategy)
    topo_time = (time.time() - start) * 1000
    print(f"Topology Inference: {topo_time:.2f} ms")
    
    # 3. Signal Extraction
    start = time.time()
    signals = extract_signals(events, incident, topo, strategy)
    signal_time = (time.time() - start) * 1000
    print(f"Signal Extraction: {signal_time:.2f} ms")
    
    # 4. Hotspot Scoring
    graph = ReliabilityGraph()
    for s in range(100):
        graph.nodes[f"svc_{s}"] = GraphNode(name=f"svc_{s}", first_seen="now", last_seen="now", implicated_count=s)
    
    start = time.time()
    calculate_hotspots(graph)
    hotspot_time = (time.time() - start) * 1000
    print(f"Hotspot Scoring: {hotspot_time:.2f} ms")

    # 5. Contradictions
    start = time.time()
    detect_contradictions(events, topo, signals, (0.8, []))
    contra_time = (time.time() - start) * 1000
    print(f"Contradiction Scoring: {contra_time:.2f} ms")

    print("\nRanked Hotspots:")
    results = [
        ("Normalization", norm_time),
        ("Topology Inference", topo_time),
        ("Signal Extraction", signal_time),
        ("Hotspot Scoring", hotspot_time),
        ("Contradiction Scoring", contra_time)
    ]
    results.sort(key=lambda x: x[1], reverse=True)
    for name, t in results:
        print(f"- {name}: {t:.2f} ms")

if __name__ == "__main__":
    profile_path()
