import os
import sys
import json
import csv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from agents.coordinator.coordinator_agent import CoordinatorAgent

def analyze_failures():
    datasets_dir = os.path.join(project_root, "evaluation", "datasets")
    results_dir = os.path.join(project_root, "evaluation", "results")
    
    seed_queries_path = os.path.join(datasets_dir, "seed_queries.json")
    results_csv_path = os.path.join(results_dir, "benchmark_results.csv")
    failure_report_path = os.path.join(results_dir, "failure_analysis.txt")
    
    if not os.path.exists(seed_queries_path):
        print(f"Error: {seed_queries_path} not found.")
        sys.exit(1)
        
    if not os.path.exists(results_csv_path):
        print(f"Error: {results_csv_path} not found.")
        sys.exit(1)
        
    # Load expected domains
    with open(seed_queries_path, "r", encoding="utf-8") as f:
        seed_data = json.load(f)
        
    ground_truth = {}
    for item in seed_data:
        q = item.get("query", "").strip()
        d = item.get("domain", "").strip()
        if q:
            ground_truth[q] = d
            
    # Load results
    results = []
    with open(results_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
            
    # Mapping agent to domain
    agent_to_domain = {
        "AdmissionsAgent": "admissions",
        "AcademicsAgent": "academics",
        "PlacementsAgent": "placements",
        "ResearchAgent": "research",
        "StudentServicesAgent": "student_services",
        "NavigationAgent": "navigation",
        "None": "None"
    }
    
    # Initialize coordinator to check matches
    coordinator = CoordinatorAgent()
    
    failures = []
    failures_by_domain = {}
    failure_reasons = {}
    
    for row in results:
        query = row.get("Query", "").strip()
        selected_agent = row.get("Selected Agent", "").strip()
        
        predicted = agent_to_domain.get(selected_agent, "unknown")
        gt = ground_truth.get(query, None)
        
        # Fuzzy match query if needed
        if gt is None:
            for q_gt, d_gt in ground_truth.items():
                if query.lower() == q_gt.lower():
                    gt = d_gt
                    break
        if gt is None:
            gt = "unknown"
            
        if predicted != gt:
            # Failure detected!
            # Analyze keywords matched
            _, confidence, reason, all_matches = coordinator.route(query)
            
            # Formulate failure reason category
            if not all_matches:
                fail_reason = "No keywords matched (Defaulted to None)"
            else:
                fail_reason = f"Keyword conflict / misrouting (Matched: {', '.join(all_matches)})"
                
            failure_item = {
                "query": query,
                "expected": gt,
                "predicted": predicted,
                "matched_keywords": all_matches,
                "reason": fail_reason
            }
            
            failures.append(failure_item)
            
            # Group by domain (expected)
            failures_by_domain[gt] = failures_by_domain.get(gt, 0) + 1
            
            # Count failure reasons
            failure_reasons[fail_reason] = failure_reasons.get(fail_reason, 0) + 1
            
    # Generate failure analysis report
    report = []
    report.append("============================================================")
    report.append("                   ROUTING FAILURE ANALYSIS")
    report.append("============================================================")
    report.append(f"Total Failures: {len(failures)}")
    report.append("")
    
    # 2. Group failures by domain
    report.append("FAILURES BY DOMAIN:")
    report.append("-" * 30)
    for dom, count in sorted(failures_by_domain.items(), key=lambda x: x[1], reverse=True):
        report.append(f"  * {dom}: {count} failure(s)")
    report.append("")
    
    # 4. Print top failure reasons
    report.append("TOP FAILURE REASONS:")
    report.append("-" * 30)
    for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True):
        report.append(f"  * {reason}: {count} time(s)")
    report.append("")
    
    # 1. Show all incorrect routes
    report.append("ALL INCORRECT ROUTES:")
    report.append("=" * 60)
    for idx, item in enumerate(failures, 1):
        report.append(f"{idx}. Query: '{item['query']}'")
        report.append(f"   Expected Domain: {item['expected']}")
        report.append(f"   Predicted Domain: {item['predicted']}")
        report.append(f"   Failure Analysis: {item['reason']}")
        report.append("-" * 60)
        
    report_text = "\n".join(report)
    
    # Print the report
    print(report_text)
    
    # Save to file
    os.makedirs(results_dir, exist_ok=True)
    with open(failure_report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print(f"\nFailure analysis report saved to: {failure_report_path}")

if __name__ == "__main__":
    analyze_failures()
