import os
import sys
import re
from typing import Dict, Any, Tuple

# Ensure parent directory is in search path if run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    import chromadb
except ImportError:
    pass

# Import all domain agents
from agents.domain.admissions_agent import AdmissionsAgent
from agents.domain.academics_agent import AcademicsAgent
from agents.domain.placements_agent import PlacementsAgent
from agents.domain.research_agent import ResearchAgent
from agents.domain.student_services_agent import StudentServicesAgent
from agents.navigation.navigation_agent import NavigationAgent

class CoordinatorAgent:
    """
    Coordinator agent that routes user queries to the appropriate domain-specific 
    agent based on confidence scores calculated from keyword mappings.
    Uses weighted scoring where multi-word phrases receive higher priority.
    """
    def __init__(self, db_path: str = None):
        """
        Initializes the CoordinatorAgent and all downstream domain agents.
        
        Args:
            db_path (str, optional): Path to persistent ChromaDB storage.
        """
        if db_path is None:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "vectorstore"))
            
        # Initialize a single shared client instance for resource optimization
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Instantiate sub-agents with the shared client
        self.agents = {
            "admissions": AdmissionsAgent(client=self.client),
            "academics": AcademicsAgent(client=self.client),
            "placements": PlacementsAgent(client=self.client),
            "research": ResearchAgent(client=self.client),
            "student_services": StudentServicesAgent(client=self.client),
            "navigation": NavigationAgent(client=self.client)
        }

        # Define keyword routing mappings for each domain agent.
        self.routing_rules = {
            "admissions": ["gpa", "transcript", "ielts", "toefl", "duolingo", "recommendation", "recommendation letter", "international student", "predicted grades", "educational gap", "tuition", "fee", "admission", "scholarship", "eligibility", "deadline", "application", "predicted grade"],
            "academics": ["attendance", "exam", "revaluation", "sgpa", "cgpa calculation", "transcript", "grading", "credits", "grade", "timetable", "course", "section", "lecture"],
            "placements": ["microsoft", "amazon", "internship", "placement", "recruitment", "oa", "online assessment", "coding test", "backlog eligibility", "dream offer", "cgpa", "interview", "resume", "ppo", "salary", "job"],
            "research": ["publication", "journal", "conference", "research grant", "travel grant", "faculty project", "urop", "research lab", "hpc", "gpu cluster", "research", "lab", "symposium", "thesis", "funding", "stipend"],
            "student_services": ["hostel", "library", "id card", "counseling", "maintenance", "certificate", "visitor", "curfew", "book borrowing", "bonafide", "health center"],
            "navigation": ["where", "location", "directions", "located", "reach", "how do I get to", "building", "office", "floor", "where is", "auditorium", "landmark", "facility", "gate", "block"]
        }

    def route(self, query: str) -> Tuple[str, float, str, list]:
        """
        Routes the query to the correct domain based on keyword matching confidence.
        Uses regex word boundaries (\b) to avoid incorrect matches on substrings.
        Multi-word phrases are weighted higher than single keywords.
        
        Args:
            query (str): The user search query.
            
        Returns:
            Tuple[str, float, str, list]: (selected_domain, confidence_score, routing_reason, matched_keywords)
        """
        query_lower = query.lower()
        scores = {}
        matched_details = {}
        all_matches = []
        
        # Check for Navigation override keywords
        nav_override_keywords = ["where", "located", "directions", "reach", "get to", "location"]
        has_nav_override = False
        for kw in nav_override_keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, query_lower):
                has_nav_override = True
                break
        
        for domain, keywords in self.routing_rules.items():
            matches = []
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, query_lower):
                    matches.append(keyword)
                    all_matches.append(keyword)
            
            # Confidence score is calculated with weighted matches:
            # Phrase matches containing spaces get a weight of 2.0 (more specific).
            # Single keyword matches get a weight of 1.0.
            score = sum(2.0 if " " in kw else 1.0 for kw in matches)
            scores[domain] = score
            matched_details[domain] = matches
            
        # Apply Navigation priority boost
        if has_nav_override:
            scores["navigation"] = scores.get("navigation", 0.0) + 100.0
            # Ensure matched navigation override keywords are recorded
            for kw in nav_override_keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, query_lower):
                    if kw not in matched_details["navigation"]:
                        matched_details["navigation"].append(kw)
                    if kw not in all_matches:
                        all_matches.append(kw)

        # Deduplicate all matches across all domains
        all_matches = list(dict.fromkeys(all_matches))
            
        # Find the domain with the highest score
        best_domain = max(scores, key=scores.get)
        best_score = scores[best_domain]
        
        if best_score > 0:
            matched_words = ", ".join(f"'{w}'" for w in matched_details[best_domain])
            reason = f"Matched keyword(s) {matched_words} in domain '{best_domain}'"
            
            # Compute confidence score
            total_score = sum(scores.values())
            other_score = total_score - best_score
            confidence = best_score / (best_score + 0.176 * other_score)
            
            return best_domain, confidence, reason, all_matches
        else:
            reason = "No matching keywords found across any domain"
            return None, 0.0, reason, []

    def answer(self, query: str) -> str:
        """
        Routes the query, prints the selection and routing reason, and retrieves the answer.
        If no strong match exists (confidence score is 0), returns "No suitable agent found".
        
        Args:
            query (str): The user search query.
            
        Returns:
            str: The final answer or fallback response.
        """
        selected_domain, confidence, reason, all_matches = self.route(query)
        
        # Check if a strong match exists
        if selected_domain is None or confidence <= 0.0:
            fallback_msg = (
                "I'm sorry, I couldn't identify the right department for your query.\n"
                "Please try asking about one of the following topics:\n"
                "- Admissions (requirements, application, fees, scholarships)\n"
                "- Academics (attendance, exams, SGPA/CGPA, transcripts)\n"
                "- Placements (internships, company eligibility, recruitment process)\n"
                "- Research (labs, publications, faculty projects, UROP)\n"
                "- Student Services (hostel, library, ID cards, certificate requests)\n"
                "- Navigation (campus directions, building/office locations)"
            )
            print("=" * 52)
            print("USER QUERY")
            print("==========")
            print()
            print(query)
            print()
            print("=" * 52)
            print("ROUTING DECISION")
            print("================")
            print()
            print("Matched Keywords:")
            print("None")
            print()
            print("Selected Agent:")
            print("None")
            print()
            print("Domain Selected:")
            print("None")
            print()
            print("Confidence:")
            print("0.00")
            print()
            print("=" * 52)
            print("ANSWER")
            print("======")
            print()
            print(fallback_msg)
            print()
            print("=" * 52)
            print("SOURCE")
            print("======")
            print()
            print("None")
            print()
            print("=" * 52)
            
            # Log trace for unmatched query
            from agents.domain.base_agent import log_evaluation_trace
            log_evaluation_trace(
                query=query,
                selected_agent="None",
                selected_domain="None",
                routing_confidence=0.0,
                selected_doc_id="None",
                retrieved_docs=[],
                answer=fallback_msg
            )
            return fallback_msg
            
        agent = self.agents[selected_domain]
        selected_agent_name = agent.__class__.__name__
        matched_keywords_str = ", ".join(all_matches) if all_matches else "None"
        
        # Print USER QUERY and ROUTING DECISION
        print("=" * 52)
        print("USER QUERY")
        print("==========")
        print()
        print(query)
        print()
        print("=" * 52)
        print("ROUTING DECISION")
        print("================")
        print()
        print("Matched Keywords:")
        print(matched_keywords_str)
        print()
        print("Selected Agent:")
        print(selected_agent_name)
        print()
        print("Domain Selected:")
        print(selected_domain)
        print()
        print("Confidence:")
        print(f"{confidence:.2f}")
        print()
        print("=" * 52)
        
        # Perform retrieval and printing of candidate documents
        raw_ans = agent.answer(query, routing_confidence=confidence)
        
        # Parse returned answer to separate answer and source
        if "\n\n[Source: " in raw_ans:
            answer_part, source_part = raw_ans.split("\n\n[Source: ", 1)
            source_part = source_part.rstrip("]")
        else:
            answer_part = raw_ans
            source_part = f"{selected_domain.title().replace('_', ' ')}"
            
        # Print ANSWER and SOURCE sections
        print("ANSWER")
        print("======")
        print()
        print(answer_part)
        print()
        print("=" * 52)
        print("SOURCE")
        print("======")
        print()
        print(source_part)
        print()
        print("=" * 52)
        
        return raw_ans

if __name__ == "__main__":
    print("====================================")
    print("CAMPUS AI BRAIN")
    print("====================================")
    print("Type 'exit' to quit.")
    
    coordinator = CoordinatorAgent()
    
    while True:
        try:
            query = input("\nEnter your query:\n").strip()
            if query.lower() == "exit":
                print("\nGoodbye!")
                break
            if not query:
                continue
                
            selected_domain, confidence, reason, _ = coordinator.route(query)
            
            selected_agent = "None"
            if selected_domain:
                agent = coordinator.agents.get(selected_domain)
                if agent:
                    selected_agent = agent.__class__.__name__
            
            # Get response
            raw_ans = coordinator.answer(query)
            
            # Extract clean answer text
            if "\n\n[Source: " in raw_ans:
                ans_text, _ = raw_ans.split("\n\n[Source: ", 1)
            else:
                ans_text = raw_ans
                
            print("\nSelected Agent:")
            print(selected_agent)
            print("\nRouting Reason:")
            print(reason)
            print("\nAnswer:")
            print(ans_text)
            print("=" * 52)
            
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
