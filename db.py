import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="FILL_HERE",
            user="FILL_HERE",
            passwd="FILL_HERE",
            database="FILL_HERE"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
