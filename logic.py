# logic.py

import pandas as pd

# --- Performance ---
def perf(series, days):
    return (series.iloc[-1] / series.iloc[-days] - 1) * 100

# --- Breadth (% above EMA21) ---
def percent_above_ema(df, length=21):
    ema = df.ewm(span=length).mean()
    return (df.iloc[-1] > ema.iloc[-1]).mean()

# --- RS Score (3 Month Relative Strength) ---
def rs_score(group_price, index_price):
    rs = group_price / index_price
    return rs.pct_change(63).iloc[-1] * 100

# --- RS Momentum (1 Month Change) ---
def rs_momentum(group_price, index_price):
    rs = group_price / index_price
    return rs.pct_change(21).iloc[-1] * 100

# --- Phase Classification ---
def classify(rs, breadth):
    if rs > 5 and breadth > 0.6:
        return "Leading"
    elif rs > 0:
        return "Emerging"
    elif rs < -5:
        return "Lagging"
    else:
        return "Weakening"

# --- Market State ---
def market_state(index):
    ret = index.pct_change().iloc[-1] * 100

    if ret > 1.5:
        return "🚀 Burst Day"
    elif ret > 0.7:
        return "🔥 Ignition Day"
    elif abs(ret) < 0.3:
        return "😐 Neutral Day"
    else:
        return "⚖️ Pause Day"