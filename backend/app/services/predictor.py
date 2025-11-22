import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List
from datetime import datetime, timedelta

def calculate_rsi(series, period=14):
    """Calculates Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_technical_indicators(prices: List[float]) -> pd.DataFrame:
    """
    Adds RSI, SMA_20, and Volatility features.
    """
    df = pd.DataFrame(prices, columns=["close"])
    
    # 1. Simple Moving Average (SMA 20)
    df["sma_20"] = df["close"].rolling(window=20).mean()
    
    # 2. RSI (14)
    df["rsi"] = calculate_rsi(df["close"], period=14)
    
    # 3. Volatility (Standard Deviation of last 5 days)
    df["volatility"] = df["close"].rolling(window=5).std()
    
    # Fill NaNs (first few rows will be empty due to rolling windows)
    df.fillna(method="bfill", inplace=True)
    df.fillna(0, inplace=True)
    
    return df

def build_dataset(df, lags=7):
    """
    Converts time-series dataframe into Supervised Learning format (X, y).
    """
    X, y = [], []
    # We need enough data for lags
    for i in range(lags, len(df)):
        # Feature vector: 
        # [Lag1, Lag2... Lag7, RSI_curr, SMA_curr, Vol_curr]
        lagged_prices = df["close"].iloc[i-lags:i].values.tolist()
        
        technical_features = [
            df["rsi"].iloc[i-1],      # RSI yesterday
            df["sma_20"].iloc[i-1],   # SMA yesterday
            df["volatility"].iloc[i-1]# Volatility yesterday
        ]
        
        features = lagged_prices + technical_features
        target = df["close"].iloc[i]
        
        X.append(features)
        y.append(target)
        
    return np.array(X), np.array(y)

async def predict_prices(price_history: List[Dict], horizon_days=7):
    """
    Advanced Prediction Pipeline:
    1. Featurization (RSI/SMA)
    2. XGBoost Regressor
    3. Conformal Prediction (Confidence Intervals)
    """
    # 1. Extract & Clean Data
    if not price_history or len(price_history) < 60:
        return {"error": "Not enough data (need > 60 days for technical analysis)"}

    prices = [p["close"] for p in price_history]
    
    # 2. Feature Engineering
    df_tech = calculate_technical_indicators(prices)
    
    # 3. Build Dataset (X, y)
    lags = 7
    X, y = build_dataset(df_tech, lags=lags)
    
    # Split into Train (80%) and Calibration (20%)
    # We use the calibration set to measure "How wrong is the model usually?"
    split = int(len(X) * 0.8)
    X_train, X_calib = X[:split], X[split:]
    y_train, y_calib = y[:split], y[split:]

    # 4. Train Model
    model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        objective="reg:squarederror",
        random_state=42
    )
    model.fit(X_train, y_train)

    # 5. Calculate Uncertainty (Conformal Prediction Lite)
    # Predict on calibration set
    preds_calib = model.predict(X_calib)
    # Calculate absolute errors
    errors = np.abs(y_calib - preds_calib)
    # Take the 90th percentile error (we are 90% sure error is below this)
    uncertainty_margin = np.percentile(errors, 90)

    # 6. Forecast Future
    future_preds = []
    current_window = df_tech["close"].iloc[-lags:].values.tolist()
    
    # We need the latest technicals to start the chain
    curr_rsi = df_tech["rsi"].iloc[-1]
    curr_sma = df_tech["sma_20"].iloc[-1]
    curr_vol = df_tech["volatility"].iloc[-1]

    # Recursive prediction loop
    temp_window = current_window.copy()
    
    for _ in range(horizon_days):
        # Build input vector
        features = temp_window[-lags:] + [curr_rsi, curr_sma, curr_vol]
        
        next_price = float(model.predict(np.array([features]))[0])
        
        # Append to results
        future_preds.append(next_price)
        
        # Update window for next step
        temp_window.append(next_price)
        
        # Note: In a real production system, you'd update RSI/SMA dynamically here.
        # For this MVP, keeping them static for 7 days is an acceptable approximation.

    # 7. Format Output with Confidence Intervals
    final_prediction = future_preds[-1]
    
    return {
        "current_price": prices[-1],
        "forecast_7d": round(final_prediction, 2),
        "forecast_range_low": round(final_prediction - uncertainty_margin, 2),
        "forecast_range_high": round(final_prediction + uncertainty_margin, 2),
        "confidence_interval_90": round(uncertainty_margin, 2),
        "method": "XGBoost + RSI/SMA + Conformal Prediction",
        "plot_data": future_preds # Frontend can use this to draw the line
    }
    
def generate_chart_data(price_history, prediction_data):
    """
    Merges historical data with future predictions into a single
    chart-ready format for the frontend.
    """
    chart_data = []
    
    # 1. Process History (Last 60 days max to keep chart clean)
    # We assume price_history is sorted by date ascending
    history_slice = price_history[-60:] if len(price_history) > 60 else price_history
    
    last_date_str = None
    
    for day in history_slice:
        chart_data.append({
            "date": day["date"],
            "price": day["close"],
            "type": "history",
            "lower": None,
            "upper": None
        })
        last_date_str = day["date"]

    # 2. Process Forecast
    # We need to generate future dates starting from the day after history ends
    if prediction_data and "plot_data" in prediction_data:
        forecast_vals = prediction_data["plot_data"]
        confidence = prediction_data.get("confidence_interval_90", 0)
        
        if last_date_str:
            current_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        else:
            current_date = datetime.utcnow()

        for val in forecast_vals:
            current_date += timedelta(days=1)
            # Skip weekends if you want (optional, keeping it simple for now)
            
            chart_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "price": round(val, 2),
                "type": "forecast",
                "lower": round(val - confidence, 2),
                "upper": round(val + confidence, 2)
            })

    return chart_data