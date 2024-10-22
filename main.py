import sys
import os

# Get the current working directory
original_dir = os.getcwd()

# Check if the program is running in a frozen state
if getattr(sys, 'frozen', False):
    # Join with '_internal' if in frozen environment
    os.chdir(os.path.join(original_dir, "_internal"))
    print("Changed Working Directory to:", os.getcwd())
else:
    # Development environment, do nothing
    print("Running in development mode, directory unchanged.")

# Print the current working directory
basedir = os.getcwd()
print('Working Directory for main.py:', basedir)

from utilities.utils import apply_style_sheet, load_config

from mwc.sql_dumper.sql_dumper import APP_SQL_Dumper

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QTextBrowser
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Suite Launcher")
        self.setGeometry(0, 0, 600, 200)
        self.center_gui()
        apply_style_sheet(self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Load applications from the config file
        self.applications = load_config()

        # Create a dropdown for applications
        self.combo_box = QComboBox(self)
        self.combo_box.addItem("Please choose an application")
        self.combo_box.addItems([app['name'] for app in self.applications])
        self.combo_box.setStyleSheet("QComboBox { padding: 2px 0px 2px 6px; margin: 0px 0px 0px 0px; }")
        layout.addWidget(self.combo_box)

        # Optional: Text area for application description
        self.description_text = QTextBrowser()
        self.description_text.setMaximumHeight(80)
        layout.addWidget(self.description_text)

        # Create a button to launch the selected application
        launch_button = QPushButton("Launch Application")
        launch_button.clicked.connect(self.initialize_app)
        layout.addWidget(launch_button)

        # Connect the combo box change event to update description
        self.combo_box.currentIndexChanged.connect(self.update_description)

    def initialize_app(self):
        """
        TO_DO: 
            [] 1) Create individual instances for applications. The launcher will remain open so the user can actually create multiple instances of the same application.    
            [] 2) Also need to add in some sort of check to see what application the user wants to instantiate. Currently is hardcoded to a single sql_dumper instance.
        """
        
        self.sql_app = APP_SQL_Dumper()
        self.sql_app.show()

    def update_description(self):
        current_index = self.combo_box.currentIndex() - 1
        if current_index >= 0:
            app = self.applications[current_index]
            self.description_text.setText(app['description'])
        else:
            self.description_text.clear()

    def center_gui(self):
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()