import os
import requests
from dotenv import load_dotenv
import mysql.connector

class SettingsModel:
    def __init__(self):
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def select_one(self, sql, params):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        columns = cursor.description
        result = cursor.fetchone()
        cursor.close()
        self.connection.close()
        return result

    def trading_enabled(self):
        sql = """SELECT * FROM `settings` WHERE setting = %s """
        return self.select_one(sql, ('trading_enabled', ))[3]

    def created_at(self):
        sql = """SELECT * FROM `settings` WHERE setting = %s """
        return self.select_one(sql, ('created_at', ))[1]
