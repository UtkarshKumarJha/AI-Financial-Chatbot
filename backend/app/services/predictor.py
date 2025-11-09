# backend/app/services/predictor.py

import numpy as np
from sklearn.ensemble import RandomForestRegressor

def _extract_closes(price_history):
    try:
        return np.array([float(p["close"]) for p in price_history])
    except:
        return None

def make_features(closes):
    if len(closes) < 14:
        last = closes[-1]
        return np.array([[last, last, last, last]])

    return np.array([[
        closes[-3:].mean(),
        closes[-7:].mean(),
        closes[-14:].mean(),
        closes[-1]
    ]])

async def predict_prices(price_history, horizon_days=7):
    closes = _extract_closes(price_history)
    if closes is None or len(closes) < 30:
        return {"error": "not enough data (need >= 30 days)"}

    X, y = [], []
    for i in range(14, len(closes) - 1):
        window = closes[:i]
        X.append(make_features(window)[0])
        y.append(closes[i])

    model = RandomForestRegressor(n_estimators=60, random_state=42)
    model.fit(X, y)

    simulated = closes.copy()
    preds = []

    for _ in range(horizon_days):
        feat = make_features(simulated)
        next_price = float(model.predict(feat)[0])
        preds.append(round(next_price, 2))
        simulated = np.append(simulated, next_price)

    return {
        "horizon_days": horizon_days,
        "predictions": preds,
        "method": "rf_v2"
    }
