from binance.client import Client
from datetime import date
from time import sleep
import pyrebase
from config import configs
config_data = configs()
firebase = pyrebase.initialize_app(config_data.FireBaseconfig)
db = firebase.database()
db.child("Trading Bots").child("CopyTrades").set({"Balance":0})


client = Client(config_data.BinanceAPIKey, config_data.BinanceAPISecretKey)

class BTCUSDT_Bot:
    

    def __init__(self, gapSize, balance, sample_time, order_time):
        self.gapSize = gapSize
        self.balance = balance
        self.sample_time = sample_time
        self.order_time = order_time
        self.BTCGap = [0,0]

    
    def start(self):
        raw = client.get_recent_trades(symbol='BTCUSDT')
        self.BTCGap[0] = int(float(raw[0]["price"]))
        sleep(self.sample_time)
        raw = client.get_recent_trades(symbol='BTCUSDT')
        self.BTCGap[1] = int(float(raw[0]["price"]))
        while True:

            self.BTCGap[1] = self.BTCGap[0]
            raw = client.get_recent_trades(symbol='BTCUSDT')
            self.BTCGap[0] = int(float(raw[0]["price"]))
            gap = self.BTCGap[0] - self.BTCGap[1]

            if gap >= self.gapSize:
                
                print("buy")
                self.buy_order()

                raw = client.get_recent_trades(symbol='BTCUSDT')
                self.BTCGap[0] = int(float(raw[0]["price"]))
                sleep(self.sample_time)
                raw = client.get_recent_trades(symbol='BTCUSDT')
                self.BTCGap[1] = int(float(raw[0]["price"]))
                
                

            if gap <= (0 - self.gapSize):
                
                print("sell")
                self.sell_order()

                raw = client.get_recent_trades(symbol='BTCUSDT')
                self.BTCGap[0] = int(float(raw[0]["price"]))
                sleep(self.sample_time)
                raw = client.get_recent_trades(symbol='BTCUSDT')
                self.BTCGap[1] = int(float(raw[0]["price"]))

            print("Balance: ",self.balance)
            db.child("Trading Bots").child("CopyTrades").update({"Balance":self.balance})
            sleep(self.sample_time)
            
            
    def buy_order(self):
        raw = client.futures_coin_symbol_ticker(symbol="BTCUSD_210625")
        BTCUSDT_futures = float(raw[0]["price"])

        quantity = (self.balance*0.1)/BTCUSDT_futures
        self.balance = self.balance - self.balance*0.1

        sleep(self.order_time)
        raw = client.futures_coin_symbol_ticker(symbol="BTCUSD_210625")
        BTCUSDT_futures = float(raw[0]["price"])

        self.balance = self.balance + (quantity * BTCUSDT_futures)
        


    def sell_order(self):
        raw = client.futures_coin_symbol_ticker(symbol="BTCUSD_210625")
        BTCUSDT_futures = float(raw[0]["price"])

        quantity = (self.balance*0.1)/BTCUSDT_futures

        sleep(self.order_time)
        raw = client.futures_coin_symbol_ticker(symbol="BTCUSD_210625")
        BTCUSDT_futures = float(raw[0]["price"])

        PandL = -((quantity * BTCUSDT_futures) - self.balance*0.1)
        print(PandL)
        self.balance = self.balance + PandL
        

    def get_gap(self):
        return self.BTCGap


b1 = BTCUSDT_Bot(10,10000.0,0.5,2)
b1.start()
