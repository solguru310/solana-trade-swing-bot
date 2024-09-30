from datetime import datetime, timezone
import cfg_load
import models.trade_model as tm
import models.settings_model as sm
import strategy as s
import twitter as t
import helpers.util as u
import api.kraken as k
alpha = cfg_load.load('alpha.yaml')
import pandas as pd
import pandas_ta as ta
import sys

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.width', 1000)
import time
import status as st

class Trader:
    def __init__(self):
        self.status = st.Status()
        self.strategy = s.Strategy()
        self.trade = tm.TradeDataModel()
        self.settings = sm.SettingsModel()
        self.trading_enabled = True
        self.created_at = self.settings.created_at()
        self.kraken = k.Kraken()
        self.account_data = self.kraken.get_account_data()
        self.pair_data = {}
        self.trade_data = {}
        self.order_data = {}
        self.positions_data = {}
        self.go()

    def go(self):
        print(datetime.now())
        u.show('trading_enabled', self.trading_enabled)
        u.show_object('account_balance', self.account_data['account_balance'])
        self.cancel_expired_order()
        if self.trading_enabled:
            self.cancel_expired_order()
            self.save_trades(self.account_data['closed_orders'])
        for pair in alpha["pairs"]:
            if pair['pair'] == str(sys.argv[1]):
                u.show('pair', str(sys.argv[1]))
                self.pair_data = self.kraken.get_pair_data(pair['pair'])
                self.time_frame_signals(pair, alpha["time_frames"])
        self.status.realized()

    def time_frame_signals(self, pair, time_frames):
        for time_frame in time_frames:
            if time_frame['enabled'] and (int(time_frame['tf']) == int(sys.argv[2])):
                u.show('timeframe', time_frame['label'], 'above')
                if self.trading_enabled:
                    self.trade_data = self.trade.get_trades(pair['pair'], time_frame['tf'])
                ohlc = self.time_frame_ohlc_data(pair['pair'], time_frame['tf'])
                u.show('price', ohlc['close'].iloc[-1])
                trade_signal_buy, trade_signal_sell = self.strategy.setup(ohlc, time_frame, pair)
                u.show('trade signal buy', trade_signal_buy)
                u.show('trade signal sell', trade_signal_sell)

                if self.trading_enabled:
                    self.status.price = ohlc['close'].iloc[-1]
                    pnl_perc = self.status.show(pair, time_frame)
                    buy, sell = self.evaluate_signals(pair, trade_signal_buy, trade_signal_sell, time_frame)
                     
                    has_open_time_frame_order, has_open_time_frame_position = self.time_frame_state(pair, time_frame)
                    self.trigger_orders(buy, sell, has_open_time_frame_order, has_open_time_frame_position, time_frame, pair)
                
                
    def cancel_expired_order(self):
        open_orders = self.trade.get_orders()
        if self.account_data['open_orders'].empty:
            for open_order in open_orders:
                self.trade.close_order(open_order['txid'])
        for index, row in self.account_data['open_orders'].iterrows():
            if (int(time.time()) - int(row['opentm'])) > 120:
                search_orders = [value for elem in open_orders for value in elem.values()]
                if index in search_orders:
                    cancel_response = self.kraken.cancel_open_order(index)
                    print(cancel_response)
                    self.trade.close_order(index)

    def save_trades(self, closed_orders):
        for index, row in closed_orders.iterrows():
            if not self.trade.get_position_by_closing_txid(index):
                if self.created_at < datetime.fromtimestamp(row['closetm']):
                    trade = self.trade.get_trade(index)
                    if not trade:
                        self.trade.save_trade(index, row['descr_pair'], row['cost'], row['fee'], row['price'], datetime.fromtimestamp(row['closetm']))
                        self.trade.close_order(index)
                    position = self.trade.get_position(index)
                    if row['descr_type'] == 'buy':
                        if not position:
                            self.trade.open_position(index, 'long')
                    if row['descr_type'] == 'sell':
                        initial_position_orders = self.trade.get_initial_position_order_by_timeframe(row['userref'], 'buy')
                        for initial_position_order in initial_position_orders:
                            self.trade.close_position(initial_position_order['txid'], index)

    def time_frame_ohlc_data(self, pair, time_frame):
        time_frame_data = self.kraken.get_time_frame_data(pair, time_frame)
        time_frame_data = time_frame_data['ohlc'][::-1]
        now = datetime.now()
        time_frame_data.loc[pd.to_datetime(now.strftime("%Y-%m-%d %H:%M:%S"))] = [int(time.time()),0,0,0,float(self.pair_data['ticker_information']['a'][0][0]),0,0,0]
        index = range(0, len(time_frame_data.index))
        time_frame_data.index = index
        return time_frame_data

    def evaluate_signals(self, pair, trade_signal_buy, trade_signal_sell, time_frame):
        bid, ask = self.get_bid_ask(pair)
        account_status = self.kraken.account_status(self.account_data, pair, self.pair_data, bid, ask, time_frame)
        u.show('have_base_currency_to_buy', account_status['have_base_currency_to_buy'])
        u.show('have_quote_currency_to_sell', account_status['have_quote_currency_to_sell'])
        return (trade_signal_buy and account_status['have_base_currency_to_buy']), (trade_signal_sell and account_status['have_quote_currency_to_sell'])

    def trigger_orders(self, buy, sell, has_open_time_frame_order, has_open_time_frame_position, time_frame, pair):
        if buy and not has_open_time_frame_order and not has_open_time_frame_position:
            self.buy_trigger(time_frame, pair)
        if (sell and has_open_time_frame_position and not has_open_time_frame_order):
            self.sell_trigger(time_frame, pair)

    def time_frame_state(self, pair, time_frame):
        return self.time_frame_order_state(pair['pair'], time_frame['tf'], 'open'), self.time_frame_position_state(pair['pair'], time_frame['tf'], 'open'),

    def time_frame_position_state(self, pair, time_frame, status):
        self.positions_data = self.trade.get_positions(pair, time_frame, status)
        return 1 if len(self.positions_data) != 0 else 0
        
    def time_frame_order_state(self, pair, time_frame, status):
        self.order_data = self.trade.get_orders(pair, time_frame, status)
        return 1 if len(self.order_data) != 0 else 0

    def buy_trigger(self, time_frame, pair):
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'buy', 'open')
        
    def sell_trigger(self, time_frame, pair):
        time.sleep(1)
        order_info = self.place_order(time_frame, pair, 'sell', 'open')

    def place_order(self, time_frame, pair, type, status):
        order_response = self.kraken.add_standard_order(pair['pair'], type, 'limit', time_frame['size'], self.get_limit(pair, type), None, None, None, 0, 0, time_frame['tf'], False)
        self.post_trade(order_response, pair, time_frame, type)
        for txid in order_response['txid']:
            self.trade.save_order(txid, pair['pair'], time_frame['tf'], status, type, time_frame['size'], self.get_limit(pair, type))

    def get_limit(self, pair, type):
        bid, ask = self.get_bid_ask(pair)
        return ask if type == 'buy' else bid

    def get_bid_ask(self, pair):
        return float(self.pair_data['ticker_information'].loc[pair['pair'], 'b'][0]) - 5, float(self.pair_data['ticker_information'].loc[pair['pair'], 'a'][0]) + 5


    def tweet(self, data, file = None):
        twitter = t.Twitter()

        print(data)
        if alpha["twitter_enabled"]:
            twitter.tweet(data, file)

    def post_trade(self, order, pair, tf, type):
        print(order)
        print(order['descr']['order'])
        utc_datetime = datetime.now(timezone.utc)
        data = ''
        for h in pair['hash_tags']:
            data = data + '#' + h + ' '
        data = data + '\r\n'
        data = data + type + '\r\n'

        data = data + '\r\n'
        data = data + '$' + str(self.status.price) + '\r\n'
        data = data + str(utc_datetime.strftime("%Y-%m-%d %H:%M:%S")) + '\r\n'
        data = data + 'Timeframe: ' + tf['label'] + '\r\n\r\n'
       
        self.tweet(data)
            
t = Trader()