import streamlit as st
from pages import home, live_matches, sql_queries, crud_operations

# App Config
st.set_page_config(
    page_title="Cricbuzz LiveStats",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sidebar Navigation
st.sidebar.title("Cricbuzz LiveStats")

page = st.sidebar.selectbox(
    "Choose a page",
    ["Dashboard", "Live Matches", "SQL Queries", "CRUD Operations"]
)

# Page Mapping
pages_map = {
    "Dashboard": home,
    "Live Matches": live_matches,
    "SQL Queries": sql_queries,
    "CRUD Operations": crud_operations,
}

# Run Selected Page
if page in pages_map:
    pages_map[page].run()
