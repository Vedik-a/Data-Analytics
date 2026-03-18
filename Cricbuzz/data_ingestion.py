import os
import requests
from mysql.connector import Error
from utils.db_connection import get_db_connection, close_db_connection

# ==============================
# API CONFIG
# ==============================
API_URL = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
API_KEY = os.getenv("API_KEY", "6d428efe4dmsh504130c95f21571p16cff7jsn2f4557000eae")
API_HOST = "cricbuzz-cricket.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# ==============================
# API HELPERS
# ==============================
def fetch_live_matches():
    """Fetch live/recent matches."""
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching matches: {e}")
        return None


def fetch_team_players(team_id):
    """Fetch all players for a team."""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/team/v1/{team_id}/players"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching players for team {team_id}: {e}")
        return None


def fetch_player_details(player_id):
    """Fetch player details by player_id."""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching player {player_id}: {e}")
        return None


def fetch_batting_stats(player_id):
    """Fetch batting stats for a player."""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching batting stats for {player_id}: {e}")
        return None


def fetch_bowling_stats(player_id):
    """Fetch bowling stats for a player."""
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching bowling stats for {player_id}: {e}")
        return None

# ==============================
# DB INSERT HELPERS
# ==============================
def insert_team_and_match_data(api_response, connection):
    """Insert teams & matches into DB."""
    cursor = connection.cursor()
    try:
        all_teams = {}
        all_matches = []

        for match_type_data in api_response.get("typeMatches", []):
            for series_data in match_type_data.get("seriesMatches", []):
                series_ad_wrapper = series_data.get("seriesAdWrapper", {})
                series_name = series_ad_wrapper.get("seriesName")
                series_id = series_ad_wrapper.get("seriesId")

                for match in series_ad_wrapper.get("matches", []):
                    match_info = match.get("matchInfo", {})
                    team1_info = match_info.get("team1", {})
                    team2_info = match_info.get("team2", {})

                    if team1_info:
                        all_teams[team1_info['teamId']] = (
                            team1_info['teamId'],
                            team1_info['teamName'],
                            team1_info['teamSName']
                        )
                    if team2_info:
                        all_teams[team2_info['teamId']] = (
                            team2_info['teamId'],
                            team2_info['teamName'],
                            team2_info['teamSName']
                        )

                    match_values = (
                        match_info.get("matchId"),
                        series_id,
                        series_name,
                        match_info.get("matchDesc"),
                        match_info.get("matchFormat"),
                        match_info.get("startDate"),
                        match_info.get("endDate"),
                        match_info.get("state"),
                        match_info.get("status"),
                        team1_info.get("teamId"),
                        team2_info.get("teamId"),
                    )
                    all_matches.append(match_values)

        if all_teams:
            cursor.executemany(
                """INSERT INTO teams (team_id, team_name, team_sname)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE team_name=VALUES(team_name), team_sname=VALUES(team_sname);""",
                list(all_teams.values())
            )
            print(f"Inserted/updated {len(all_teams)} teams.")

        if all_matches:
            cursor.executemany(
                """INSERT INTO matches
                   (match_id, series_id, series_name, match_desc, match_format, start_date, end_date, state, status, team1_id, team2_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE status=VALUES(status), state=VALUES(state);""",
                all_matches
            )
            print(f"Inserted/updated {len(all_matches)} matches.")

        connection.commit()
    except Error as e:
        print(f"Error inserting teams/matches: {e}")
        connection.rollback()


def insert_player_data(player_data, connection):
    """Insert player details into DB."""
    if not player_data:
        return

    cursor = connection.cursor()
    try:
        player_id = str(player_data.get("id"))
        full_name = player_data.get("name", "")
        playing_role = player_data.get("role", "")
        batting_style = player_data.get("battingStyle", "")
        bowling_style = player_data.get("bowlingStyle", "")
        nationality = player_data.get("country", "")

        cursor.execute(
            """INSERT INTO players (player_id, full_name, playing_role, batting_style, bowling_style, nationality)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE full_name=VALUES(full_name),
                                       playing_role=VALUES(playing_role),
                                       batting_style=VALUES(batting_style),
                                       bowling_style=VALUES(bowling_style),
                                       nationality=VALUES(nationality);""",
            (player_id, full_name, playing_role, batting_style, bowling_style, nationality),
        )
        connection.commit()
        print(f"Inserted/updated player: {full_name}")
    except Exception as e:
        print(f"Error inserting player {player_data.get('name')}: {e}")


def insert_batting_stats(player_id, batting_data, connection):
    """Insert batting stats for a player."""
    if not batting_data:
        return
    cursor = connection.cursor()
    try:
        stats = batting_data.get("stats", [])
        if stats:
            odi_stats = next((s for s in stats if s["matchType"] == "odi"), None)
            if odi_stats:
                cursor.execute(
                    """INSERT INTO batting_stats (player_id, total_runs, total_matches, batting_average, highest_score)
                       VALUES (%s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE total_runs=VALUES(total_runs),
                                               total_matches=VALUES(total_matches),
                                               batting_average=VALUES(batting_average),
                                               highest_score=VALUES(highest_score);""",
                    (
                        player_id,
                        odi_stats.get("runs", 0),
                        odi_stats.get("matches", 0),
                        odi_stats.get("average", 0.0),
                        odi_stats.get("hs", ""),
                    ),
                )
                connection.commit()
                print(f"Inserted batting stats for {player_id}")
    except Exception as e:
        print(f"Error inserting batting stats for {player_id}: {e}")


def insert_bowling_stats(player_id, bowling_data, connection):
    """Insert bowling stats for a player."""
    if not bowling_data:
        return
    cursor = connection.cursor()
    try:
        stats = bowling_data.get("stats", [])
        if stats:
            odi_stats = next((s for s in stats if s["matchType"] == "odi"), None)
            if odi_stats:
                cursor.execute(
                    """INSERT INTO bowling_stats (player_id, total_wickets, total_matches, bowling_average, best_figures)
                       VALUES (%s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE total_wickets=VALUES(total_wickets),
                                               total_matches=VALUES(total_matches),
                                               bowling_average=VALUES(bowling_average),
                                               best_figures=VALUES(best_figures);""",
                    (
                        player_id,
                        odi_stats.get("wickets", 0),
                        odi_stats.get("matches", 0),
                        odi_stats.get("average", 0.0),
                        odi_stats.get("bbm", ""),
                    ),
                )
                connection.commit()
                print(f"Inserted bowling stats for {player_id}")
    except Exception as e:
        print(f"Error inserting bowling stats for {player_id}: {e}")

# ==============================
# MAIN INGESTION LOGIC
# ==============================
def run_ingestion():
    api_data = fetch_live_matches()
    if not api_data:
        print("No API data fetched.")
        return

    connection = get_db_connection()
    if not connection:
        print("DB connection failed.")
        return

    try:
        # Insert teams and matches
        insert_team_and_match_data(api_data, connection)

        # For each team -> fetch players
        cursor = connection.cursor()
        cursor.execute("SELECT team_id FROM teams")
        team_ids = [row[0] for row in cursor.fetchall()]

        for team_id in team_ids:
            players_data = fetch_team_players(team_id)
            if not players_data:
                continue

            for player in players_data.get("player", []):
                player_id = str(player.get("id"))
                player_details = fetch_player_details(player_id)
                insert_player_data(player_details, connection)

                batting_stats = fetch_batting_stats(player_id)
                insert_batting_stats(player_id, batting_stats, connection)

                bowling_stats = fetch_bowling_stats(player_id)
                insert_bowling_stats(player_id, bowling_stats, connection)

    finally:
        close_db_connection(connection)


if __name__ == "__main__":
    run_ingestion()
