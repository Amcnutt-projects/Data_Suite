import os
import sys
import yaml
import json
import mysql.connector

def apply_style_sheet(self):
    with open('resources\\style.qss', "r") as file:
        style_sheet = file.read()
        self.setStyleSheet(style_sheet)
        return self
    
def load_config():
    with open('resources\\launcher.yaml', "r") as config_file:
        config_data = yaml.safe_load(config_file)
        return config_data.get('applications', [])

def load_credentials():
    with open('resources\\credentials.json', "r") as f:
        credentials = json.load(f)
        return credentials
    
def check_connection(credentials) -> bool:
    try:
        connection = mysql.connector.connect(**credentials)
        if connection.is_connected():
            connection.close()
            return True
        else:
            return False
        
    except Exception as e:
        print(e)
        return False