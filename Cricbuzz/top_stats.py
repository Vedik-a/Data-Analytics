import streamlit as st
import pandas as pd
from utils.db_connection import get_db_connection, close_db_connection

def run():
    st.title("Top Player Statistics")
    st.markdown("### Batting and Bowling Leaders")

    # Tabs for different stats
    tab1, tab2 = st.tabs(["Top Batsmen", "Top Bowlers"])

    connection = get_db_connection()
    if not connection:
        st.error("Failed to connect to the database. Please check your connection settings.")
        return

    try:
        with tab1:
            st.header("Top Batsmen")
            st.markdown("---")
            # Query to find top batsmen (Note: The batting_stats table must be created and populated)
            batting_query = """
                SELECT
                    p.full_name AS player_name,
                    bs.total_runs,
                    bs.total_matches,
                    bs.batting_average,
                    bs.highest_score
                FROM
                    players p
                JOIN
                    batting_stats bs ON p.player_id = bs.player_id
                ORDER BY
                    bs.total_runs DESC
                LIMIT 10;
            """
            batting_df = pd.read_sql(batting_query, connection)

            if batting_df.empty:
                st.info("No batting stats available. Please ensure the 'batting_stats' table exists and is populated.")
            else:
                st.dataframe(batting_df, use_container_width=True)

        with tab2:
            st.header("Top Bowlers")
            st.markdown("---")
            st.info("This section requires a 'bowling_stats' table to be populated.")
            # Placeholder for bowling stats query (you will need to create and populate the table)
            st.write("Coming Soon...")
            
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
    finally:
        close_db_connection(connection)
