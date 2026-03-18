import streamlit as st

def run():
    st.title("Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics")
    st.markdown("---")

    st.header("Project Overview")
    st.markdown("""
        This project is a comprehensive cricket analytics dashboard built using **Streamlit** and a **MySQL** database.
        It allows you to get real-time match updates, analyze detailed player statistics, and run SQL-driven queries
        to practice your data analytics skills.
    """)

    st.subheader("Key Features")
    st.markdown("""
        - **Live Match Scorecard:** Get real-time updates for ongoing matches.
        - **Player Analytics:** View top player statistics for batting and bowling.
        - **SQL & Analytics:** Run predefined SQL queries to analyze the data.
        - **CRUD Operations:** Perform Create, Read, Update, and Delete operations on player data.
    """)

    st.subheader("Technical Stack")
    st.markdown("""
        - **Frontend:** Streamlit for a fast and interactive web application.
        - **Backend:** MySQL for relational database management.
        - **Data Source:** A custom data ingestion script that fetches data from the Cricbuzz API.
        - **Libraries:** pandas, mysql-connector-python, requests.
    """)
