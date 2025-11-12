# backend/app/services/sentiment.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load FinBERT model from Hugging Face
MODEL_NAME = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Label mapping for FinBERT
id2label = {0: "neutral", 1: "positive", 2: "negative"}

def compute_sentiment(news_docs):
    """
    Compute average sentiment using FinBERT for finance-specific text.
    Returns average polarity and counts of each sentiment label.
    """
    if not isinstance(news_docs, list) or len(news_docs) == 0:
        return {"average_sentiment": 0, "label_distribution": {}, "note": "no news data"}

    scores = []
    labels = {"positive": 0, "negative": 0, "neutral": 0}

    for article in news_docs:
        text = ((article.get("title") or "") + " " + (article.get("content") or "")).strip()
        if not text:
            continue

        # Tokenize and run through FinBERT
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            pred = torch.argmax(probs, dim=1).item()
            label = id2label[pred]
            confidence = probs[0][pred].item()

        # Map to numerical sentiment score for averaging
        if label == "positive":
            val = confidence
        elif label == "negative":
            val = -confidence
        else:
            val = 0

        scores.append(val)
        labels[label] += 1

    # Compute average sentiment value
    if not scores:
        return {"average_sentiment": 0, "label_distribution": labels}

    avg = sum(scores) / len(scores)
    return {
        "average_sentiment": round(avg, 3),
        "label_distribution": labels,
    }
