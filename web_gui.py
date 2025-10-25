import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "restaurant_order_recommender.db"

# Page Config
st.set_page_config(page_title="Restaurant Recommender", layout="centered")

st.title("Restaurant Recommender System")
st.markdown("Use DoorDash-like historical data to find the best restaurants for your preferences.")

# User Inputs
st.sidebar.header("Filter Options")

# Cuisine Type
cuisine = st.sidebar.selectbox(
    "Select Cuisine Type",
    ["all", "american", "mexican", "asian", "italian", "indian"]
)

# Market / Region Filter
market = st.sidebar.number_input("Market ID (optional)", min_value=0, step=1, value=0)

# Preference Type
preference = st.sidebar.selectbox(
    "Select Preference",
    ["Fast Delivery", "High Value", "Most Popular"]
)

# Number of Results
limit = st.sidebar.slider("Number of Recommendations", 5, 20, 10)

# Query Based on Preference
query = ""
if preference == "Fast Delivery":
    query = f"""
        SELECT r.restaurant_id, r.cuisine_type,
               AVG((julianday(o.delivery_time) - julianday(o.order_datetime)) * 24 * 60) AS avg_delivery_min
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        WHERE o.delivery_time IS NOT NULL
        {"AND r.cuisine_type = '" + cuisine + "'" if cuisine != "all" else ""}
        {"AND r.location = " + str(market) if market > 0 else ""}
        GROUP BY r.restaurant_id
        HAVING COUNT(o.order_id) > 20
        ORDER BY avg_delivery_min ASC
        LIMIT {limit};
    """

elif preference == "High Value":
    query = f"""
        SELECT r.restaurant_id, r.cuisine_type,
               AVG(o.subtotal / NULLIF(o.total_items, 0)) AS avg_item_value
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        {"WHERE r.cuisine_type = '" + cuisine + "'" if cuisine != "all" else ""}
        {"AND r.location = " + str(market) if market > 0 else ""}
        GROUP BY r.restaurant_id
        HAVING COUNT(o.order_id) > 20
        ORDER BY avg_item_value DESC
        LIMIT {limit};
    """

elif preference == "Most Popular":
    query = f"""
        SELECT r.restaurant_id, r.cuisine_type, COUNT(o.order_id) AS total_orders
        FROM restaurants r
        JOIN orders o ON r.restaurant_id = o.restaurant_id
        {"WHERE r.cuisine_type = '" + cuisine + "'" if cuisine != "all" else ""}
        {"AND r.location = " + str(market) if market > 0 else ""}
        GROUP BY r.restaurant_id
        ORDER BY total_orders DESC
        LIMIT {limit};
    """

# Display Query Preview
st.markdown("### SQL Query Preview")
st.code(query, language="sql")

# Run Query
if st.button("Get Recommendations"):
    if query.strip():
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            st.warning("No matching restaurants found for your filters.")
        else:
            st.success("Here are your top recommendations:")
            st.dataframe(df)
    else:
        st.warning("Please select a valid preference to build a query.")
