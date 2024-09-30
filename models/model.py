import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()

class Model:
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
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return None if len(results) == 0 else results[0]

    def select_all(self, sql, params):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results

    def insert(self, sql, params):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def update(self, sql, params):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        self.connection.commit()
        cursor.close()
        self.connection.close()