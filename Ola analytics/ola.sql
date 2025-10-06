create database olaa;
show tables;

SELECT *
FROM ola_july_cleaned
WHERE Booking_Status = 'Success';

SELECT Vehicle_Type, AVG(Ride_Distance) AS Avg_Ride_Distance
FROM ola_july_cleaned
GROUP BY Vehicle_Type;

SELECT COUNT(*) AS Cancelled_By_Customers
FROM ola_july_cleaned
WHERE Booking_Status = 'Canceled by Customer';

SELECT Customer_ID, COUNT(*) AS Total_Rides
FROM ola_july_cleaned
GROUP BY Customer_ID
ORDER BY Total_Rides DESC
LIMIT 5;

SELECT COUNT(*) AS Total_Canceled_By_Driver
FROM ola_july_cleaned
WHERE Booking_Status = 'Canceled by Driver';

SELECT MAX(Driver_Ratings) AS Max_Rating,
       MIN(Driver_Ratings) AS Min_Rating
FROM ola_july_cleaned
WHERE Vehicle_Type = 'Prime Sedan';

SELECT *
FROM ola_july_cleaned
WHERE Payment_Method = 'UPI';

SELECT Vehicle_Type, AVG(Customer_Rating) AS Avg_Customer_Rating
FROM ola_july_cleaned
GROUP BY Vehicle_Type;

SELECT SUM(Booking_Value) AS Total_Booking_Value
FROM ola_july_cleaned
WHERE Booking_Status = 'Success';

SELECT Booking_ID, Customer_ID, Vehicle_Type, Incomplete_Rides_Reason
FROM ola_july_cleaned
WHERE Incomplete_Rides = 'Yes';
