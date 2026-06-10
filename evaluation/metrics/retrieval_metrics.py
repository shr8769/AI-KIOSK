import os
import json
import csv
import sys

def generate_report():
    # Define directories relative to this file
    metrics_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(metrics_dir, "..", ".."))
    
    datasets_dir = os.path.join(project_root, "evaluation", "datasets")
    results_dir = os.path.join(project_root, "evaluation", "results")
    
    seed_queries_path = os.path.join(datasets_dir, "seed_queries.json")
    results_csv_path = os.path.join(results_dir, "benchmark_results.csv")
    report_txt_path = os.path.join(results_dir, "retrieval_metrics_report.txt")
    
    if not os.path.exists(seed_queries_path):
        print(f"Error: Seed queries file not found at {seed_queries_path}")
        sys.exit(1)
        
    if not os.path.exists(results_csv_path):
        print(f"Error: Benchmark results CSV file not found at {results_csv_path}")
        sys.exit(1)
        
    # Load seed queries (ground truth)
    with open(seed_queries_path, "r", encoding="utf-8") as f:
        seed_data = json.load(f)
        
    # Create lookup for ground truth: query -> domain
    ground_truth = {}
    for item in seed_data:
        q = item.get("query", "").strip()
        d = item.get("domain", "").strip()
        if q:
            ground_truth[q] = d
            
    # Read benchmark results CSV
    results = []
    with open(results_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
            
    # Mapping from Agent name to domain key
    agent_to_domain = {
        "AdmissionsAgent": "admissions",
        "AcademicsAgent": "academics",
        "PlacementsAgent": "placements",
        "ResearchAgent": "research",
        "StudentServicesAgent": "student_services",
        "NavigationAgent": "navigation",
        "None": "None"
    }
    
    total_queries = len(results)
    correct_routing_count = 0
    incorrect_routing_count = 0
    
    incorrect_details = []
    
    for row in results:
        query = row.get("Query", "").strip()
        selected_agent = row.get("Selected Agent", "").strip()
        
        # Get predicted domain
        predicted_domain = agent_to_domain.get(selected_agent, "unknown")
        
        # Get ground truth domain
        gt_domain = ground_truth.get(query, None)
        
        if gt_domain is None:
            # Try fuzzy matching in case whitespace differs
            for q_gt, d_gt in ground_truth.items():
                if query.lower() == q_gt.lower():
                    gt_domain = d_gt
                    break
        
        if gt_domain is None:
            # If still not found, treat it as unknown ground truth
            gt_domain = "unknown"
            
        if predicted_domain == gt_domain:
            correct_routing_count += 1
        else:
            incorrect_routing_count += 1
            incorrect_details.append({
                "query": query,
                "ground_truth": gt_domain,
                "predicted": predicted_domain,
                "selected_agent": selected_agent
            })
            
    # Compute accuracy
    accuracy = (correct_routing_count / total_queries * 100) if total_queries > 0 else 0.0
    
    # Generate the report text
    report = []
    report.append("=" * 60)
    report.append("                RETRIEVAL ROUTING METRICS REPORT")
    report.append("=" * 60)
    report.append(f"Total Queries Evaluated:    {total_queries}")
    report.append(f"Correct Domain Routings:    {correct_routing_count}")
    report.append(f"Incorrect Domain Routings:  {incorrect_routing_count}")
    report.append(f"Agent Routing Accuracy:     {accuracy:.2f}%")
    report.append("=" * 60)
    
    if incorrect_details:
        report.append("\nINCORRECT ROUTING DETAILS:")
        report.append("-" * 60)
        for idx, item in enumerate(incorrect_details, 1):
            report.append(f"{idx}. Query: '{item['query']}'")
            report.append(f"   Ground Truth Domain: {item['ground_truth']}")
            report.append(f"   Selected Agent:      {item['selected_agent']} (Mapped: {item['predicted']})")
            report.append("-" * 60)
            
    report_text = "\n".join(report)
    
    # Print to console
    print(report_text)
    
    # Write report file
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print(f"\nReport successfully generated and saved to {report_txt_path}")

if __name__ == "__main__":
    generate_report()
