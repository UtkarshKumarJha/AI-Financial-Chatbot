# backend/app/api/chat.py

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

# Import the ingestion service (make sure you created the file from the previous step)
from ..rag.ingest import ingest_news_for_ticker
from ..rag.chat_chain import run_chat
from ..rag.vector_store import retrieve

router = APIRouter()

class ChatReq(BaseModel):
    user_input: str
    ticker: str | None = None
    horizon_days: int = 7

@router.post("/api/chat")
async def api_chat(req: ChatReq, background_tasks: BackgroundTasks):
    """
    Main chat endpoint.
    1. Triggers background news ingestion (non-blocking).
    2. Runs the RAG/LLM chain immediately using *existing* data.
    """
    if req.ticker:
        ticker = req.ticker.upper()
        collection_name = f"news_{ticker.lower()}"
        existing_docs = retrieve(query=ticker, k=1, collection=collection_name)
        if not existing_docs:
            print(f"No existing news for {ticker}.")
            await ingest_news_for_ticker(ticker, limit=25)
            print(f"Ingestion for {ticker} completed.")
        else:
            print(f"Existing news found for {ticker}, refreshing ingestion.")
            background_tasks.add_task(ingest_news_for_ticker, ticker, limit=25)
        
    return await run_chat(
        user_input=req.user_input,
        ticker=req.ticker,
        horizon_days=req.horizon_days
    )