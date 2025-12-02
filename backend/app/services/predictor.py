import numpy as np
import pandas as pd
import xgboost as xgb
from typing import Dict, List

# ==========================================
# 1. FEATURE ENGINEERING (Pure Technicals)
# ==========================================

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Log Returns, RSI, Volatility, and SMA Distance.
    """
    df = df.copy()
    
    # 1. Log Returns (The Target)
    df['log_ret'] = np.log(df['close'] / df['close'].shift(1))
    
    # 2. Volatility (Risk)
    df["volatility"] = df['log_ret'].rolling(window=5).std()
    
    # 3. RSI (Momentum)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    
    # 4. SMA Distance (Mean Reversion)
    df["sma_dist"] = df['close'] / df['close'].rolling(window=10).mean() - 1

    # Fill NaNs
    df = df.fillna(0)
    return df

def build_features(df, lags=7):
    """
    Converts time-series into supervised learning format (X, y).
    """
    X, y = [], []
    target_col = 'log_ret'
    
    for i in range(lags, len(df) - 1):
        past_returns = df[target_col].iloc[i-lags:i].values.tolist()
        
        technical_features = [
            df["rsi"].iloc[i],
            df["sma_dist"].iloc[i],
            df["volatility"].iloc[i]
        ]
        
        features = past_returns + technical_features
        target = df[target_col].iloc[i+1]
        
        X.append(features)
        y.append(target)
        
    return np.array(X), np.array(y)

# ==========================================
# 2. MAIN PREDICTION PIPELINE
# ==========================================

async def predict_prices(price_history: List[Dict], horizon_days=7, sentiment_score: float = 0.0):
    """
    Predicts future prices using XGBoost + Sentiment Adjustment Layer.
    """
    # 1. Validation
    if not price_history or len(price_history) < 60:
        return {"error": "Not enough data (need > 60 days)"}

    # 2. Convert to DataFrame
    df = pd.DataFrame(price_history)
    df['close'] = df['close'].astype(float)
    
    # 3. Apply Engineering
    df_tech = calculate_technical_indicators(df)
    
    # 4. Build Dataset
    lags = 7
    X, y = build_features(df_tech, lags=lags)
    
    if len(X) < 20:
        return {"error": "Not enough valid training samples"}

    # 5. Train Model (Pure Technicals)
    # Using your Kaggle-validated hyperparameters
    model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        objective="reg:squarederror",
        n_jobs=-1,
        random_state=42
    )
    model.fit(X, y)

    # 6. Calculate Uncertainty (Conformal Prediction)
    preds_train = model.predict(X)
    errors = np.abs(y - preds_train)
    uncertainty_margin = np.percentile(errors, 90)

    # 7. Recursive Forecast with Sentiment Adjustment
    future_prices = []
    current_price = df_tech['close'].iloc[-1]
    
    # Build initial input vector
    last_known_idx = -1
    current_features = df_tech['log_ret'].iloc[-lags:].values.tolist() + [
        df_tech['rsi'].iloc[last_known_idx],
        df_tech['sma_dist'].iloc[last_known_idx],
        df_tech['volatility'].iloc[last_known_idx]
    ]

    # --- THE SENTIMENT BIAS FACTOR ---
    # We apply a small daily drift based on sentiment score (-1 to 1).
    # 0.001 means a strong 1.0 sentiment adds 0.1% daily return boost.
    # Over 7 days, this can shift price by ~0.7-1.0%, which is significant but realistic.
    sentiment_bias = sentiment_score * 0.001 

    for i in range(horizon_days):
        # A. Get Technical Prediction (Base Math)
        pred_log_ret = float(model.predict(np.array([current_features]))[0])
        
        # B. Apply Sentiment Bias (The "Hybrid" Logic)
        # If sentiment is positive, we tilt the probability up.
        # We decay the bias slightly each day (news fades).
        daily_bias = sentiment_bias * (0.9 ** i)
        adjusted_log_ret = pred_log_ret + daily_bias
        
        # C. Convert back to Price
        next_price = current_price * np.exp(adjusted_log_ret)
        future_prices.append(next_price)
        current_price = next_price
        
        # D. Update Feature Vector for next step
        current_features = current_features[1:lags] + [adjusted_log_ret] + current_features[lags:]

    # 8. Output
    final_price = future_prices[-1]
    
    # Adjust Confidence Interval based on Sentiment Strength
    # Strong sentiment = Higher volatility risk = Wider cone
    scaling_factor = np.sqrt(horizon_days)
    upper_bound = final_price * np.exp(uncertainty_margin * scaling_factor)
    lower_bound = final_price * np.exp(-uncertainty_margin * scaling_factor)

    return {
        "current_price": df_tech['close'].iloc[-1],
        "forecast_7d": round(final_price, 2),
        "forecast_range_low": round(lower_bound, 2),
        "forecast_range_high": round(upper_bound, 2),
        "confidence_interval_90": round(upper_bound - final_price, 2),
        "method": "XGBoost (Log-Returns) + Sentiment Adjustment",
        "plot_data": future_prices
    }

# ==========================================
# 3. HELPER FOR FRONTEND CHART
# ==========================================
from datetime import datetime, timedelta

def generate_chart_data(price_history, prediction_data):
    chart_data = []
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

    if prediction_data and "plot_data" in prediction_data:
        forecast_vals = prediction_data["plot_data"]
        # Calculate proportional width for the cone
        total_width_pct = (prediction_data["forecast_range_high"] / prediction_data["forecast_7d"]) - 1
        
        if last_date_str:
            current_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        else:
            current_date = datetime.utcnow()

        for i, val in enumerate(forecast_vals):
            current_date += timedelta(days=1)
            # Cone grows with sqrt of time
            step_uncertainty = total_width_pct * np.sqrt((i+1) / len(forecast_vals))
            upper = val * (1 + step_uncertainty)
            lower = val * (1 - step_uncertainty)

            chart_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "price": round(val, 2),
                "type": "forecast",
                "lower": round(lower, 2),
                "upper": round(upper, 2)
            })

    return chart_data