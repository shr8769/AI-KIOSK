#!/usr/bin/env python3
"""
ingest.py

A production-ready Python script to ingest university knowledge base JSON files 
into a persistent ChromaDB vector store.

Features:
1. Creates a PersistentClient at a configurable path.
2. Creates/gets six target collections: admissions, academics, placements, research, student_services, navigation.
3. Reads JSON files under knowledge/sources/.
4. Formats and stores question + answer as documents.
5. Uses deterministic, unique IDs to support idempotent updates (upserts).
6. Displays progress bars via tqdm and logs events.
7. Prints a detailed ingestion summary at the end.
"""

import os
import json
import logging
import time
import argparse
import hashlib
from typing import Dict, List, Any, Tuple

try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Error: chromadb is not installed. Please install it using 'pip install chromadb'")
    import sys
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not installed
    def tqdm(iterable, *args, **kwargs):
        return iterable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ingestion.log", mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DB_PATH = os.path.join("knowledge", "vectorstore")
DEFAULT_SOURCES_DIR = os.path.join("knowledge", "sources")

COLLECTIONS_MAP = {
    "admissions": os.path.join("admissions", "faq.json"),
    "academics": os.path.join("academics", "faq.json"),
    "placements": os.path.join("placements", "faq.json"),
    "research": os.path.join("research", "faq.json"),
    "student_services": os.path.join("student_services", "faq.json"),
    "navigation": os.path.join("navigation", "locations.json"),
}

def generate_unique_id(collection_name: str, item: Dict[str, Any], index: int) -> str:
    """
    Generates a deterministic unique ID for each document to support idempotency.
    If 'id' is provided in the JSON, it uses it. Otherwise, it generates a hash based on
    distinctive textual fields.
    """
    if "id" in item and item["id"]:
        return f"{collection_name}_{item['id']}"
    
    # Fallback to hashing stable content fields
    # Use 'question' for FAQs, 'facility' for navigation locations
    content_key = item.get("question") or item.get("facility") or f"index_{index}"
    hashed = hashlib.md5(content_key.encode("utf-8")).hexdigest()[:12]
    return f"{collection_name}_{hashed}"

def format_document(collection_name: str, item: Dict[str, Any]) -> str:
    """
    Formats the item into a standard "Question: ... \nAnswer: ..." format as a document.
    """
    if collection_name == "navigation":
        # Formulate a Q&A representation for navigation locations
        facility = item.get("facility", "Unknown Facility")
        building = item.get("building", "Unknown Building")
        floor = item.get("floor", "Unknown Floor")
        landmark = item.get("landmark", "Unknown Landmark")
        directions = item.get("directions", "No directions provided.")
        
        question = f"Where is the {facility}?"
        answer = f"The {facility} is located in {building} on the {floor} (landmark: {landmark}). Directions: {directions}"
    else:
        question = item.get("question", "").strip()
        answer = item.get("answer", "").strip()
        
    return f"Question: {question}\nAnswer: {answer}"

def get_metadata(collection_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs metadata fields from the item for filtering and source tracking.
    """
    metadata = {"category": collection_name}
    
    # Store topic/facility/building/floor details in metadata for granular filtering if needed
    for key in ["topic", "facility", "building", "floor", "landmark"]:
        if key in item and item[key]:
            metadata[key] = item[key]
            
    return metadata

def ingest_file(
    client: chromadb.PersistentClient,
    collection_name: str,
    file_path: str,
    emb_fn: Any
) -> Tuple[int, int]:
    """
    Reads a JSON file, creates/gets a collection, and ingests/upserts the documents.
    Returns a tuple of (inserted_count, error_count).
    """
    if not os.path.exists(file_path):
        logger.error(f"Source file not found for collection '{collection_name}': {file_path}")
        return 0, 1

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read or parse JSON file {file_path}: {e}")
        return 0, 1

    if not isinstance(data, list):
        logger.error(f"Invalid format in {file_path}. Expected a JSON array/list.")
        return 0, 1

    logger.info(f"Loaded {len(data)} items from {file_path}. Getting or creating collection '{collection_name}'...")
    
    try:
        # Get or create the collection with the specified embedding function
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=emb_fn
        )
    except Exception as e:
        logger.error(f"Failed to create/get collection '{collection_name}': {e}")
        return 0, len(data)

    ids = []
    documents = []
    metadatas = []
    
    for idx, item in enumerate(data):
        doc_id = generate_unique_id(collection_name, item, idx)
        doc_text = format_document(collection_name, item)
        meta = get_metadata(collection_name, item)
        
        ids.append(doc_id)
        documents.append(doc_text)
        metadatas.append(meta)

    # Ingest in chunks/batches to prevent payload size issues
    batch_size = 100
    success_count = 0
    failure_count = 0
    
    logger.info(f"Ingesting documents into collection '{collection_name}'...")
    
    for i in tqdm(range(0, len(ids), batch_size), desc=f"Ingesting {collection_name}"):
        batch_ids = ids[i:i + batch_size]
        batch_docs = documents[i:i + batch_size]
        batch_metas = metadatas[i:i + batch_size]
        
        try:
            # Using upsert to avoid duplicate key errors and update documents if they change
            collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas
            )
            success_count += len(batch_ids)
        except Exception as e:
            logger.error(f"Error during upsert batch in collection '{collection_name}': {e}")
            failure_count += len(batch_ids)

    logger.info(f"Completed collection '{collection_name}': {success_count} success, {failure_count} failures.")
    return success_count, failure_count

def main():
    parser = argparse.ArgumentParser(description="Ingest university knowledge JSONs into ChromaDB.")
    parser.add_argument(
        "--db-path",
        type=str,
        default=DEFAULT_DB_PATH,
        help=f"Path to persistent ChromaDB storage (default: {DEFAULT_DB_PATH})"
    )
    parser.add_argument(
        "--sources-dir",
        type=str,
        default=DEFAULT_SOURCES_DIR,
        help=f"Directory containing JSON sources (default: {DEFAULT_SOURCES_DIR})"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing collections before ingesting new data"
    )
    args = parser.parse_args()

    start_time = time.time()
    
    logger.info(f"Initializing ChromaDB PersistentClient at: {args.db_path}")
    try:
        # Create persistent client
        client = chromadb.PersistentClient(path=args.db_path)
    except Exception as e:
        logger.critical(f"Failed to initialize PersistentClient: {e}")
        return

    # Initialize standard embedding function (using sentence-transformers local model)
    logger.info("Initializing SentenceTransformer embedding function (all-MiniLM-L6-v2)...")
    try:
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    except Exception as e:
        logger.warning(f"Could not load local SentenceTransformer function: {e}. Falling back to default embeddings.")
        emb_fn = None

    if args.reset:
        logger.warning("Reset mode activated. Deleting existing collections...")
        for col_name in COLLECTIONS_MAP.keys():
            try:
                client.delete_collection(name=col_name)
                logger.info(f"Deleted collection '{col_name}' successfully.")
            except Exception:
                # Collection might not exist, ignore
                pass

    summary = []
    total_success = 0
    total_failures = 0

    for col_name, relative_path in COLLECTIONS_MAP.items():
        file_path = os.path.join(args.sources_dir, relative_path)
        logger.info(f"Processing collection '{col_name}' from: {file_path}")
        
        success, failure = ingest_file(client, col_name, file_path, emb_fn)
        
        # Get actual document count in the collection now
        actual_count = 0
        try:
            col = client.get_collection(name=col_name)
            actual_count = col.count()
        except Exception:
            pass

        summary.append({
            "collection": col_name,
            "file": relative_path,
            "success": success,
            "failure": failure,
            "total_count": actual_count
        })
        
        total_success += success
        total_failures += failure

    duration = time.time() - start_time

    # Print Ingestion Summary Table
    print("\n" + "="*80)
    print("                          CHROMADB INGESTION SUMMARY")
    print("="*80)
    print(f"Persistent DB Path: {os.path.abspath(args.db_path)}")
    print(f"Total Time Taken  : {duration:.2f} seconds")
    print(f"Total Successful  : {total_success}")
    print(f"Total Failed      : {total_failures}")
    print("-"*80)
    print(f"{'Collection':<20} | {'Source File':<35} | {'Ingested':<8} | {'Failed':<6} | {'Total Docs':<10}")
    print("-"*80)
    for row in summary:
        print(f"{row['collection']:<20} | {row['file']:<35} | {row['success']:<8} | {row['failure']:<6} | {row['total_count']:<10}")
    print("="*80)

if __name__ == "__main__":
    main()
