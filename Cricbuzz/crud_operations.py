import streamlit as st
import pandas as pd
import sys
import os
import traceback
import numpy as np

# Add utils path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.db_connection import get_db_connection


def run():
    st.title("Team CRUD Operations")
    st.markdown("---")

    conn = None
    try:
        conn = get_db_connection()
        st.success("Successfully connected to the database!")
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        st.warning("Please check your database credentials and connection.")
        st.stop()

    # ------------------------------
    # Helper functions
    # ------------------------------
    def get_teams(conn):
        try:
            query = "SELECT team_id, team_name, team_sname FROM teams"
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"Error fetching teams: {e}")
            return pd.DataFrame()

    def get_deletable_teams(conn):
        try:
            query = """
            SELECT DISTINCT t.team_id, t.team_name, t.team_sname
            FROM teams t
            WHERE t.team_id NOT IN (
                SELECT DISTINCT team1_id FROM matches WHERE team1_id IS NOT NULL
                UNION
                SELECT DISTINCT team2_id FROM matches WHERE team2_id IS NOT NULL
            )
            """
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"Error fetching deletable teams: {e}")
            return pd.DataFrame()

    def add_team(conn, team_name, team_sname):
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(team_id) FROM teams")
            result = cursor.fetchone()
            next_id = (result[0] + 1) if result[0] is not None else 1

            query = "INSERT INTO teams (team_id, team_name, team_sname) VALUES (%s, %s, %s)"
            cursor.execute(query, (next_id, team_name, team_sname))
            conn.commit()
            cursor.close()
            st.success(f"✅ Successfully added team: {team_name} (ID: {next_id})")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Error adding team: {e}")
            conn.rollback()

    def update_team(conn, team_id, team_name, team_sname):
        try:
            cursor = conn.cursor()
            query = "UPDATE teams SET team_name = %s, team_sname = %s WHERE team_id = %s"
            team_id = int(team_id)
            cursor.execute(query, (team_name, team_sname, team_id))
            conn.commit()
            cursor.close()
            st.success(f"✅ Successfully updated team: {team_name} (ID: {team_id})")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Error updating team: {e}")
            conn.rollback()

    def delete_team(conn, team_id):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                  (SELECT COUNT(*) FROM matches WHERE team1_id = %s OR team2_id = %s) AS matches_count,
                  (SELECT COUNT(*) FROM players WHERE team_id = %s) AS players_count
            """, (team_id, team_id, team_id))
            counts = cursor.fetchone()

            if counts and (counts[0] > 0 or counts[1] > 0):
                st.error("❌ Cannot delete — team is still referenced in other tables.")
                cursor.close()
                return

            cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
            conn.commit()
            deleted = cursor.rowcount
            cursor.close()

            if deleted and deleted > 0:
                st.success(f"✅ Team (ID: {team_id}) deleted successfully.")
                st.experimental_rerun()
            else:
                st.error("Delete did not remove any row (maybe ID mismatch).")
        except Exception as e:
            st.error(f"Error deleting team: {e}")
            st.text(traceback.format_exc())
            conn.rollback()

    # ------------------------------
    # Show current teams
    # ------------------------------
    st.header("Current Teams")
    teams_df = get_teams(conn)
    if not teams_df.empty:
        st.dataframe(teams_df)
    else:
        st.warning("No teams found. Please add a new team below.")
    st.markdown("---")

    # ------------------------------
    # Add new team
    # ------------------------------
    st.header("Add New Team")
    with st.form("add_team_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            team_name = st.text_input("Team Full Name", max_chars=255)
        with col2:
            team_sname = st.text_input("Team Short Name (e.g., IND)", max_chars=10)

        submitted = st.form_submit_button("Add Team", type="primary")
        if submitted:
            if team_name and team_sname:
                add_team(conn, team_name, team_sname)
            else:
                st.warning("⚠️ Team Full Name and Short Name are required.")
    st.markdown("---")

    # ------------------------------
    # Update team
    # ------------------------------
    st.header("Update Team")
    if not teams_df.empty:
        team_selection = st.selectbox("Select Team to Update", teams_df['team_name'].tolist(), key='update_select')
        selected_team = teams_df[teams_df['team_name'] == team_selection].iloc[0]

        with st.form("update_team_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_team_name = st.text_input("New Full Name", value=selected_team['team_name'])
            with col2:
                new_team_sname = st.text_input("New Short Name", value=selected_team['team_sname'])

            update_submitted = st.form_submit_button("Update Team", type="primary")
            if update_submitted:
                team_id = int(selected_team['team_id'])
                update_team(conn, team_id, new_team_name, new_team_sname)
    else:
        st.info("No teams to update.")
    st.markdown("---")

         # --- Delete Team ---
    st.header("Delete Team")

    deletable_teams_df = get_deletable_teams(conn)

    if deletable_teams_df.empty:
        st.info("No teams are safe to delete. All teams are referenced in other tables.")
    else:
        st.subheader("Teams that can be deleted")
        st.dataframe(deletable_teams_df.reset_index(drop=True))

        with st.form("delete_team_form"):
            chosen_name = st.selectbox(
                "Choose team to delete",
                options=deletable_teams_df["team_name"].tolist()
            )
            chosen_row = deletable_teams_df[deletable_teams_df["team_name"] == chosen_name].iloc[0]
            team_id = int(chosen_row["team_id"])

            st.write("Selected team details:", chosen_row.to_dict())

            confirm = st.checkbox(f"I confirm I want to delete '{chosen_name}' (ID: {team_id})")
            submitted = st.form_submit_button("Delete team")

            if submitted:
                if not confirm:
                    st.session_state["delete_msg"] = ("warning", "Please tick the confirmation box before deleting.")
                else:
                    try:
                        cursor = conn.cursor()

                        # check references again (extra safety)
                        cursor.execute("""
                            SELECT
                              (SELECT COUNT(*) FROM matches WHERE team1_id = %s OR team2_id = %s) AS matches_count,
                              (SELECT COUNT(*) FROM players WHERE team_id = %s) AS players_count
                        """, (team_id, team_id, team_id))
                        counts = cursor.fetchone()

                        if counts and (counts[0] > 0 or counts[1] > 0):
                            st.session_state["delete_msg"] = ("error", "❌ Cannot delete — team is still linked in matches/players.")
                        else:
                            cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
                            conn.commit()
                            deleted = cursor.rowcount
                            cursor.close()

                            if deleted > 0:
                                st.session_state["delete_msg"] = ("success", f"✅ Team (ID: {team_id}) deleted successfully.")
                            else:
                                st.session_state["delete_msg"] = ("error", "⚠️ Delete query ran but no rows were removed. ID mismatch?")
                    except Exception as e:
                        st.session_state["delete_msg"] = ("error", f"Error during delete: {e}")
                        conn.rollback()

    # 🔔 Show delete result message (after form submit)
    if "delete_msg" in st.session_state:
        level, msg = st.session_state["delete_msg"]
        if level == "success":
            st.success(msg)
        elif level == "error":
            st.error(msg)
        elif level == "warning":
            st.warning(msg)


if __name__ == "__main__":
    run()
