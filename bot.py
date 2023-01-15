from colorama import Fore,Back,Style, init
from dotenv import load_dotenv
import datetime as dt
import time
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
        balances = self.api.balances()
        self.gridIndex = 'Hold'

        #ESTABLISH COIN NAMES
        self.minor_name = coin[4:] 
        self.major_name = coin[:3]

        #ESTABLISH COINS CURRENT BALANCES
        self.minor_balance = round(float(getattr(balances, self.minor_name).available),2)
        self.major_balance = round(float(getattr(balances, self.major_name).available),2)

        #ESTABLISH COINS CURRENT PRICES
        self.major_price = float(self.api.ticker(self.major_name + "_" + self.minor_name).last)
        try:
            self.minor_price = float(self.api.ticker(self.minor_name + "_mxn").last)
        except:
            major_mxn = float(self.api.ticker(self.major_name + "_mxn").last)
            self.minor_price = major_mxn/self.major_price 

        # START LOGGING     
        print('\n============== Starting Bot ==============')
        print(' ------ ' + str(dt.datetime.now()) + ' ------ ')
        self.writeLog('Starting Bot')

# Print methods ------------------------------------------------------------

    def get_balance(self):

        # UPDATE COINS CURRENT BALANCES
        balances = self.api.balances()
        self.minor_balance = float(getattr(balances, self.minor_name).available)
        self.major_balance = float(getattr(balances, self.major_name).available)

        # GET BALANCE IN FIAT *MXN
        mxn = self.minor_balance * self.minor_price + self.major_balance * self.major_price
        message = f'{self.minor_name.upper()}:  {self.minor_balance:.4f} + {self.major_name.upper()}: {self.major_balance:.6f} ---> TOTAL: {mxn:.2f} MXN\n'
        self.writeLog(message)
        print(message)


        if self.init_balance == 0:
            self.init_balance = 1
            f = open(r'logs\balance.txt','w+')
        else:
            f = open(r'logs\balance.txt','a')
        f.write(str(dt.datetime.now()) +';'+ str(mxn) + '\n')
        f.close()

    def writeLog(self,message):
        if self.init_logs == 0:
            self.init_logs = 1
            f = open(r'logs\log.txt','w+')
        else:
            f = open(r'logs\log.txt','a')
        f.write(str(dt.datetime.now()) + ' --- ' + message + '\n')
        f.close()
     
    def open_orders(self):
        book = self.major_name + "_" + self.minor_name
        oo = self.api.open_orders(book)
        print(oo)
    
    def trades(self):
        book = self.major_name + "_" + self.minor_name
        utx = self.api.user_trades(book)
        
        print("UPDATING trades.txt")
        try:
            if self.init_trades == 0:
                self.init_trades = 1
                f = open(r'logs\trades.txt','w+')
            else:
                f = open(r'logs\trades.txt','a')
            f.write(utx)
            f.close()
            print('Update completed')
        except:
            print("Error updating trades.csv") 

# Important methods ------------------------------------------------------------

    def buy(self,amount):
        book = self.major_name + "_" + self.minor_name
        coins = round(amount,1)/self.major_price
        if self.minor_balance >= amount:
            order = self.api.place_order(book=book, side='buy', order_type='market', major=f'{coins:.8f}')

            print(f'{Style.BRIGHT + Fore.GREEN}********* BOUGHT {coins:.6f}  {self.major_name.upper()}  @ {self.major_price:.2f}  MXN *********{Style.RESET_ALL}')
            self.writeLog(f'********* BOUGHT {coins:.6f}  {self.major_name.upper()}  @ {self.major_price:.2f}  MXN *********')
            self.writeLog(f"Buy order id: {order['oid']}")
        else:
            print(f'NOT ENOUGH {self.minor_name.upper()}')
   
    def sell(self,amount):
        if self.major_balance > amount:
            book = self.major_name + "_" + self.minor_name
            order = self.api.place_order(book=book, side='sell', order_type='market', major=f'{amount:.8f}')
            
            print(f'{Style.BRIGHT + Fore.RED}********* SOLD {amount:.6f} {self.major_name.upper()} @ {self.major_price} MXN *********{Style.RESET_ALL}' )
            self.writeLog(f'********* SOLD {amount:.6f} {self.major_name.upper()} @ {self.major_price} MXN *********')
            self.writeLog(f"Sell order id: {order['oid']}")
        else:
            print(f'NOT ENOUGH {self.major_name.upper()}')
       

    def update(self):
        try:
            self.major_price = float(self.api.ticker(self.major_name + "_" + self.minor_name).last)
            print(str(dt.datetime.now()) + f' {self.major_name.upper()} @ ' + Style.BRIGHT + f'${self.major_price}' + Style.RESET_ALL)

            self.Logic()

            if self.gridIndex == 'Hold':
                pass
            else:                
                if self.gridIndex == 'Buy':    
                    print("\n" + Fore.GREEN + "--- BUYING ---")
                    self.buy(self.minor_balance)
                    
                elif self.gridIndex == 'Sell':   
                    print("\n" + Fore.RED +  "--- SELLING ---")
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
