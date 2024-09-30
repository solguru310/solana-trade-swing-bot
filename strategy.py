import ta_signals
import pyangles

class Strategy:
    def setup(self, ohlc, time_frame, pair):
        price = float(ohlc['close'][::-1][0])
        buy = []
        sell = []

        #print(ohlc[['time', 'close', 'volume', 'low', 'high']].to_dict('records'))

        ta_data, ohlc = ta_signals.go(ohlc, 'close')
        pattern_data, lows, highs = pyangles.go(ohlc, 'close', [3, 3], [3, 3])

        #print(lows['close'][-5:])
        #print(highs['close'][-5:])


        data = ta_data + pattern_data


        signals = []
        for signal in data:
            if signal['value']:
                signals.append(signal['key'])

        print(ohlc[['close','rsi','rsi_slope','ema8','ema34','ema8_slope','ema34_slope', 'key_slope']].iloc[-3:])
        print('---------ta_data--------------------')
        print(signals)
        print('---------strategy_data--------------------')
        print(time_frame['buy_signals'])
        print(time_frame['sell_signals'])
        print('------------------------------------')

        for signal_group in time_frame['buy_signals']:
            buy.append(all(item in signals for item in signal_group))

        for signal_group in time_frame['sell_signals']:
            sell.append(all(item in signals for item in signal_group))

        return True in buy, True in sell

