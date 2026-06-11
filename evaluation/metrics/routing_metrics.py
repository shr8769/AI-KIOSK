import os
import sys
import json
import pandas as pd

def calculate_metrics():
    # Resolve directories relative to this file
    metrics_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(metrics_dir, "..", ".."))
    
    datasets_dir = os.path.join(project_root, "evaluation", "datasets")
    results_dir = os.path.join(project_root, "evaluation", "results")
    
    seed_queries_path = os.path.join(datasets_dir, "seed_queries.json")
    results_csv_path = os.path.join(results_dir, "benchmark_results.csv")
    report_txt_path = os.path.join(results_dir, "routing_report.txt")
    
    # 1. Read seed_queries.json using pandas
    if not os.path.exists(seed_queries_path):
        print(f"Error: {seed_queries_path} not found.")
        sys.exit(1)
    df_expected = pd.read_json(seed_queries_path)
    
    # 2. Read benchmark_results.csv using pandas
    if not os.path.exists(results_csv_path):
        print(f"Error: {results_csv_path} not found.")
        sys.exit(1)
    df_results = pd.read_csv(results_csv_path)
    
    # Standardize column casing/names for query matching
    df_expected['query_clean'] = df_expected['query'].str.strip().str.lower()
    df_results['query_clean'] = df_results['Query'].str.strip().str.lower()
    
    # Merge the dataframes on the cleaned query column
    df = pd.merge(df_results, df_expected, on='query_clean', how='inner')
    
    # Define agent to domain mapping
    agent_to_domain = {
        "AdmissionsAgent": "admissions",
        "AcademicsAgent": "academics",
        "PlacementsAgent": "placements",
        "ResearchAgent": "research",
        "StudentServicesAgent": "student_services",
        "NavigationAgent": "navigation",
        "None": "None"
    }
    
    # Map selected_agent to predicted domain
    df['predicted_domain'] = df['Selected Agent'].map(agent_to_domain).fillna('None')
    
    # Calculate correctness
    df['is_correct'] = df['predicted_domain'] == df['domain']
    
    # Calculate metrics
    total_queries = len(df)
    correct_routes = df['is_correct'].sum()
    incorrect_routes = total_queries - correct_routes
    routing_accuracy = (correct_routes / total_queries * 100) if total_queries > 0 else 0.0
    
    # Formulate report string matching the specified format
    report = []
    report.append("================================")
    report.append("ROUTING EVALUATION REPORT")
    report.append("================================")
    report.append("")
    report.append(f"Total Queries: {total_queries}")
    report.append(f"Correct Routes: {correct_routes}")
    report.append(f"Incorrect Routes: {incorrect_routes}")
    report.append(f"Routing Accuracy: {routing_accuracy:.2f}%")
    report.append("")
    report.append("================================")
    
    report_text = "\n".join(report)
    
    # Print the report
    print(report_text)
    
    # Ensure results directory exists and write report to file
    os.makedirs(results_dir, exist_ok=True)
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print(f"\nReport saved to: {report_txt_path}")

if __name__ == "__main__":
    calculate_metrics()
