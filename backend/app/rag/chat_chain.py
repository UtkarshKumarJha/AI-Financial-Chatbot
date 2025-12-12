import asyncio
from datetime import datetime

# Internal imports
from .vector_store import retrieve
from .gemini_llm import get_gemini_llm
from ..services.data_fetcher import fetch_fundamentals, fetch_price_history
from ..services.sentiment import compute_sentiment
from ..services.predictor import predict_prices, generate_chart_data

# --------------------------------------
# Helper: Format retrieved documents
# --------------------------------------
def format_docs(docs):
    if not docs:
        return "No relevant news articles found."
        
    out = []
    for i, d in enumerate(docs, 1):
        meta = d.metadata
        # Clean up newlines for cleaner injection
        snippet = d.page_content[:300].replace("\n", " ")
        title = meta.get('title', 'Unknown Title')
        source = meta.get('source', 'Unknown Source')
        
        out.append(f"[{i}] {title} ({source})\n    Snippet: {snippet}...")
    return "\n\n".join(out)

# --------------------------------------
# Main Chat Function
# --------------------------------------
async def run_chat(user_input, ticker=None, horizon_days=7):
    # Normalize Ticker
    ticker = ticker.upper() if ticker else None
    
    # -----------------------------
    # 1) Retrieve News (Context)
    # -----------------------------
    collection = f"news_{ticker.lower()}" if ticker else "news"
    retrieved_docs = retrieve(
        user_input if not ticker else ticker,
        k=5,
        collection=collection
    )
    print(f"Retrieved {len(retrieved_docs)} documents for ticker '{ticker}'.")
    # -----------------------------
    # 2) Fetch Real-Time Data
    # -----------------------------
    # We use asyncio.gather for parallel fetching (faster response)
    if ticker:
        fundamentals, price_history = await asyncio.gather(
            fetch_fundamentals(ticker),
            fetch_price_history(ticker)
        )
        
        # Run sentiment & prediction
        sentiment = compute_sentiment([d.metadata for d in retrieved_docs])
        prediction = await predict_prices(price_history, horizon_days)
        
        # Generate Chart Data (History + Forecast)
        chart_data = generate_chart_data(price_history, prediction)
    else:
        fundamentals, price_history, sentiment, prediction, chart_data = {}, [], {}, {}, []

    # -----------------------------
    # 3) The "Professional" Prompt
    # -----------------------------
    # We explicitly instruct Gemini on HOW to handle data gaps (7 vs 14 days)
    
    context = f"""
You are InsightInvest, a Senior Investment Strategist at a top-tier firm. 
Your goal is to synthesize complex financial data into a clear, professional narrative.

### AVAILABLE DATA
---
**1. FUNDAMENTALS (Quarterly Trends & Health):**
{fundamentals}

**2. MARKET SENTIMENT (News Analysis):**
{sentiment}

**3. QUANTITATIVE MODEL (Technical Forecast):**
{prediction}
*(Note: The model provides a 7-day technical forecast with 90% confidence intervals. 'forecast_range_low/high' indicates volatility risk.)*

**4. RECENT NEWS (Sources):**
{format_docs(retrieved_docs)}

**5. USER INQUIRY:**
"{user_input}"
---

### ANALYST INSTRUCTIONS (Review Carefully):

1.  **ANSWER THE QUESTION IMMEDIATELY:** * If the user asks a specific question (e.g., "Should I buy?", "Is it overvalued?", "What is the risk?"), **the very first sentence of your "analysis" must be a direct answer.** * *Example:* "Given the bearish technical signal despite positive news, it is advisable to wait for a lower entry point."
    * Do not start with "Apple is a tech company..." start with the conclusion.

2.  **SYNTHESIZE, DON'T LIST:** * Explain the *interaction* between data points.
    * *Bad:* "Sentiment is 0.8. Price is predicted to drop."
    * *Good:* "While market sentiment is highly positive (0.8), our technical model diverges significantly, predicting a short-term pullback. This suggests the stock may be overbought."

3.  **HANDLE LIMITATIONS GRACEFULLY:**
    * If the user asks for a timeframe longer than your 7-day model (e.g., "14 days" or "1 month"):
    * **DO NOT** say "I only have 7 days."
    * **DO** use the *Sentiment* and *Fundamentals* (which are long-term indicators) to bridge the gap. Extrapolate logically.

4.  **TONE & STYLE:**
    * Professional, objective, insightful.
    * No "I am an AI" or "As a language model."
    * Use financial terminology appropriately (volatility, consolidation, catalyst, headwinds).

### REQUIRED OUTPUT FORMAT (Strict JSON):
Respond ONLY with this JSON structure. Do not add markdown outside the JSON.

{{
  "analysis": "Direct answer to the user's question followed by a detailed 3-4 sentence synthesis of news, fundamentals, and price action.",
  "sentiment_summary": "A concise summary of the market mood (Bullish/Bearish) and key drivers.",
  "prediction_summary": "A professional description of the model's forecast. Mention the confidence interval to explain risk.",
  "risk_factors": "List 2-3 key risks (e.g., 'High Volatility', 'Declining Revenue', 'Sentiment/Price Divergence').",
  "confidence": "Low | Medium | High",
  "disclaimer": "Not financial advice. For informational purposes only."
}}
"""

    # -----------------------------
    # 4) Execute Reasoning Engine
    # -----------------------------
    llm = get_gemini_llm()
    resp = llm.invoke(context)

    reply = getattr(resp, "text", "")
    if not reply and hasattr(resp, "content"):
        reply = resp.content
    if isinstance(reply, list):
        reply = reply[0].text
        
    reply = reply.strip()
    if reply.startswith("```"):
        reply = reply.split("```")[1]
        if reply.startswith("json"):
            reply = reply[4:]
    reply = reply.strip()

    return {
        "reply": reply,
        "fundamentals": fundamentals,
        "sentiment": sentiment,
        "prediction": prediction,
        "chart_data": chart_data,
        "sources": [d.metadata for d in retrieved_docs],
    }