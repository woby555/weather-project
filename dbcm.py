"""
Description: Python Project Milestone 1 - Database Context Manager
Author: Jake Licmo
Date: 2025-03-28
"""

import sqlite3

class DBCM:
    """
    Database Context Manager for SQLite.
    This class provides a context manager for SQLite database operations.
    It handles the connection and cursor creation, and ensures that
    the connection is properly closed after use.
    """
    def __init__(self, db_name):
        """
        Initializes the context manager with the database name.
        :param db_name: The name of the SQLite database file.
        """
        self.db_name = db_name

    def __enter__(self):
        """
        Establishes a connection to the database and creates a cursor.
        :return: The cursor object for executing SQL commands.
        """
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection.
        """
        if exc_type is None:
            self.conn.commit()
        self.conn.close()

