#!/usr/bin/env python
import app.trader as t

class Heartbeat:
    def run(self):
        trader = t.Trader()
        trader.go()

def main():
  heartbeat = Heartbeat()
  heartbeat.run()