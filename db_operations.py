"""
Description: Python Project Milestone 1 - Database Operations
Author: Jake Licmo
Date: 2025-03-28
"""
import os
import csv
from dbcm import DBCM

class DBOperations:
    """
    Handles SQLite database operations for weather data.
    """
    def __init__(self, db_name='weather_data.db'):
        """
        Initializes the database connection and creates the table if it doesn't exist.
        :param db_name: Name of the SQLite database file.
        """
        self.db_name = db_name
        self.initialize_db()

    def initialize_db(self):
        """
        Creates the weather table if it doesn't exist.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    max_temp REAL,
                    min_temp REAL,
                    avg_temp REAL,
                    UNIQUE(sample_date, location)
                )
            ''')

    def fetch_data(self, location):
        """
        Fetches weather data for a specific location from the database.
        :param location: The location for which to fetch weather data.
        :return: A list of tuples containing the weather data.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute('''
                SELECT sample_date, min_temp, max_temp, avg_temp FROM weather
                WHERE location = ?
                ORDER BY sample_date
            ''', (location,))
            return cursor.fetchall()

    def save_data(self, data_dict, location="Winnipeg"):
        """
        Saves weather data to the database.
        :param data_dict: A dictionary containing weather data.
        """
        with DBCM(self.db_name) as cursor:
            for sample_date, temps in data_dict.items():
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO weather (sample_date, location, min_temp, max_temp, avg_temp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        sample_date,
                        location,
                        temps.get('Max'),
                        temps.get('Min'),
                        temps.get('Mean')
                    ))
                except Exception as e:
                    print(f"Error saving data for {sample_date}: {e}")

    def purge_data(self):
        """
        Deletes all data from the weather table.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute('DELETE FROM weather')

    def get_latest_date(self, location="Winnipeg"):
        """
        Gets the most recent sample_date in the DB for a given location.
        """
        with DBCM(self.db_name) as cursor:
            cursor.execute('''
                SELECT MAX(sample_date) FROM weather
                WHERE location = ?
            ''', (location,))
            result = cursor.fetchone()
            return result[0]


    def export_to_csv(self, output_path, location="Winnipeg"):
        """
        Exports all weather data for a specific location to a CSV file.
        :param output_path: The file path to save the CSV.
        :param location: The location to export data for.
        """
        data = self.fetch_data(location)

        if not data:
            print(f"No data found for location: {location}")
            return

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Min Temp", "Max Temp", "Mean Temp"])
            for row in data:
                writer.writerow(row)

        print(f"Data exported to {output_path}")
