import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from crypto_indicators import fetch_ohlcv, compute_sma, compute_pct_change
st.set_page_config(page_title="Crypto SMA Dashboard", layout="wide")
from streamlit_autorefresh import st_autorefresh


# Centered title
st.markdown("<h1 style='text-align: center;'>📊 Crypto OHLCV + SMA Dashboard</h1>", unsafe_allow_html=True)

# Auto-refresh every 60 seconds


st_autorefresh(interval=60 * 1000, key="refresh")


# -------------------- PAIRS LIST --------------------
if "pairs" not in st.session_state:
    st.session_state.pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT"]

# Sidebar
st.sidebar.header("Settings")

# Dropdown with "Custom" option
pair_selection = st.sidebar.selectbox("Select Trading Pair", st.session_state.pairs + ["Custom"])

if pair_selection == "Custom":
    custom_pair = st.sidebar.text_input("Enter Custom Pair (e.g. DOGEUSDT)").upper()
    if custom_pair:
        if custom_pair not in st.session_state.pairs:
            st.session_state.pairs.append(custom_pair)
        symbol = custom_pair
    else:
        st.warning("Please enter a custom trading pair.")
        st.stop()
else:
    symbol = pair_selection

window = st.sidebar.slider("SMA Window", min_value=5, max_value=50, value=10)

try:
    data = fetch_ohlcv(symbol)
    if not data:  # Binance returned nothing
        st.error(f"❌ Currency pair '{symbol}' not found.")
        st.stop()

    # ✅ Only save the pair if it’s valid
    if symbol not in st.session_state.pairs:
        st.session_state.pairs.append(symbol)

    sma = compute_sma(data, window=window)
    pct = compute_pct_change(data)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["sma"] = sma

    if len(df) > 60:
        df = df.tail(60)

    # -------------------- DASHBOARD --------------------
    #controls
    colA, colB = st.columns([2, 1])




    
    # Show metrics
    col4, col5, col6 = st.columns(3)
    col6.metric("Percent Change", f"{pct:.2f}%", f"{pct:.2f}%")
    col4.metric("High", f"{df['high'].max():.2f}")
    col5.metric("Low", f"{df['low'].min():.2f}")

    # Build candlestick + SMA chart
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="OHLC"
    )])

    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["sma"],
        mode="lines",
        name=f"SMA-{window}",
        line=dict(color="orange")
    ))

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        title=f"{symbol.upper()} OHLCV with SMA-{window}",
        yaxis_title="Price"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show table
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error fetching data for {symbol}: {e}")