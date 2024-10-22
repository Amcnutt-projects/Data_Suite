from PyQt6.QtCore import QThread, pyqtSignal
import mysql.connector
from mysql.connector import Error

class QueryThread(QThread):
    # Signal to indicate when the thread is done and to pass results
    finished_signal = pyqtSignal(list)  # Change to emit results

    def __init__(self, query, credentials):
        super().__init__()
        self.query = query
        self.credentials = credentials

    def run(self):
        results = []
        column_names = []
        try:
            print(f"Connecting to database with credentials: {self.credentials}")
            connection = mysql.connector.connect(**self.credentials)

            if connection.is_connected():
                cursor = connection.cursor()
                print(f"Executing query: {self.query}")
                cursor.execute(self.query)

                # Fetch results and cursor description
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                print("Query execution finished.")
                
            else:
                print("Failed to connect to the database.")

        except Error as e:
            print(f"Error occurred: {e}")

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("Database connection closed.")

        # Emit the results and column names signal
        self.finished_signal.emit((results, column_names))