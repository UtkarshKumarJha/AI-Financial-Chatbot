from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

def compute_sentiment(news_docs):
    if not isinstance(news_docs, list):
        return {"average_sentiment": 0}

    scores = []
    for article in news_docs:
        text = (article.get("title","") or "") + " " + (article.get("content","") or "")
        print(article.get("content"))
        if text.strip():
            score = sia.polarity_scores(text)["compound"]
            scores.append(score)

    if not scores:
        return {"average_sentiment": 0}

    avg = sum(scores) / len(scores)
    return {"average_sentiment": round(avg, 3)}
