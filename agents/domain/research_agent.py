import os
import sys
from typing import List, Dict, Any

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    pass

from agents.domain.base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Agent handling research-related queries using ChromaDB.
    """
    def __init__(self, client: Any = None, db_path: str = None):
        """
        Initializes the ResearchAgent.
        
        Args:
            client (chromadb.PersistentClient, optional): An existing persistent client.
            db_path (str, optional): Path to persistent ChromaDB storage.
        """
        super().__init__(collection_name="research", client=client, db_path=db_path)

    def get_domain(self) -> str:
        """
        Returns the domain name.
        """
        return self.collection_name

if __name__ == "__main__":
    print("====================================")
    print("Research Agent Ready")
    print("Type 'exit' to quit")
    print("====================================")
    
    agent = ResearchAgent()
    
    while True:
        try:
            query = input("\nEnter your query:\n").strip()
            if query.lower() == "exit":
                print("\nGoodbye!")
                break
            if not query:
                continue
                
            response = agent.answer(query)
            print(f"\nAnswer:\n{response}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
