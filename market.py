import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

st.set_page_config(page_title="Nigeria Market Price Tracker", page_icon="📈")

st.title("📈 Nigeria Market Price Tracker")
st.markdown("Track commodity prices across Nigerian markets")

# ===== CONNECT TO GOOGLE SHEETS =====
def connect_to_sheet():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Nigeria Market Prices").sheet1
        return sheet
    except Exception as e:
        st.error("❌ Connection failed. Check your internet and try again.")
        st.stop()
sheet = connect_to_sheet()

# ===== LOAD DATA =====
def load_data():
    records = sheet.get_all_records()
    return pd.DataFrame(records)

# ===== INPUT SECTION =====
st.subheader("➕ Add Today's Price")

COMMODITIES = [
    "Maize", "Rice", "Tomato", "Onion", "Pepper",
    "Groundnut", "Cowpea", "Yam", "Cassava", "Sorghum",
    "Millet", "Soybean", "Wheat", "Plantain", "Watermelon"
]

LOCATIONS = [
    "Dutse", "Kano", "Lagos", "Abuja", "Kaduna",
    "Maiduguri", "Sokoto", "Jos", "Ibadan", "Katsina",
    "Hadejia", "Zaria", "Port Harcourt", "Enugu", "Damaturu"
]

col1, col2, col3, col4 = st.columns(4)
with col1:
    entry_date = st.date_input("Date", value=date.today())
with col2:
    commodity = st.selectbox("Commodity", COMMODITIES)
with col3:
    location = st.selectbox("Location", LOCATIONS)
with col4:
    price = st.number_input("Price (₦/kg)", min_value=0, value=0, step=10)

if st.button("➕ Add Price"):
    if price > 0:
        sheet.append_row([str(entry_date), commodity, location, price])
        st.success(f"✅ Saved: {commodity} in {location} — ₦{price}/kg")
        st.rerun()
    else:
        st.warning("Enter a price greater than 0.")

# ===== SHOW DATA =====
st.divider()
df = load_data()

if not df.empty:
    st.subheader("📊 Price Records")
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("📈 Price Trend")

    selected = st.selectbox("Select commodity to view trend", df["Commodity"].unique())
    filtered = df[df["Commodity"] == selected]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(filtered["Date"], filtered["Price (₦/kg)"], marker="o", color="#FF6B35")
    ax.set_title(f"{selected} Price Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (₦/kg)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No data yet. Add your first price above!")