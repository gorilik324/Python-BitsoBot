import bitso
import os
from dotenv import load_dotenv
import datetime as dt

from extras.taapi import FetchIndicators

load_dotenv() 

class Bot:
    init_balance = init_logs = 0

    def __init__(self,coin):
        # INITIATE API
        API_KEY = os.getenv("API_KEY")
        API_SECRET = os.getenv("API_SECRET")

        self.api = bitso.Api(API_KEY, API_SECRET) 
        balances = self.api.balances()
        self.gridIndex = 'hold'

        #ESTABLISH COIN NAMES
        self.minor_name = coin[4:7] 
        self.major_name = coin[:3]

        #ESTABLISH COINS CURRENT PRICES
        self.minor_price = float(self.api.ticker(self.minor_name + "_" + "mxn").last)
        self.major_price = float(self.api.ticker(self.major_name + "_" + self.minor_name).last)

        #ESTABLISH COINS CURRENT BALANCES
        self.minor_balanace = round(float(getattr(balances, self.minor_name).available),2)
        self.major_balanace = round(float(getattr(balances, self.major_name).available),2)

        # START LOGGING     
        print('\n============== Starting Bot ==============')
        print(' ------ ' + str(dt.datetime.now()) + ' ------ ')
        self.writeLog('Starting Bot')

        # START WITH HALF OG BOTH COINS
        self.buy(amount= self.minor_balanace/2)
        self.get_balance()
     
# Print methods ------------------------------------------------------------

    def get_balance(self):

        # UPDATE COINS CURRENT BALANCES
        balances = self.api.balances()
        self.minor_balanace = round(float(getattr(balances, self.minor_name).available),2)
        self.major_balanace = round(float(getattr(balances, self.major_name).available),2)

        # GET BALANCE IN FIAT *MXN
        mxn = round(self.minor_balanace * self.minor_price + self.major_balanace * self.major_price,2)
        message = f'BALANCE {self.minor_name.upper()}: '+ str(self.minor_balanace) + f', {self.major_name.upper()}: ' + str(self.major_balanace) + f' ---> TOTAL: {mxn} MXN\n'
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
     
# Important methods ------------------------------------------------------------

    def buy(self,amount):
        book = self.major_name + "_" + self.minor_name
        coin = amount/self.major_price

        if self.minor_balanace >= amount:
            # order = self.api.place_order(book=book, side='buy', order_type='limit', major=coin, price=self.major_price)
            
            message = '********* BOUGHT ' + format(coin,'.2f') + ' ' + self.major_name.upper() + ' @ ' + str(self.major_price) + ' MXN *********'
            self.writeLog(message)
        else:
            print(f'NOT ENOUGH {self.minor_name.upper()}')
   
    def sell(self,amount):
        if self.major_balanace > amount:
            book = self.major_name + "_" + self.minor_name
            # order = self.api.place_order(book=book, side='sell', order_type='limit', major=amount, price=self.major_price)
            
            message = '********* SOLD ' + format(amount,'.2f') + ' ' + self.major_name.upper() + ' @ ' + str(self.major_price) + ' MXN *********' 
            self.writeLog(message)
        else:
            print(f'NOT ENOUGH {self.major_name.upper()}')
       

    def update(self):
        # BitsoBook = self.api.available_books()
        # BitsoBook.btc_usdt.minimum_value  # Minor
        try:
            self.major_price = float(self.api.ticker(self.major_name + "_" + self.minor_name).last)
            self.Logic()

            if self.gridIndex == 'hold':
                pass
            else:
                print("\n*** UPDATING BOT ***")
                
                if self.gridIndex == 'sell-all': self.sell(self.major_balanace)
                elif self.gridIndex == 'buy':    self.buy(1)
                elif self.gridIndex == 'sell':   self.sell(1)
                
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
                    self.gridIndex = 'buy'
                elif rsi == 'Sell':
                    self.gridIndex = 'hold'     
            elif macd == 'Sell':
                if rsi == 'Buy':
                    self.gridIndex = 'hold'
                elif rsi == 'Sell':
                    self.gridIndex = 'sell' 
            else:
                self.gridIndex = 'hold'
        except:
            self.gridIndex = 'hold'
        print(f'\nSTATUS: {self.gridIndex}, RSI: {rsi}, MACD:{macd}\n')
