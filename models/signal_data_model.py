import app.models.model as m

class SignalDataModel:
    def __init__(self):
        self.model = m.Model()

    def get_market_state(self, time_frame, pair):
        sql = """ SELECT * FROM `market_state`
                  WHERE time_frame = %s AND pair = %s
                  ORDER BY id DESC LIMIT 1 """
        params = (time_frame, pair, )
        return self.model.select_one(sql, params)

    def insert_market_state(self, pair, price, time_frame, type):
        sql = "INSERT IGNORE INTO `market_state` (pair, price, time_frame, type) VALUES (%s, %s, %s, %s)"
        params = (pair, price, time_frame, type, )
        return self.model.insert(sql, params)