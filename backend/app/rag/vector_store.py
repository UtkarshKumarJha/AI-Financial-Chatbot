# backend/app/rag/vector_store.py

import os
import hashlib
from typing import List, Dict

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
HF_MODEL = os.getenv("HF_EMB_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=HF_MODEL)

def get_vectorstore(collection_name="news"):
    embeddings = get_embeddings()
    return Chroma(
        embedding_function=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_PERSIST_DIR,
    )

def generate_doc_id(url: str) -> str:
    """Generates a consistent MD5 hash from the URL to use as a Document ID."""
    return hashlib.md5(url.encode("utf-8")).hexdigest()

def docs_from_news(news_docs: List[Dict]) -> (List[Document], List[str]):
    """
    Converts news dicts to LangChain Documents and generates unique IDs.
    Returns: (docs_list, ids_list)
    """
    docs = []
    ids = []
    
    for nd in news_docs:
        title = nd.get("title") or ""
        description = nd.get("content") or nd.get("description") or ""
        url = nd.get("url") or ""
        
        # Skip useless empty articles
        if not title and not description:
            continue
            
        # Create a comprehensive content block
        page_content = f"{title}\n{description}"
        
        metadata = {
            "source": nd.get("source"),
            "url": url,
            "published_at": nd.get("published_at"),
            "title": title,
        }

        # Generate Unique ID based on URL
        # If URL is missing (rare), fall back to title hash
        unique_id = generate_doc_id(url) if url else generate_doc_id(title)

        docs.append(Document(page_content=page_content, metadata=metadata))
        ids.append(unique_id)
        
    return docs, ids

def ingest_documents(docs: List[Document], ids: List[str], collection_name: str):
    """
    Smart Ingestion: Checks for existing IDs before adding to avoid duplicates.
    """
    if not docs:
        return 0

    vs = get_vectorstore(collection_name)
    
    # 1. Check which IDs already exist in the DB
    existing_records = vs.get(ids=ids)
    existing_ids = set(existing_records["ids"])

    # 2. Filter out duplicates
    new_docs = []
    new_ids = []
    
    for doc, doc_id in zip(docs, ids):
        if doc_id not in existing_ids:
            new_docs.append(doc)
            new_ids.append(doc_id)
            
    # 3. Add only new documents
    if new_docs:
        vs.add_documents(documents=new_docs, ids=new_ids)
        # Chroma persists automatically in newer versions, but explicit calls don't hurt if old version
        # vs.persist() 
        print(f"✅ Ingested {len(new_docs)} new documents into '{collection_name}'.")
    else:
        print(f"⏩ Skipped ingestion for '{collection_name}' (all docs already exist).")

    return len(new_docs)

def retrieve(query, k=5, collection="news"):
    vs = get_vectorstore(collection)
    retriever = vs.as_retriever(search_kwargs={"k": k})
    return retriever.invoke(query)