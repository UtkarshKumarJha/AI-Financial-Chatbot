from .celery_app import app
from .rag.ingest import ingest_news_for_ticker
import asyncio

@app.task(name="ingest_ticker_news")
def task_ingest_news(ticker: str):
    print(f"Worker: Starting ingestion for {ticker}...")
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(ingest_news_for_ticker(ticker))
    
    print(f"Worker: Finished ingestion for {ticker}")
    return result