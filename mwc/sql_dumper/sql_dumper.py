from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QApplication,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem,
    QProgressDialog,
    QTableWidgetItem,
    QFileDialog
)

from PyQt6.QtCore import Qt

import sys
import os
import pandas as pd

if getattr(sys, 'frozen', False):
    from utilities.utils import apply_style_sheet, load_credentials, check_connection
    from query_handler.query_thread import QueryThread
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from utilities.utils import apply_style_sheet, load_credentials, check_connection
    from query_handler.query_thread import QueryThread

class APP_SQL_Dumper(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("SQL Dumper")
        self.setGeometry(100, 100, 1000, 675)
        self.center_gui()

        # Apply the style sheet from a file
        apply_style_sheet(self)

        # Central widget and main horizontal layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left layout for connection list
        left_layout = QVBoxLayout()
        self.connection_list = QListWidget()

        self.connection_list.itemClicked.connect(self.on_connection_click)
        self.connection_list.setFixedWidth(200)
        left_layout.addWidget(self.connection_list)

        main_layout.addLayout(left_layout, 1)  # Add left layout to main layout with stretch factor

        # Right layout for other widgets
        right_layout = QVBoxLayout()

        # Test Connection button
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.setEnabled(False)
        self.test_connection_button.clicked.connect(self.test_connection)
        left_layout.addWidget(self.test_connection_button)

        # Label
        self.label = QLabel("Enter SQL query:")
        right_layout.addWidget(self.label)

        # Text area for SQL input
        self.sql_text_area = QTextEdit()
        right_layout.addWidget(self.sql_text_area)

        # Execute button
        self.execute_button = QPushButton("Execute", self)
        self.execute_button.clicked.connect(self.execute_query)
        right_layout.addWidget(self.execute_button)

        # Save button
        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self.save_results)
        right_layout.addWidget(self.save_button)

        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        right_layout.addWidget(self.reset_button)

        # Result label
        self.result_label = QLabel("Output Preview (First 100 rows)")
        right_layout.addWidget(self.result_label)

        # Table for displaying results
        self.results_table = QTableWidget()
        right_layout.addWidget(self.results_table)

        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet(
            "QLabel { padding: 4px 0px 4px 0px; margin: 0px 0px 0px 0px; }"
        )
        right_layout.addWidget(self.status_label)

        main_layout.addLayout(right_layout, 3)

        self.credentials = load_credentials()
        self.selected_connection = None

        self.results_df = pd.DataFrame()        # Placeholder for results

        self.populate_list()
        self.query_thread = None  # Initialize the query thread variable

    def center_gui(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_connection_click(self, item):
        selected_connection = item.text()
        if selected_connection in self.credentials:
            self.test_connection_button.setEnabled(True)
        else:
            self.test_connection_button.setEnabled(False)

    def test_connection(self):
        parent_name = self.connection_list.currentItem().text()
        if parent_name not in self.credentials:
            QMessageBox.critical(self, "Error", "Selected connection not found.")
            return
        
        connection_info = self.credentials[parent_name]

        if check_connection(connection_info):
            QMessageBox.information(self, "Success", "Connection successful.")
            self.selected_connection = parent_name
            self.test_connection_button.setEnabled(False)
            self.status_label.setText(f"Connected to {parent_name}")
            self.status_label.setStyleSheet(
                "background-color: rgba(154, 228, 69, 0.64); padding: 4px 0px 4px 0px; margin: 0px 0px 0px 0px; color: black;"
            )
        else:
            QMessageBox.critical(self, "Error", "Connection failed.")
            self.status_label.setText(f"Fail to connect to: {parent_name}")
            self.status_label.setStyleSheet(
                "background-color: 	rgb(255, 102, 102); padding: 4px 0px 4px 0px; margin: 0px 0px 0px 0px; color: black;"
            )

    def execute_query(self):
        if not self.selected_connection:
            QMessageBox.warning(self, "Warning", "Please select a connection first.")
            return

        query = self.sql_text_area.toPlainText()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a SQL query.")
            return

        # Show progress dialog
        self.progress_dialog = QProgressDialog("Executing query...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)  # Correct usage
        self.progress_dialog.setRange(0, 0)  # Indeterminate progress
        self.progress_dialog.show()

        # Disable buttons during execution
        self.execute_button.setEnabled(False)
        self.test_connection_button.setEnabled(False)

        # Start the query execution in a separate thread
        self.query_thread = QueryThread(query, self.credentials[self.selected_connection])
        self.query_thread.finished_signal.connect(self.on_query_finished)
        self.query_thread.start()

    def on_query_finished(self, data):
        results, column_names = data  # Unpack the results and column names
        print("Query thread has finished execution.")

        # Store results in self.results_df
        self.results_df = pd.DataFrame(results, columns=column_names)

        # Populate the results table with the query results
        self.populate_results_table(results, column_names)


    def populate_results_table(self, results, column_names):
        self.progress_dialog.close()
        self.execute_button.setEnabled(True)
        self.test_connection_button.setEnabled(True)

        self.results_table.setRowCount(0)  # Clear previous results
        self.results_table.setColumnCount(0)

        # Check if there are results
        if results:
            # Set the column count based on the number of columns in the first result
            self.results_table.setColumnCount(len(column_names))

            # Set headers based on the column names
            self.results_table.setHorizontalHeaderLabels(column_names)

        max_rows = 100  
        total_rows = len(results)

        for row_index, row in enumerate(results):
            if row_index >= max_rows:  # Stop after the first 100 rows
                break
            row_position = self.results_table.rowCount()
            self.results_table.insertRow(row_position)
            for column, data in enumerate(row):
                self.results_table.setItem(row_position, column, QTableWidgetItem(str(data)))

            self.result_label.setText("Output Preview (First 100 rows of " + str(total_rows) + " rows)")
        else:
            self.result_label.setText("No results returned.")

    def save_results(self):
        if self.results_df.empty:
            QMessageBox.warning(self, "Warning", "No results to save.")
            return

        options = QFileDialog.Option(0)  # You can specify options if needed
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Results",
            "",
            "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)",
            options=options,
        )
        if file_path:
            try:
                # Define the chunk size
                chunk_size = 10000  # Adjust this size as needed

                # Create a progress dialog
                num_chunks = (len(self.results_df) // chunk_size) + 1
                progress = QProgressDialog("Exporting data...", "Cancel", 0, num_chunks, self)
                progress.setWindowModality(Qt.WindowModality.WindowModal) 
                progress.show()

                # Save in chunks
                for i, chunk in enumerate(range(0, len(self.results_df), chunk_size)):
                    self.results_df.iloc[chunk:chunk + chunk_size].to_csv(file_path, mode='a', header=(i == 0), index=False)

                    # Update progress dialog
                    progress.setValue(i)
                    if progress.wasCanceled():
                        break

                progress.setValue(num_chunks)  # Ensure the progress dialog is complete
                QMessageBox.information(self, "Success", "Results saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save results: {e}")

    def reset(self):
        self.sql_text_area.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.result_label.setText("Output Preview (First 100 rows)")
        self.selected_connection = None
        self.populate_list()
        self.test_connection_button.setEnabled(False)
        self.status_label.setText(None)
        self.status_label.setStyleSheet(None)

    def populate_list(self):
        self.connection_list.clear()
        for parent in self.credentials:
            item = QListWidgetItem(parent)
            self.connection_list.addItem(item)

def main():
    app = QApplication(sys.argv)
    window = APP_SQL_Dumper()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()