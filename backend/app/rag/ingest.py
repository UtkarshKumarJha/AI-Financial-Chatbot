from ..services.data_fetcher import fetch_news_docs
from .vector_store import docs_from_news, ingest_documents

async def ingest_news_for_ticker(ticker: str, limit: int = 25):
    ticker = ticker.upper()
    collection_name = f"news_{ticker.lower()}"
    
    print(f"Fetching news for {ticker}...")
    raw_news = await fetch_news_docs(ticker, limit=limit)
    
    if not raw_news or "error" in raw_news[0]:
        print(f"Error fetching news for {ticker}: {raw_news}")
        return {"status": "error", "details": raw_news}

    docs, ids = docs_from_news(raw_news)

    count = ingest_documents(docs, ids, collection_name)

    return {
        "ticker": ticker,
        "new_articles_ingested": count,
        "total_fetched": len(docs),
        "collection": collection_name
    }