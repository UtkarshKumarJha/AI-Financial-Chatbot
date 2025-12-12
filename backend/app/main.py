from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from .api.report import generate_report
from fastapi.middleware.cors import CORSMiddleware
from .api.chat import router as chat_router

app = FastAPI(
    title="InsightInvest API",
    version="1.0.0",
    description="API for InsightInvest Financial Chatbot"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReportRequest(BaseModel):
    ticker: str
    horizon_days: int=7
    
@app.post("/api/report")
async def report(req:ReportRequest):
    ticker = req.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required.")
    report = await generate_report(ticker, req.horizon_days)
    return report

@app.get("/health")
async def health_check():
    return {"status": "ok","fake_data": os.getenv("FAKE_DATA","0")} 

app.include_router(chat_router)