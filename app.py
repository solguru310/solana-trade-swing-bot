from typing import List, Dict
from flask import Flask
import mysql.connector
import json
import datetime
import os
from dotenv import load_dotenv

app = Flask(__name__)

def defaultconverter(o):
  if isinstance(o, datetime.datetime):
      return o.__str__()

def get_positions() -> List[Dict]:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute("""SELECT p.txid, p.type, p.closed_at, o.pair FROM  `position` p
                    INNER JOIN `trade` t ON p.txid = t.txid
                    INNER JOIN `order` o ON p.txid = o.txid
                    GROUP BY t.txid""")
    columns = cursor.description
    results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def get_orders() -> List[Dict]:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `order`')
    columns = cursor.description
    results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def get_trades() -> List[Dict]:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_DATABASE'),
    }
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM `trade` ORDER by closed_at DESC')
    columns = cursor.description
    results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def get_time_frames() -> List[Dict]:
    import cfg_load
    alpha = cfg_load.load('/home/user/app/alpha.yaml')
    return alpha["time_frames"]

@app.route('/time_frames')
def time_frames() -> str:
    return json.dumps({'time_frames': get_time_frames()}, default = defaultconverter)

@app.route('/orders')
def orders() -> str:
    return json.dumps({'orders': get_orders()}, default = defaultconverter)

@app.route('/trades')
def trades() -> str:
    return json.dumps({'trades': get_trades()}, default = defaultconverter)

@app.route('/positions')
def positions() -> str:
    return json.dumps({'positions': get_positions()}, default = defaultconverter)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
