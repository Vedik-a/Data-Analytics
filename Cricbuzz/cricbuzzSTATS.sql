SELECT * FROM teams;
Show tables;
SELECT * FROM players LIMIT 10;
SELECT * FROM batting_stats LIMIT 10;
SELECT * FROM bowling_stats LIMIT 10;
DESCRIBE teams;
ALTER TABLE matches ADD COLUMN venue VARCHAR(255);
CREATE TABLE players (
    player_id VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    playing_role VARCHAR(100),
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50),
    nationality VARCHAR(100)
);
CREATE TABLE batting_stats (
    player_id VARCHAR(50) PRIMARY KEY,
    total_runs INT,
    total_matches INT,
    batting_average DECIMAL(10, 2),
    highest_score INT
);
CREATE TABLE bowling_stats (
    player_id VARCHAR(50),
    total_wickets INT,
    total_matches INT,
    bowling_average FLOAT,
    best_figures VARCHAR(20),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
-- 1. List all teams from India
SELECT team_name, team_sname
FROM teams
WHERE team_name = 'India' OR team_sname = 'IND';

-- 2. Matches played in the last 30 days
SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
       m.series_name, m.start_date
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
WHERE m.start_date >= (CURRENT_DATE - INTERVAL 30 DAY)
ORDER BY m.start_date DESC;

DESCRIBE matches;

-- 3. Top 10 teams with most wins
SELECT t.team_name, COUNT(*) AS wins
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
GROUP BY t.team_name
ORDER BY wins DESC
LIMIT 10;

-- 4. Venues with more than 10 matches
SELECT series_name, COUNT(*) AS matches_played
FROM matches
GROUP BY series_name
HAVING COUNT(*) > 10
ORDER BY matches_played DESC;

-- 5. Matches won by each team
SELECT t.team_name, COUNT(*) AS wins
FROM matches m
JOIN teams t 
  ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
GROUP BY t.team_name
ORDER BY wins DESC;

-- 6. Matches played by each team
SELECT t.team_name, COUNT(*) AS matches_played
FROM teams t
JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
GROUP BY t.team_name
ORDER BY matches_played DESC;

-- 7. Longest win descriptions (approx "largest victory margin")
SELECT status
FROM matches
WHERE status LIKE '%won by%'
ORDER BY LENGTH(status) DESC
LIMIT 3;

-- 8. Matches in 2024
SELECT match_desc, series_name, match_format, FROM_UNIXTIME(start_date/1000) AS start_time
FROM matches
WHERE YEAR(FROM_UNIXTIME(start_date/1000)) = 2024;

-- 9. Teams with more than 20 wins
SELECT t.team_name, COUNT(*) AS wins
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
GROUP BY t.team_name
HAVING COUNT(*) > 20
ORDER BY wins DESC;

-- 10. Last 20 completed matches
SELECT m.match_desc, t1.team_name AS team1, t2.team_name AS team2,
       m.status, m.series_name
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
WHERE m.state = 'Complete'
ORDER BY m.start_date DESC
LIMIT 20;

-- 11. Wins split by match_format
SELECT match_format, t.team_name, COUNT(*) AS wins
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
GROUP BY match_format, t.team_name
ORDER BY match_format, wins DESC;

-- 12. Home vs Away (approx: if series_name contains team name = home)
SELECT t.team_name,
       SUM(CASE WHEN m.series_name LIKE CONCAT('%', t.team_name, '%')
                AND m.status LIKE CONCAT(t.team_name, '%') THEN 1 ELSE 0 END) AS home_wins,
       SUM(CASE WHEN m.series_name NOT LIKE CONCAT('%', t.team_name, '%')
                AND m.status LIKE CONCAT(t.team_name, '%') THEN 1 ELSE 0 END) AS away_wins
FROM teams t
JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
GROUP BY t.team_name;

-- 13. Team’s biggest win (status with max length)
SELECT t.team_name, m.status
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
ORDER BY LENGTH(m.status) DESC
LIMIT 10;

-- 14. Most common formats
SELECT match_format, COUNT(*) AS matches
FROM matches
GROUP BY match_format
ORDER BY matches DESC;

-- 15. Close wins (margin in status < 50 runs OR < 5 wickets)
SELECT t.team_name, COUNT(*) AS close_wins
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE (m.status LIKE '%won by % run%' AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' run', 1) AS UNSIGNED) < 50)
   OR (m.status LIKE '%won by % wkt%' AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' wkt', 1) AS UNSIGNED) < 5)
GROUP BY t.team_name
ORDER BY close_wins DESC;

-- 16. Matches per year
SELECT YEAR(FROM_UNIXTIME(start_date/1000)) AS year, COUNT(*) AS matches
FROM matches
GROUP BY year
ORDER BY year;

-- 18. Wins by format
SELECT match_format, t.team_name, COUNT(*) AS wins
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
GROUP BY match_format, t.team_name
ORDER BY match_format, wins DESC;

-- 19. Teams with average margin (approx: extract number from status)
SELECT t.team_name,
       AVG(CASE 
            WHEN m.status LIKE '%won by % run%' 
            THEN CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' run', 1) AS UNSIGNED)
            WHEN m.status LIKE '%won by % wkt%' 
            THEN CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.status, 'won by ', -1), ' wkt', 1) AS UNSIGNED)
           END) AS avg_margin
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won by%'
GROUP BY t.team_name
ORDER BY avg_margin DESC;

-- 20. Matches + wins breakdown by format
SELECT t.team_name, m.match_format,
       COUNT(*) AS total_matches,
       SUM(CASE WHEN m.status LIKE CONCAT(t.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) AS wins
FROM teams t
JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
GROUP BY t.team_name, m.match_format;

-- 21. Team performance score (wins * 2 + matches)
SELECT t.team_name,
       (SUM(CASE WHEN m.status LIKE CONCAT(t.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) * 2) +
       COUNT(*) AS perf_score
FROM teams t
JOIN matches m ON t.team_id IN (m.team1_id, m.team2_id)
GROUP BY t.team_name
ORDER BY perf_score DESC;

-- 22. Head-to-head
SELECT LEAST(t1.team_name, t2.team_name) AS teamA,
       GREATEST(t1.team_name, t2.team_name) AS teamB,
       COUNT(*) AS matches_played,
       SUM(CASE WHEN m.status LIKE CONCAT(t1.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) AS teamA_wins,
       SUM(CASE WHEN m.status LIKE CONCAT(t2.team_name, '%') AND m.status LIKE '%won%' THEN 1 ELSE 0 END) AS teamB_wins
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
GROUP BY teamA, teamB
HAVING COUNT(*) >= 5;

-- 23. Recent form (last 10 matches per team)
WITH ranked AS (
  SELECT m.match_id, m.start_date, t.team_id, t.team_name,
         (m.status LIKE CONCAT(t.team_name, '%') AND m.status LIKE '%won%') AS is_win,
         ROW_NUMBER() OVER (PARTITION BY t.team_id ORDER BY m.start_date DESC) AS rn
  FROM matches m
  JOIN teams t ON t.team_id IN (m.team1_id, m.team2_id)
)
SELECT team_name,
       AVG(CASE WHEN rn <= 5 THEN is_win ELSE NULL END) AS win_rate_last5,
       AVG(CASE WHEN rn <= 10 THEN is_win ELSE NULL END) AS win_rate_last10
FROM ranked
WHERE rn <= 10
GROUP BY team_name;

-- 24. Most frequent rivalries
SELECT LEAST(t1.team_name, t2.team_name) AS teamA,
       GREATEST(t1.team_name, t2.team_name) AS teamB,
       COUNT(*) AS matches_played
FROM matches m
JOIN teams t1 ON m.team1_id = t1.team_id
JOIN teams t2 ON m.team2_id = t2.team_id
GROUP BY teamA, teamB
ORDER BY matches_played DESC;

-- 25. Wins per year
SELECT t.team_name, YEAR(FROM_UNIXTIME(m.start_date/1000)) AS year,
       COUNT(*) AS wins
FROM matches m
JOIN teams t ON m.status LIKE CONCAT(t.team_name, '%')
WHERE m.status LIKE '%won%'
GROUP BY t.team_name, year
ORDER BY year, wins DESC;