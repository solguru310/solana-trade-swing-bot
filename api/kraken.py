import api.kraken as k
import krakenex
from pykrakenapi import KrakenAPI
import time

class Kraken:
    def __init__(self):
        kex = krakenex.API()
        kex.load_key('kraken.key')
        self.k = KrakenAPI(kex)
        self.delay = 2

    def cancel_open_order(self, txid):
        return self.k.cancel_open_order(txid)

    def add_standard_order(self, pair, type, ordertype, volume, price, price2, leverage, oflags, starttm, expiretm, userref, validate):
        return self.k.add_standard_order(ordertype, type, pair, userref, volume, price, price2, None, leverage, oflags, None, starttm, expiretm, None, None, None, None, validate)

    def get_time_frame_data(self, pair, time_frame):
        ohlc, last = self.k.get_ohlc_data(pair, time_frame)
        time.sleep(self.delay)
        return {
            "ohlc": ohlc,
            "last": last,
        }

    def get_pair_data(self, pair):
        order_book = self.k.get_order_book(pair, 10, True)
        time.sleep(self.delay)
        trade_volume = self.k.get_trade_volume(pair)
        time.sleep(self.delay)
        ticker_information = self.k.get_ticker_information(pair)
        time.sleep(self.delay)
        recent_trades = self.k.get_recent_trades(pair, since = None)
        time.sleep(self.delay)
        return {
            "ask_price": order_book[0]['price'].iloc[0],
            "bid_price": order_book[1]['price'].iloc[0],
            "fee_currency": trade_volume[0],
            "taker_fee": trade_volume[2][pair]['fee'],
            "maker_fee": trade_volume[3][pair]['fee'],
            "ticker_information": ticker_information,
            "recent_trades": recent_trades,
        }

    def account_status(self, account_data, pair, pair_data, bid, ask, time_frame):
        base_balance = account_data['account_balance'].loc[pair['currency']['base'], 'vol']
        quote_balance = account_data['account_balance'].loc[pair['currency']['quote'], 'vol']
        buy_volume = time_frame['size'] * ask
        sell_volume = time_frame['size']
        return {
            'base_balance': base_balance,
            'quote_balance': quote_balance,
            'buy_volume': buy_volume,
            'sell_volume': sell_volume,
            'quote_balance_in_base_currency': quote_balance * bid,
            'have_base_currency_to_buy': base_balance > buy_volume,
            'base_currency_amount_needed_to_buy': buy_volume + (pair_data['maker_fee'] * buy_volume),
            'have_quote_currency_to_sell': quote_balance > sell_volume,
            'quote_currency_amount_needed_to_sell': sell_volume + (pair_data['maker_fee'] * sell_volume),
        }

    def get_account_data(self):
        account_balance = {}
        open_orders = self.k.get_open_orders()
        time.sleep(self.delay)
        closed_orders = self.k.get_closed_orders()
        closed_orders = closed_orders[0].query('status == "closed"', inplace = False)
        #print(closed_orders)
        time.sleep(self.delay)
        account_balance = self.k.get_account_balance()
        #print(account_balance)
        time.sleep(self.delay)
        return {
            "account_balance": account_balance,
            "open_orders": open_orders,
            "closed_orders": closed_orders.loc[:, closed_orders.columns],
        }