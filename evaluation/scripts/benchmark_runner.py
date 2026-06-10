import os
import sys
import json
import csv

# Add the project root directory to sys.path so we can import agents
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from agents.coordinator.coordinator_agent import CoordinatorAgent

def run_benchmark():
    # Resolve paths
    datasets_dir = os.path.join(project_root, "evaluation", "datasets")
    results_dir = os.path.join(project_root, "evaluation", "results")
    
    seed_queries_path = os.path.join(datasets_dir, "seed_queries.json")
    results_csv_path = os.path.join(results_dir, "benchmark_results.csv")
    
    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    if not os.path.exists(seed_queries_path):
        print(f"Error: {seed_queries_path} not found.")
        sys.exit(1)
        
    # Load queries
    with open(seed_queries_path, "r", encoding="utf-8") as f:
        queries_data = json.load(f)
        
    print(f"Loaded {len(queries_data)} queries from {seed_queries_path}.")
    
    # Initialize coordinator
    coordinator = CoordinatorAgent()
    
    # Prepare results list
    results = []
    
    for idx, item in enumerate(queries_data, 1):
        query = item.get("query", "")
        if not query:
            continue
            
        print(f"\n[{idx}/{len(queries_data)}] Running query: '{query}'")
        
        # Route query to get the selected domain and agent
        selected_domain, confidence, reason, _ = coordinator.route(query)
        
        selected_agent = "None"
        if selected_domain:
            agent = coordinator.agents.get(selected_domain)
            if agent:
                selected_agent = agent.__class__.__name__
        
        # Get the actual answer using coordinator
        answer = coordinator.answer(query)
        
        results.append({
            "Query": query,
            "Selected Agent": selected_agent,
            "Answer": answer
        })
        
    # Save as CSV
    with open(results_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Query", "Selected Agent", "Answer"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\nBenchmark completed successfully! Results saved to {results_csv_path}.")

if __name__ == "__main__":
    run_benchmark()
