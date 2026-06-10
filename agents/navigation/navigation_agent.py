import os
from typing import List, Dict, Any

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    pass

from agents.domain.base_agent import BaseAgent

class NavigationAgent(BaseAgent):
    """
    Agent handling location and navigation-related queries using ChromaDB.
    """
    def __init__(self, client: Any = None, db_path: str = None):
        """
        Initializes the NavigationAgent.
        
        Args:
            client (chromadb.PersistentClient, optional): An existing persistent client.
            db_path (str, optional): Path to persistent ChromaDB storage.
        """
        super().__init__(collection_name="navigation", client=client, db_path=db_path)

    def get_domain(self) -> str:
        """
        Returns the domain name.
        """
        return self.collection_name

if __name__ == "__main__":
    print("====================================")
    print("Navigation Agent Ready")
    print("Type 'exit' to quit")
    print("====================================")
    
    agent = NavigationAgent()
    
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
