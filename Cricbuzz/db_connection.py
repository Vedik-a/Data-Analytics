import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    try:
        
     connection = mysql.connector.connect(
    host="localhost",
    database="cricbuzz_livestats",
    user="root",
    password="pass@ved07",
    port=3306
)
     if connection.is_connected():
            print("Successfully connected to MySQL database.")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_db_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection is closed.")

        