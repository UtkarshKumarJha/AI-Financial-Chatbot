import os
import hashlib
from typing import List, Dict
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")

def get_embeddings():
    """
    Returns the embedding function using Hugging Face's Serverless Inference API.
    """
    api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not api_key:
        print("⚠️ WARNING: HUGGINGFACEHUB_API_TOKEN is missing. Embeddings will fail.")
        return None
    
    return HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=api_key,
    )

def get_vectorstore(collection_name="news"):
    embeddings = get_embeddings()
    if not embeddings:
        raise ValueError("Cannot initialize vector store without embeddings.")
        
    return Chroma(
        embedding_function=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_PERSIST_DIR,
    )

def generate_doc_id(url: str) -> str:
    """Generates a consistent MD5 hash from the URL to use as a Document ID."""
    if not url:
        return hashlib.md5(os.urandom(16)).hexdigest()
    return hashlib.md5(url.encode("utf-8")).hexdigest()

def docs_from_news(news_docs: List[Dict]):
    """Converts news dicts to LangChain Documents."""
    docs = []
    ids = []
    
    for nd in news_docs:
        title = nd.get("title") or ""
        description = nd.get("content") or nd.get("description") or ""
        url = nd.get("url") or ""
        
        if not title and not description:
            continue
            
        page_content = f"{title}\n{description}"
        
        metadata = {
            "source": nd.get("source"),
            "url": url,
            "published_at": nd.get("published_at"),
            "title": title,
        }

        unique_id = generate_doc_id(url)
        docs.append(Document(page_content=page_content, metadata=metadata))
        ids.append(unique_id)
        
    return docs, ids

def ingest_documents(docs: List[Document], ids: List[str], collection_name: str):
    """Smart Ingestion: Checks for existing IDs before adding."""
    if not docs:
        return 0

    try:
        vs = get_vectorstore(collection_name)
        
        try:
            existing_records = vs.get(ids=ids)
            existing_ids = set(existing_records["ids"]) if existing_records else set()
        except:
            existing_ids = set()

        new_docs = []
        new_ids = []
        
        for doc, doc_id in zip(docs, ids):
            if doc_id not in existing_ids:
                new_docs.append(doc)
                new_ids.append(doc_id)
                
        if new_docs:
            vs.add_documents(documents=new_docs, ids=new_ids)
            print(f"✅ Ingested {len(new_docs)} new documents into '{collection_name}'.")
        else:
            print(f"⏩ Skipped ingestion for '{collection_name}' (all docs already exist).")

        return len(new_docs)
        
    except Exception as e:
        print(f"❌ Critical Error in ingest_documents: {e}")
        return 0

def retrieve(query, k=5, collection="news"):
    try:
        vs = get_vectorstore(collection)
        retriever = vs.as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)
    except Exception as e:
        print(f"❌ Error retrieving documents: {e}")
        return []