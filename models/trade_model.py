import os
import requests
import json
from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
now = datetime.now()
import models.model as m

class TradeDataModel:
    def __init__(self):
        self.model = m.Model()
        load_dotenv()
        self.db_config = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_USER_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE'),
        }

    def get_initial_position_order_by_timeframe(self, time_frame, type):
        sql = """SELECT * FROM `order`
                 WHERE time_frame = %s
                 AND type = %s
                 ORDER BY created_at DESC
                 LIMIT 1"""
        return self.model.select_all(sql, (time_frame, type, ))

    def get_orders(self, pair = None, time_frame = None, status = None):
        if pair and time_frame and status:
            sql = 'SELECT * FROM `order` WHERE pair = %s AND time_frame = %s AND status = %s'
            params = (pair, time_frame, status, )
        else:
            sql = 'SELECT * FROM `order`'
            params = None
        sql = sql + ' ORDER BY created_at DESC'
        return self.model.select_all(sql, params)

    def open_orders(self, pair = None, time_frame = None, status = None):
        if pair and time_frame and status:
            sql = 'SELECT * FROM `order` WHERE pair = %s AND time_frame = %s AND status = %s'
            params = (pair, time_frame, status, )
        else:
            sql = 'SELECT * FROM `order`'
            params = None
        return self.model.select_all(sql, params)

    def get_position_by_closing_txid(self, closing_txid):
        sql = """SELECT * FROM  `position` WHERE closing_txid = %s AND closed_at IS NOT NULL """
        params = (closing_txid, )
        return self.model.select_one(sql, params)

    def save_order(self, txid, pair, time_frame, status, type, volume, price):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT IGNORE INTO `order` (txid, pair, time_frame, status, type, volume, price) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (txid, pair, time_frame, status, type, volume, price, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def get_order(self, txid):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = 'SELECT * FROM `order` WHERE txid = %s'
        cursor.execute(sql, (txid, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]

    def save_trade(self, txid, pair, cost, fee, price, closed_at):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT IGNORE INTO trade (txid, pair, cost, fee, price, closed_at) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (txid, pair, cost, fee, price, closed_at, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        return id

    def get_trade(self, txid):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = """SELECT * FROM trade WHERE txid = %s """
        cursor.execute(sql, (txid, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]

    def get_trades(self, pair, timeframe, status = None):
        sql = """SELECT * FROM trade
                 INNER JOIN `order` ON `order`.txid = trade.txid
                 AND trade.pair = %s AND `order`.time_frame = %s """
        sql = (sql + ' AND trade.closed_at IS NULL') if status == "open" else sql
        sql = sql + ' ORDER BY `order`.created_at DESC'
        return self.model.select_all(sql, (pair, timeframe, ))

    def close_order(self, txid):
        order = self.get_order(txid)
        if order and order['closed_at'] == None:
            self.connection = mysql.connector.connect(**self.db_config)
            cursor = self.connection.cursor()
            sql = "UPDATE `order` SET closed_at = %s, status = %s WHERE txid = %s"
            cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), 'closed', txid, ))
            self.connection.commit()
            cursor.close()
            self.connection.close()

    def open_position(self, txid, type):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "INSERT IGNORE INTO `position` (txid, type) VALUES (%s, %s)"
        cursor.execute(sql, (txid, type, ))
        self.connection.commit()
        id = cursor.lastrowid
        cursor.close()
        self.connection.close()
        return id

    def close_position(self, txid, closing_txid):
        print('close position')
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = "UPDATE `position` SET closed_at = %s, closing_txid = %s WHERE txid = %s"
        cursor.execute(sql, (now.strftime('%Y-%m-%d %H:%M:%S'), closing_txid, txid, ))
        self.connection.commit()
        cursor.close()
        self.connection.close()

    def get_position(self, txid):
        self.connection = mysql.connector.connect(**self.db_config)
        cursor = self.connection.cursor()
        sql = """SELECT * FROM  `position` WHERE txid = %s"""
        cursor.execute(sql, (txid, ))
        columns = cursor.description
        results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        cursor.close()
        self.connection.close()
        return [] if len(results) == 0 else results[0]

    def get_positions(self, pair, timeframe, status = None):
        sql = """SELECT * FROM  `position`
                 INNER JOIN `trade` ON `position`.txid = trade.txid
                 INNER JOIN `order` ON `position`.txid = order.txid
                 AND trade.pair = %s
                 AND `order`.time_frame = %s """
        sql = (sql + ' AND position.closed_at IS NULL') if status == "open" else sql
        sql = sql + ' ORDER BY trade.created_at DESC'
        return self.model.select_all(sql, (pair, timeframe, ))

    def open_positions(self):
        sql = """SELECT * FROM  `position`
                         INNER JOIN `trade` ON `position`.txid = trade.txid
                         INNER JOIN `order` ON `position`.txid = order.txid
                         AND position.closed_at IS NULL"""
        sql = sql + ' ORDER BY trade.created_at DESC'
        return self.model.select_all(sql, ())

    def closed_positions(self):
        sql = """SELECT * FROM  `position`
                         INNER JOIN `trade` ON `position`.txid = trade.txid
                         INNER JOIN `order` ON `position`.txid = order.txid
                         AND position.closed_at IS NOT NULL"""
        return self.model.select_all(sql, ())