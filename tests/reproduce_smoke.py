import json
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

from rca.loader import load_run
from rca.orchestrator import run_with_aogc
from rca.persistent_graph import GraphManager
from rca.history import HistoryStore

def run_smoke_test():
    shared_folder = "shared_demo_root/current"
    graph_path = "reliability_graph.json"
    history_path = "rca_history.jsonl"
    
    # Reset files if they exist to ensure fresh proof
    if os.path.exists(graph_path):
        os.remove(graph_path)
    if os.path.exists(history_path):
        os.remove(history_path)
        
    print(f"--- Phase 1: Loading run from {shared_folder} ---")
    run_data = load_run(shared_folder)
    if not run_data:
        print("FAILED: Could not load run data from shared folder.")
        sys.exit(1)
    
    run_id = run_data["manifest"]["run_id"]
    if len(run_data.get("logs", [])) == 0:
        print("FAILED: Logs are empty. Check manifest 'streams' mapping.")
        sys.exit(1)
    print(f"SUCCESS: Loaded run {run_id} with {len(run_data['logs'])} logs.")

    print("\n--- Phase 2: Executing RCA Orchestrator (AOGC + CEF) ---")
    bundle = run_with_aogc(run_data, model_path=None)
    
    print(f"SUCCESS: Analysis complete. Kept: {bundle['kept']}")
    print(f"TSS: {bundle['final']['tss']:.3f}")
    
    # Record history manually (as api.py would do)
    hs = HistoryStore(storage_path=history_path)
    hs.record_pass(run_id, bundle["final"], bundle["final"].get("epistemic_state"))

    # Verify CEF fields
    print("\n--- Phase 3: Verifying CEF Fields ---")
    if bundle.get("forecasting"):
        print(f"SUCCESS: Forecasting: {bundle['forecasting']['risk_score']} risk")
    else:
        print("FAILED: Missing forecasting data.")
        sys.exit(1)
        
    if bundle.get("probes") is not None:
        print(f"SUCCESS: Probes: {len(bundle['probes'])} recommended")
    else:
        print("FAILED: Missing probe recommendations.")
        sys.exit(1)

    # Verify Persistent Graph
    print("\n--- Phase 4: Verifying Persistent Graph ---")
    if not os.path.exists(graph_path):
        print("FAILED: reliability_graph.json was not created.")
        sys.exit(1)
    else:
        gm = GraphManager(storage_path=graph_path)
        node_count = len(gm.graph.nodes)
        edge_count = len(gm.graph.edges)
        print(f"Graph Populated: {node_count} nodes, {edge_count} edges")
        if node_count == 0:
            print("FAILED: Graph nodes are empty.")
            sys.exit(1)
        else:
            print(f"Nodes found: {list(gm.graph.nodes.keys())}")

    # Verify History
    print("\n--- Phase 5: Verifying History Store ---")
    if not os.path.exists(history_path):
        print("FAILED: rca_history.jsonl was not created.")
        sys.exit(1)
    else:
        with open(history_path, "r") as f:
            lines = f.readlines()
            print(f"History Entries: {len(lines)}")
            if len(lines) == 0:
                print("FAILED: History file is empty.")
                sys.exit(1)

    print("\nSMOKE TEST COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    run_smoke_test()
