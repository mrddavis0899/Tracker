import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Constants
CSV_FILE = "bet_history.csv"
STARTING_BANKROLL = 83.0  # Initial bankroll

# Load or create data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["Date", "Event", "Bet Type", "Amount", "Result", "Payout"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# 🎨 Inject custom Gators theme
def gators_style():
    st.markdown("""
        <style>
        body {
            background-image: url("https://upload.wikimedia.org/wikipedia/commons/4/44/Florida_Gators_logo.svg");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: top right;
        }
        .main {
            background-color: rgba(255, 255, 255, 0.90);
            padding: 2rem;
            border-radius: 1rem;
        }
        h1, h2, h3 {
            color: #0021A5; /* Gators blue */
        }
        .stButton button {
            background-color: #FA4616 !important; /* Gators orange */
            color: white !important;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

# Run the app
st.set_page_config(page_title="Fanduel Tracker", layout="centered")
gators_style()
st.title("🐊 Fanduel Tracker")

# Tabs
tab1, tab2 = st.tabs(["➕ Add Bet", "📊 View History"])

with tab1:
    st.subheader("Add a New Bet")

    date = st.date_input("Date", value=datetime.today())
    event = st.text_input("Event (e.g. Gators vs FSU)")
    bet_type = st.text_input("Bet Type (e.g. Spread, Total, Moneyline)")
    amount = st.number_input("Amount Bet ($)", min_value=0.0, step=1.0)
    result = st.selectbox("Result", ["Pending", "Won", "Lost"])

    payout = 0.0
    if result == "Won":
        payout = st.number_input("Payout Received ($)", min_value=0.0, step=1.0)
    elif result == "Lost":
        payout = 0.0
    else:
        payout = ""

    if st.button("💾 Submit Bet"):
        new_data = {
            "Date": date.strftime("%Y-%m-%d"),
            "Event": event,
            "Bet Type": bet_type,
            "Amount": amount,
            "Result": result,
            "Payout": payout
        }

        df = load_data()
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        save_data(df)
        st.success("Bet added!")

with tab2:
    st.subheader("Your Bet History")

    df = load_data()

    # Make sure Amount and Payout are numeric
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Payout"] = pd.to_numeric(df["Payout"], errors="coerce").fillna(0)

    status_filter = st.multiselect("Filter by Result", options=["Pending", "Won", "Lost"], default=["Pending", "Won", "Lost"])
    filtered_df = df[df["Result"].isin(status_filter)]

    st.dataframe(filtered_df, use_container_width=True)

    # Filter to only completed bets
    completed_bets = df[df["Result"].isin(["Won", "Lost"])]

    total_in = completed_bets["Payout"].sum()
    total_out = completed_bets["Amount"].sum()
    net_profit = total_in - total_out
    current_bankroll = STARTING_BANKROLL + net_profit
    roi = (net_profit / total_out * 100) if total_out > 0 else 0.0

    st.markdown(f"💰 **Money In (Winnings):** ${total_in:,.2f}")
    st.markdown(f"📤 **Money Out (All Bets):** ${total_out:,.2f}")
    st.markdown(f"📈 **Net Profit/Loss:** ${net_profit:,.2f}")
    st.markdown(f"🏦 **Current Bankroll:** ${current_bankroll:,.2f} (Starting: ${STARTING_BANKROLL})")
    st.markdown(f"📊 **ROI:** {roi:.2f}%")
