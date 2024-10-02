from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTextBrowser,
    QTextEdit,
    QApplication,
    QVBoxLayout,
    QListWidget,
    QHBoxLayout,
    QListWidgetItem
)

import sys
import os
import pandas as pd
import mysql.connector

if getattr(sys, 'frozen', False):
    from utilities.utils import apply_style_sheet, load_credentials, check_connection
else:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    from utilities.utils import apply_style_sheet, load_credentials, check_connection

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
        self.execute_button = QPushButton("Execute")
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

    def execute_query():
        pass

    def save_results():
        pass

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