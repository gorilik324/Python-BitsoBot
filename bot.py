from colorama import Fore,Back,Style, init
from dotenv import load_dotenv
import datetime as dt
import math
# import time
import bitso
import os

from extras.taapi import FetchIndicators
    
init(autoreset=True)
load_dotenv() 

class Bot:
    init_balance = init_logs = init_trades = 0

    def __init__(self,coin):
        # INITIATE API
        API_KEY = os.getenv("API_KEY")
        API_SECRET = os.getenv("API_SECRET")

        self.api = bitso.Api(API_KEY, API_SECRET) 
        self.gridIndex = 'Hold'

        #ESTABLISH COIN NAMES
        self.minor_name = coin[4:] 
        self.major_name = coin[:3]
        
        # ESTABLISH MINIMUMS
        books = self.api.available_books() 

        self.minimum_value = getattr(books, coin).minimum_value
        self.minimum_amount= getattr(books, coin).minimum_amount

        # START LOGGING     
        print('\n============== Starting Bot ==============')
        print(' ------ ' + str(dt.datetime.now()) + ' ------ ')
        self.writeLog('Starting Bot')

        #ESTABLISH COINS CURRENT PRICES
        self.major_price = float(self.api.ticker(self.major_name + "_" + self.minor_name).last)
        try:
            self.minor_price = float(self.api.ticker(self.minor_name + "_mxn").last)
        except:
            major_mxn = float(self.api.ticker(self.major_name + "_mxn").last)
            self.minor_price = major_mxn/self.major_price 
        
        #ESTABLISH COINS CURRENT BALANCES
        self.get_balance()

# Print methods ------------------------------------------------------------

    def get_balance(self):

        # UPDATE COINS CURRENT BALANCES
        balances = self.api.balances()
        self.minor_balance = float(getattr(balances, self.minor_name).available)
        self.major_balance = float(getattr(balances, self.major_name).available)

        # GET BALANCE IN FIAT *MXN
        mxn = (self.minor_balance * self.minor_price) + (self.major_balance * self.major_price * self.minor_price)
        message = f'{self.minor_name.upper()}:  {self.minor_balance:.4f} + {self.major_name.upper()}: {self.major_balance:.6f} ---> TOTAL: {mxn:,.2f} MXN\n'
        print(message)

        if self.init_balance == 0:
            self.init_balance = 1
            f = open(r'logs/balance.txt','w+')
        else:
            f = open(r'logs/balance.txt','a')
        f.write(str(dt.datetime.now()) +';'+ message + '\n')
        f.close()

    def writeLog(self,message):
        if self.init_logs == 0:
            self.init_logs = 1
            f = open(r'logs/log.txt','w+')
        else:
            f = open(r'logs/log.txt','a')
        f.write(str(dt.datetime.now()) + ' --- ' + message + '\n')
        f.close()

# Important methods ------------------------------------------------------------

    def buy(self,amount):
        book = self.major_name + "_" + self.minor_name
        coins = (math.floor(amount*10)/10)/self.major_price
        if (self.minor_balance >= amount) and (amount >= self.minimum_value):
            print("\n" + Fore.GREEN + "--- BUYING ---")
            order = self.api.place_order(book=book, side='buy', order_type='market', minor=f'{amount:.8f}'[:8])

            print(f'{Style.BRIGHT + Fore.GREEN}********* BOUGHT {coins:.6f}  {self.major_name.upper()}  @ {self.major_price:,.2f}  {self.minor_name.upper()} *********{Style.RESET_ALL}')
            self.writeLog(f'********* BOUGHT {coins:.6f}  {self.major_name.upper()}  @ {self.major_price:,.2f}  {self.minor_name.upper()} *********')
            self.writeLog(f"\nORDER ID: {order['oid']}")
        else:
            print(f'NOT ENOUGH {self.minor_name.upper()}')
   
    def sell(self,amount):
        if (self.major_balance >= amount) and (amount >= self.minimum_amount):
            book = self.major_name + "_" + self.minor_name
            print("\n" + Fore.RED +  "--- SELLING ---")
            order = self.api.place_order(book=book, side='sell', order_type='market', major=f'{amount:.8f}'[:8])
            
            print(f'{Style.BRIGHT + Fore.RED}********* SOLD {amount:.6f} {self.major_name.upper()} @ {self.major_price:,.2f} {self.minor_name.upper()} *********{Style.RESET_ALL}' )
            self.writeLog(f'********* SOLD {amount:.6f} {self.major_name.upper()} @ {self.major_price:,.2f} {self.minor_name.upper()} *********')
            self.writeLog(f"\nORDER ID: {order['oid']}")
        else:
            print(f'NOT ENOUGH {self.major_name.upper()}')
       

    def update(self):
        try:
            self.major_price = float(self.api.ticker(self.major_name + "_" + self.minor_name).last)
            print(str(dt.datetime.now()) + f' {self.major_name.upper()} @ ' + Style.BRIGHT + f'${self.major_price:,.0f}' + Style.RESET_ALL)

            self.Logic()

            if self.gridIndex == 'Hold':
                pass
            else:                
                if self.gridIndex == 'Buy':    
                    self.buy(self.minor_balance)
                    
                elif self.gridIndex == 'Sell':   
                    self.sell(self.major_balance)
                self.get_balance()
        except:
            pass

    def Logic(self):        
        fetch = FetchIndicators()
        try:
            rsi    = fetch['RSI']
            macd   = fetch['MACD']

            if macd == 'Buy':
                if rsi == 'Buy':
                    self.gridIndex = 'Buy'
                elif rsi == 'Sell':
                    self.gridIndex = 'Hold'     
            elif macd == 'Sell':
                if rsi == 'Buy':
                    self.gridIndex = 'Hold'
                elif rsi == 'Sell':
                    self.gridIndex = 'Sell' 
            else:
                self.gridIndex = 'Hold'
        except:
            self.gridIndex = 'Hold'
