#!/usr/bin/env python3
"""
query.py

A utility script to query the persistent ChromaDB vector store.
Features:
1. Connects to ChromaDB PersistentClient.
2. Lists available collections and prompts selection (or takes it via arguments).
3. Accepts a user query.
4. Performs a semantic search using the same embedding function (all-MiniLM-L6-v2).
5. Returns and displays the top 3 matching documents along with distances and metadata.
"""

import os
import argparse
import logging
import sys
from typing import Any, List, Dict

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Error: chromadb is not installed. Please install it using 'pip install chromadb'")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Note: Since this file is in knowledge/embeddings/, the relative path to vectorstore is ../vectorstore
DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vectorstore"))
VALID_COLLECTIONS = ["admissions", "academics", "placements", "research", "student_services", "navigation"]

def print_banner():
    print("=" * 80)
    print("                     UNIVERSITY AI ASSISTANT - QUERY PORTAL")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Query the university AI assistant's ChromaDB vector store.")
    parser.add_argument(
        "--db-path",
        type=str,
        default=DEFAULT_DB_PATH,
        help=f"Path to persistent ChromaDB storage (default: {DEFAULT_DB_PATH})"
    )
    parser.add_argument(
        "--collection",
        type=str,
        choices=VALID_COLLECTIONS,
        help="The collection to query. If not specified, you will be prompted."
    )
    parser.add_argument(
        "--query",
        type=str,
        help="The query text. If not specified, you will be prompted."
    )
    parser.add_argument(
        "--n-results",
        type=int,
        default=3,
        help="Number of results to return (default: 3)"
    )
    args = parser.parse_args()

    print_banner()

    # 1. Connect to PersistentClient
    if not os.path.exists(args.db_path):
        print(f"Error: Vector store not found at '{args.db_path}'.")
        print("Please run the ingestion script first to build the database.")
        sys.exit(1)

    try:
        client = chromadb.PersistentClient(path=args.db_path)
    except Exception as e:
        print(f"Failed to connect to ChromaDB PersistentClient: {e}")
        sys.exit(1)

    # 2. Select a Collection
    collection_name = args.collection
    if not collection_name:
        print("\nAvailable collections:")
        for idx, col in enumerate(VALID_COLLECTIONS, 1):
            print(f"  {idx}. {col}")
        
        while True:
            try:
                choice = input("\nSelect a collection number (or enter name): ").strip()
                if choice.isdigit():
                    num = int(choice)
                    if 1 <= num <= len(VALID_COLLECTIONS):
                        collection_name = VALID_COLLECTIONS[num - 1]
                        break
                elif choice in VALID_COLLECTIONS:
                    collection_name = choice
                    break
                print(f"Invalid selection. Please enter a number from 1 to {len(VALID_COLLECTIONS)} or a valid name.")
            except (KeyboardInterrupt, EOFError):
                print("\nOperation cancelled.")
                sys.exit(0)

    # Load local SentenceTransformer embedding function (same model used during ingestion)
    try:
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformer function: {e}. Using default embeddings.")
        emb_fn = None

    try:
        collection = client.get_collection(name=collection_name, embedding_function=emb_fn)
    except Exception as e:
        print(f"Error loading collection '{collection_name}': {e}")
        print("Please ensure the data has been ingested successfully.")
        sys.exit(1)

    # 3. Accept User Query
    query_text = args.query
    if not query_text:
        try:
            query_text = input(f"\nEnter search query for '{collection_name}': ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)
            
    if not query_text:
        print("Error: Query cannot be empty.")
        sys.exit(1)

    # 4. Perform Search and Return Results
    print(f"\nSearching '{collection_name}' for: '{query_text}'...")
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=args.n_results
        )
    except Exception as e:
        print(f"Error querying collection: {e}")
        sys.exit(1)

    # Check if results are empty
    if not results or not results['documents'] or not results['documents'][0]:
        print("\nNo matching documents found.")
        sys.exit(0)

    documents = results['documents'][0]
    distances = results['distances'][0] if 'distances' in results and results['distances'] else [None] * len(documents)
    metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(documents)
    ids = results['ids'][0] if 'ids' in results and results['ids'] else [None] * len(documents)

    print("\n" + "-"*80)
    print(f"Found {len(documents)} matching documents (sorted by relevance):")
    print("-"*80)

    for i, (doc, dist, meta, doc_id) in enumerate(zip(documents, distances, metadatas, ids), 1):
        print(f"\n[Result #{i}]")
        print(f"  ID       : {doc_id}")
        if dist is not None:
            print(f"  Distance : {dist:.4f} (lower is closer)")
        
        # Display metadata neatly
        if meta:
            meta_str = ", ".join(f"{k}: {v}" for k, v in meta.items())
            print(f"  Metadata : {meta_str}")
            
        print("  Content  :")
        # Indent document text for readable output
        indented_doc = "\n".join("      " + line for line in doc.split("\n"))
        print(indented_doc)
        print("-" * 80)

if __name__ == "__main__":
    main()
