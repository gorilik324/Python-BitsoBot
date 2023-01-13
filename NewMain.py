import bitso
from extras.ordertree import OrderTree

import threading
import time

import datetime as dt
from bot import Bot

# FUNCIONES PROPORCIONADAS POR BITSO: LiveOrderBook,merge_orders  ----------
class LiveOrderBook(object):
    def __init__(self, rest_book):
        self.bids = OrderTree()
        self.asks = OrderTree()

        for bid in rest_book.bids:
            self.bids.insert_price(bid.price, bid.amount, bid.oid)
        for ask in rest_book.asks:
            self.asks.insert_price(ask.price, ask.amount, ask.oid)

# define a thread which takes input
class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread, self).__init__()
        self.daemon = True
        self.user_input = None

    def run(self):
        while True:
            self.user_input = input('\n')
            # let main do something with self.user_input
            print(f'\nUSER: {self.user_input}') 

            if self.user_input == "get_balance":
                bot.get_balance()
            elif self.user_input == "last price": 
                print(f"ANSWER LAST PRICE: \033[91m${listener.last_price}\033[0m\n")
            elif self.user_input == "status": 
                print(f"ANSWER BOT STATUS: \033[91m${bot.gridIndex}\033[0m\n")
                
class UpdateBot(threading.Thread):
    def __init__(self):
        super(UpdateBot, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            bot.update()
            time.sleep(20)


class BasicBitsoListener(bitso.bitsows.Listener):
    def __init__(self):
        self.order_book = None
        self.last_price = 1
        
    def on_connect(self):
        api = bitso.Api()

        self.last_price = float(api.ticker(market).last)

        rest_book = api.order_book(market, aggregate=False)
        self.order_book = LiveOrderBook(rest_book)
        
    def on_update(self, message):
        try:
            if message.channel == 'trades':
                *_, last = message.updates
                change = round(float(last.rate)/self.last_price - 1,4) * 100

                print(dt.datetime.now(), 'TRADE @',f'\033[1m\033[91m ${last.rate}\033[0m {change}%')
                print(f'Best ask: {self.order_book.asks.min_price}, Best bid: {self.order_book.bids.max_price}, Spread: {self.order_book.asks.min_price - self.order_book.bids.max_price}\n')

                self.last_price = float(last.rate)
            else:
                self.merge_orders(message.updates)
        except:
            print("!")
    
    def on_close(self, **kwargs):
        pass

    def merge_orders(self, orders):
        for order in orders:
            tree = self.order_book.bids if order.side == 'bid' else self.order_book.asks
            tree.insert_price(order.rate, order.amount, order.oid)


        
if __name__ == '__main__':
    it = InputThread()
    up = UpdateBot()
    market   = input('Enter book: ')
    
    bot = Bot(market)
    up.start()
    it.start()

    listener = BasicBitsoListener()
    client   = bitso.bitsows.Client(listener)
    channels = ['trades','diff-orders']
    book     = market 
    client.connect(channels, book)
    