# backend/app/api_report.py

import asyncio
from ..services.data_fetcher import fetch_fundamentals, fetch_price_history, fetch_news_docs
from ..services.sentiment import compute_sentiment
from ..services.predictor import predict_prices
from datetime import datetime

async def generate_report(ticker: str, horizon_days: int = 7):

    fund_task = asyncio.create_task(fetch_fundamentals(ticker))
    price_task = asyncio.create_task(fetch_price_history(ticker))
    news_task = asyncio.create_task(fetch_news_docs(ticker))

    fundamentals = await fund_task
    price_history = await price_task
    news_docs = await news_task

    sentiment = compute_sentiment(news_docs)
    prediction = await predict_prices(price_history, horizon_days)

    return {
        "ticker": ticker.upper(),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "fundamentals": fundamentals,
        "price_history": price_history,
        "news_docs": news_docs,
        "sentiment": sentiment,
        "prediction": prediction,
    }
