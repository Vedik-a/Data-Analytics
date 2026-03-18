import streamlit as st
import pandas as pd
from utils.db_connection import get_db_connection, close_db_connection

def run():
    st.title("Live Match Scorecard")
    st.markdown("### Real-time updates from ongoing matches")

    # Connect to the database
    connection = get_db_connection()
    if not connection:
        st.error("Failed to connect to the database. Please check your connection settings.")
        return

    try:
        # SQL query to fetch live match data. Removed the venue column as it doesn't exist.
        query = """
        SELECT
            m.match_desc,
            m.match_format,
            m.status,
            t1.team_name AS team1,
            t2.team_name AS team2
        FROM
            matches m
        JOIN
            teams t1 ON m.team1_id = t1.team_id
        JOIN
            teams t2 ON m.team2_id = t2.team_id
        WHERE
            m.state = 'Live'
        ORDER BY
            m.start_date DESC;
        """
        
        # Read the query results into a pandas DataFrame
        df = pd.read_sql(query, connection)

        if df.empty:
            st.info("No live matches are currently available.")
        else:
            # Display each live match in a card-like format
            for index, row in df.iterrows():
                with st.expander(f"**{row['team1']} vs {row['team2']}** - {row['match_format']}"):
                    st.write(f"**Match Description:** {row['match_desc']}")
                    st.write(f"**Status:** {row['status']}")

    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
    finally:
        close_db_connection(connection)
