# backend/app/rag/gemini_llm.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.2,
        max_output_tokens=4096,
    )
