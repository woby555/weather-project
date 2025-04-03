import sqlite3
from dbcm import DBCM


class DBOperations:
    def __init__(self, db_name='weather_data.db'):
        self.db_name = db_name
        self.initialize_db()

    def initialize_db(self):
        with DBCM(self.db_name) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sample_date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    min_temp REAL,
                    max_temp REAL,
                    avg_temp REAL,
                    UNIQUE(sample_date, location)
                )
            ''')

    def fetch_data(self, location):
        with DBCM(self.db_name) as cursor:
            cursor.execute('''
                SELECT sample_date, min_temp, max_temp, avg_temp FROM weather
                WHERE location = ?
                ORDER BY sample_date
            ''', (location,))
            return cursor.fetchall()

    def save_data(self, data_dict):
        with DBCM(self.db_name) as cursor:
            for sample_date, weather in data_dict.items():
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO weather (sample_date, location, min_temp, max_temp, avg_temp)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        sample_date,
                        weather['location'],
                        weather['min_temp'],
                        weather['max_temp'],
                        weather['avg_temp']
                    ))
                except sqlite3.Error as e:
                    print(f"Error saving data for {sample_date}: {e}")



    def purge_data(self):
        with DBCM(self.db_name) as cursor:
            cursor.execute('DELETE FROM weather')