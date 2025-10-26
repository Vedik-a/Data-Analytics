create database gamesdb;
 show tables;
 
 -- Top 10 games by global sales
SELECT Name, Platform, Global_Sales
FROM vgsales
ORDER BY Global_Sales DESC
LIMIT 10;
-- Average rating by release year
SELECT Release_Year, AVG(Rating) AS Avg_Rating
FROM games
GROUP BY Release_Year
ORDER BY Release_Year DESC;
-- Total Global Sales by Genre
SELECT Genre, 
       SUM(Global_Sales) AS Total_Sales
FROM vgsales
GROUP BY Genre
ORDER BY Total_Sales DESC;
-- Average Global Sales per Publisher
SELECT Publisher, 
       AVG(Global_Sales) AS Avg_Sales
FROM vgsales
GROUP BY Publisher
ORDER BY Avg_Sales DESC
LIMIT 10;
-- Total Games Released per Year
SELECT Release_Year, COUNT(*) AS Total_Games
FROM games
GROUP BY Release_Year
ORDER BY Release_Year DESC;
-- Sales by Region and Genre
SELECT Genre,
       SUM(NA_Sales) AS NA_Total,
       SUM(EU_Sales) AS EU_Total,
       SUM(JP_Sales) AS JP_Total,
       SUM(Other_Sales) AS Other_Total
FROM vgsales
GROUP BY Genre
ORDER BY NA_Total DESC;
-- Average Rating by Genre
SELECT Genres AS Genre, 
       AVG(Rating) AS Avg_Rating
FROM games
GROUP BY Genres
ORDER BY Avg_Rating DESC;
-- Combine Ratings and Sales by Game
SELECT g.Title, g.Rating, v.Global_Sales
FROM games g
JOIN vgsales v
  ON g.Title = v.Name;
-- Total Sales per Release Year
SELECT g.Release_Year,
       SUM(v.Global_Sales) AS Total_Sales
FROM games g
JOIN vgsales v
  ON g.Title = v.Name
GROUP BY g.Release_Year
ORDER BY g.Release_Year DESC;

 
