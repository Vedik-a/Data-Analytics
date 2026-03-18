import streamlit as st
import pandas as pd
from utils.db_connection import get_db_connection, close_db_connection

def run():
    st.title("SQL Queries & Analytics")
    st.markdown("### Run predefined SQL queries on the cricket database")
    st.info("Select a query from the dropdown to see the results.")

    SQL_QUERIES = {
        "Query 1: Find all teams from India": "SELECT team_name, team_sname FROM teams WHERE team_name = 'India' OR team_sname = 'IND';",
        "Query 2: Matches played in the last 30 days": "SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2, m.series_name, FROM_UNIXTIME(m.start_date/1000) AS start_date FROM matches m JOIN teams t1 ON m.team1_id = t1.team_id JOIN teams t2 ON m.team2_id = t2.team_id WHERE FROM_UNIXTIME(m.start_date/1000) >= (CURRENT_DATE - INTERVAL 30 DAY) ORDER BY start_date DESC;",
        "Query 3: Top 10 teams with most wins": "SELECT t.team_name, COUNT(*) AS wins FROM matches m JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%') WHERE m.status LIKE '%won%' GROUP BY t.team_name ORDER BY wins DESC LIMIT 10;",
        "Query 4: Venues with more than 10 matches": "SELECT venue, COUNT(*) AS matches_played FROM matches GROUP BY venue HAVING COUNT(*) > 10 ORDER BY matches_played DESC;",
        "Query 5: Matches won by each team": "SELECT t.team_name, COUNT(*) AS wins FROM matches m JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%') WHERE m.status LIKE '%won%' GROUP BY t.team_name ORDER BY wins DESC;",
        "Query 6: Matches played by each team": "SELECT t.team_name, COUNT(*) AS matches_played FROM teams t JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id) GROUP BY t.team_name ORDER BY matches_played DESC;",
        "Query 7: Longest win descriptions (approx 'largest victory margin')": "SELECT status FROM matches WHERE status LIKE '%won by%' ORDER BY LENGTH(status) DESC LIMIT 3;",
        "Query 8: Matches in 2024": "SELECT match_desc, series_name, match_format, FROM_UNIXTIME(start_date/1000) AS start_time FROM matches WHERE YEAR(FROM_UNIXTIME(start_date/1000)) = 2024;",
        "Query 9: Teams with more than 20 wins": "SELECT t.team_name, COUNT(*) AS wins FROM matches m JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%') WHERE m.status LIKE '%won%' GROUP BY t.team_name HAVING COUNT(*) > 20 ORDER BY wins DESC;",
        "Query 10: Last 20 completed matches": "SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2, m.status, m.series_name FROM matches m JOIN teams t1 ON m.team1_id = t1.team_id JOIN teams t2 ON m.team2_id = t2.team_id WHERE m.state = 'Complete' ORDER BY m.start_date DESC LIMIT 20;",
        "Query 11: Wins split by match format": "SELECT match_format, t.team_name, COUNT(*) AS wins FROM matches m JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%') WHERE m.status LIKE '%won%' GROUP BY match_format, t.team_name ORDER BY match_format, wins DESC;",
        "Query 12: Home vs Away (approx: if series_name contains team name = home)": "SELECT t.team_name, SUM(CASE WHEN m.series_name LIKE CONCAT('%', t.team_name, '%') AND m.status LIKE CONCAT(t.team_name, '%') THEN 1 ELSE 0 END) AS home_wins, SUM(CASE WHEN m.series_name NOT LIKE CONCAT('%', t.team_name, '%') AND m.status LIKE CONCAT(t.team_name, '%') THEN 1 ELSE 0 END) AS away_wins FROM teams t JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id) GROUP BY t.team_name;",
        "Query 13: Team’s biggest win (status with max length)": "SELECT t.team_name, m.status FROM matches m JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%') WHERE m.status LIKE '%won%' ORDER BY LENGTH(m.status) DESC LIMIT 10;",
        "Query 14: Most common formats": "SELECT match_format, COUNT(*) AS matches FROM matches GROUP BY match_format ORDER BY matches DESC;",
        "Query 15: Close wins (margin in status < 50 runs OR < 5 wickets)": "SELECT t.team_name, COUNT(*) AS close_wins FROM matches m JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%') WHERE (m.status LIKE '%won by % run%' AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' run', 1) AS UNSIGNED) < 50) OR (m.status LIKE '%won by % wkt%' AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' wkt', 1) AS UNSIGNED) < 5) GROUP BY t.team_name ORDER BY close_wins DESC;",
        "Query 16: Matches per year": "SELECT YEAR(FROM_UNIXTIME(start_date/1000)) AS year, COUNT(*) AS matches FROM matches GROUP BY year ORDER BY year;",
        "Query 17: Toss winning advantage analysis": "SELECT toss_winner_decision, COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS win_percentage FROM matches WHERE toss_winner_id = winner_id GROUP BY toss_winner_decision;",
        "Query 18: Most economical bowlers": "SELECT p.full_name, AVG(bs.economy_rate) AS avg_economy FROM players p JOIN bowling_stats bs ON p.player_id = bs.player_id WHERE bs.match_format IN ('ODI', 'T20I') GROUP BY p.full_name HAVING COUNT(bs.match_id) >= 10;",
        "Query 19: Most consistent batsmen": "SELECT p.full_name, AVG(ps.runs_scored) AS avg_runs, STDDEV(ps.runs_scored) AS stdev_runs FROM players p JOIN player_stats ps ON p.player_id = ps.player_id WHERE ps.balls_faced >= 10 AND YEAR(ps.match_date) >= 2022 GROUP BY p.full_name ORDER BY stdev_runs ASC;",
        "Query 20: Player matches and average by format": "SELECT p.full_name, SUM(CASE WHEN m.match_format = 'Test' THEN 1 ELSE 0 END) AS test_matches, AVG(CASE WHEN m.match_format = 'Test' THEN ps.batting_average ELSE NULL END) AS test_avg, SUM(CASE WHEN m.match_format = 'ODI' THEN 1 ELSE 0 END) AS odi_matches, AVG(CASE WHEN m.match_format = 'ODI' THEN ps.batting_average ELSE NULL END) AS odi_avg, SUM(CASE WHEN m.match_format = 'T20I' THEN 1 ELSE 0 END) AS t20i_matches, AVG(CASE WHEN m.match_format = 'T20I' THEN ps.batting_average ELSE NULL END) AS t20i_avg FROM players p JOIN player_stats ps ON p.player_id = ps.player_id JOIN matches m ON ps.match_id = m.match_id GROUP BY p.full_name HAVING COUNT(*) >= 20;",
        "Query 21: Team performance score (wins * 2 + matches)": "SELECT t.team_name, (SUM(CASE WHEN m.status LIKE CONCAT(t.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) * 2) + COUNT(*) AS perf_score FROM teams t JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id) GROUP BY t.team_name ORDER BY perf_score DESC;",
        "Query 22: Head-to-head match prediction": "SELECT LEAST(t1.team_name, t2.team_name) AS teamA, GREATEST(t1.team_name, t2.team_name) AS teamB, COUNT(*) AS total_matches, SUM(CASE WHEN m.status LIKE CONCAT(t1.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) AS teamA_wins, SUM(CASE WHEN m.status LIKE CONCAT(t2.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) AS teamB_wins FROM matches m JOIN teams t1 ON m.team1_id = t1.team_id JOIN teams t2 ON m.team2_id = t2.team_id GROUP BY teamA, teamB HAVING COUNT(*) >= 5;",
        "Query 23: Recent player form and momentum": "SELECT p.full_name, AVG(ps.runs_scored) AS last_5_avg_runs, AVG(ps.strike_rate) AS last_5_avg_sr FROM players p JOIN player_stats ps ON p.player_id = ps.player_id WHERE ps.match_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH) GROUP BY p.full_name;",
        "Query 24: Successful batting partnerships": "SELECT p1.full_name AS player1, p2.full_name AS player2, AVG(pa.runs) AS avg_partnership_runs, COUNT(CASE WHEN pa.runs > 50 THEN 1 ELSE NULL END) AS count_50_plus_partnerships FROM partnerships pa JOIN players p1 ON pa.batsman1_id = p1.player_id JOIN players p2 ON pa.batsman2_id = p2.player_id GROUP BY p1.full_name, p2.full_name HAVING COUNT(*) >= 5 ORDER BY avg_partnership_runs DESC;",
        "Query 25: Time-series analysis of player performance": "SELECT p.full_name, YEAR(m.start_date) AS match_year, QUARTER(m.start_date) AS match_quarter, AVG(ps.runs_scored) AS avg_runs, AVG(ps.strike_rate) AS avg_sr FROM players p JOIN player_stats ps ON p.player_id = ps.player_id JOIN matches m ON ps.match_id = m.match_id GROUP BY p.full_name, match_year, match_quarter HAVING COUNT(ps.match_id) >= 3;",
    }

    selected_query_name = st.selectbox(
        "Select a query to run:",
        list(SQL_QUERIES.keys())
    )

    if selected_query_name:
        st.markdown(f"**Executing Query:** `{SQL_QUERIES[selected_query_name]}`")

        connection = get_db_connection()
        if connection:
            try:
                df = pd.read_sql(SQL_QUERIES[selected_query_name], connection)

                if df.empty:
                    st.info("The query returned no results. This may be because the required data or tables are not yet populated.")
                else:
                    st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred while executing the query: {e}")
                st.markdown("Please ensure the required tables (`players`, `batting_stats`, `bowling_stats`, etc.) and columns are created in your MySQL database and populated with data.")
            finally:
                close_db_connection(connection)
        else:
            st.error("Failed to establish a database connection.")
