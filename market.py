import streamlit as st
import pandas as pd
import plotly.express as px
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
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
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
    st.divider()
    st.subheader("📊 Market Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        most_expensive = df.loc[df["Price (₦/kg)"].idxmax()]
        st.metric("💰 Most Expensive", most_expensive["Commodity"], f"₦{most_expensive['Price (₦/kg)']}/kg")
    
    with col2:
        cheapest = df.loc[df["Price (₦/kg)"].idxmin()]
        st.metric("🟢 Cheapest Right Now", cheapest["Commodity"], f"₦{cheapest['Price (₦/kg)']}/kg")
    
    with col3:
        most_active = df["Location"].value_counts().idxmax()
        st.metric("📍 Most Active Market", most_active, f"{df['Location'].value_counts().max()} entries")
if not df.empty:
    st.subheader("📊 Price Records")
    st.dataframe(df, use_container_width=True)

    st.divider()
    st.subheader("🏷️ Latest Prices")

    latest = df.sort_values("Date", ascending=False).drop_duplicates(subset=["Commodity", "Location"])
    latest = latest.sort_values("Commodity")
    st.dataframe(latest[["Commodity", "Location", "Price (₦/kg)", "Date"]], use_container_width=True)

    st.divider()
    st.subheader("📈 Price Trend")

    selected = st.multiselect("Select commodities to compare", df["Commodity"].unique(), default=[df["Commodity"].unique()[0]])
    filtered = df[df["Commodity"].isin(selected)]
    
    fig = px.line(filtered, x="Date", y="Price (₦/kg)", 
                title=f"{selected} Price Trend",
                markers=True,
                color="Commodity",
                hover_data={"Location": True, "Price (₦/kg)": True, "Date": True})
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data yet. Add your first price above!")