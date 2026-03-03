import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

from groups import GROUPS, INDEX
from logic import *

st.set_page_config(layout="wide")
st.title("📊 ASX Leading Industry Groups — PRO")

# -----------------------
# LOAD DATA
# -----------------------
@st.cache_data(ttl=3600)
def load_data(tickers):
    data = yf.download(tickers, period="1y")["Close"]
    return data.dropna(how="all")

tickers = list(set(sum(GROUPS.values(), [])))
data = load_data(tickers + [INDEX])
index_price = data[INDEX]

# -----------------------
# MARKET STATUS
# -----------------------
state = market_state(index_price)
st.header(f"Market Status: {state}")

# -----------------------
# CALCULATE GROUP DATA
# -----------------------
rows = []

for group, stocks in GROUPS.items():
    df = data[stocks].dropna(axis=1)

    if df.empty:
        continue

    group_price = df.mean(axis=1)

    rs = rs_score(group_price, index_price)
    momentum = rs_momentum(group_price, index_price)
    breadth = percent_above_ema(df)
    phase = classify(rs, breadth)

    rows.append({
        "Group": group,
        "RS": round(rs,2),
        "Momentum": round(momentum,2),
        "Breadth %": round(breadth*100,1),
        "Phase": phase,
        "3M %": round(perf(group_price,63),2)
    })

rank_df = pd.DataFrame(rows).sort_values("RS", ascending=False)

# -----------------------
# TOP 3 LEADERS
# -----------------------
st.subheader("🏆 Top 3 Leading Groups")

cols = st.columns(3)
for i in range(min(3, len(rank_df))):
    row = rank_df.iloc[i]
    cols[i].metric(
        row["Group"],
        f'RS {row["RS"]}',
        row["Phase"]
    )

# -----------------------
# TABLE
# -----------------------
st.subheader("📋 Industry Rotation Table")
st.dataframe(rank_df, use_container_width=True)

# -----------------------
# ROTATION CHART
# -----------------------
st.subheader("🔄 Industry Rotation")

fig = px.scatter(
    rank_df,
    x="RS",
    y="Momentum",
    text="Group",
    size="Breadth %",
    title="Industry Rotation Quadrant"
)

fig.update_traces(textposition="top center")
fig.add_hline(y=0)
fig.add_vline(x=0)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# RS TREND
# -----------------------
st.subheader("📈 RS Trend vs ASX 200")

group_choice = st.selectbox("Select Group", rank_df["Group"])

stocks = GROUPS[group_choice]
group_series = data[stocks].mean(axis=1)

rs_line = (group_series / index_price) * 100

fig2 = px.line(rs_line, title=f"{group_choice} RS vs ASX 200")
st.plotly_chart(fig2, use_container_width=True)
# -----------------------
# STOCK DRILL-DOWN
# -----------------------
st.subheader(f"🔎 {group_choice} — Stock Leaders")

stock_rows = []

for stock in stocks:
    if stock not in data.columns:
        continue
        
    stock_series = data[stock].dropna()
    
    if len(stock_series) < 100:
        continue

    # Stock RS vs index
    rs_stock = rs_score(stock_series, index_price)
    
    # 3M performance
    perf_3m = perf(stock_series, 63)
    
    # Above EMA21?
    ema21 = stock_series.ewm(span=21).mean()
    above_ema = stock_series.iloc[-1] > ema21.iloc[-1]
    
    stock_rows.append({
        "Ticker": stock,
        "RS vs XJO": round(rs_stock,2),
        "3M %": round(perf_3m,2),
        "Above 21 EMA": "✅" if above_ema else "❌"
    })

if stock_rows:
    stock_df = pd.DataFrame(stock_rows).sort_values("RS vs XJO", ascending=False)
    st.dataframe(stock_df, use_container_width=True)
else:
    st.write("No stock data available.")