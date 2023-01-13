import requests
import json
import os
from dotenv import load_dotenv

load_dotenv() 

url = "https://api.taapi.io/bulk"
payload = {
    "secret": os.getenv("TAAPI_API_KEY"),
    "construct": {
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "interval": "1m",
        "indicators": [
            {"indicator": "stochrsi","backtracks":5,"kPeriod":20,"dPeriod":10,"rsiPeriod":15,"stochasticPeriod":30}, 
            {"indicator": "macd","backtracks":5}]
    } 
}

def FetchIndicators():
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers)
    response = json.loads(response.text)

    try:
        # RSI OPERATION should return min and max value 
        rsi = [backtrack['result']['valueFastD'] for backtrack in response['data'][0:5]]
        rsi = RsiSignal(rsi)

        # MACD OPERATION should return TRUE if cross apreared in period and direction of trend
        valueMACDHist   = [backtrack['result']['valueMACDHist'] for backtrack in response['data'][5:10]]
        signal = getSignal(valueMACDHist)
        
        return({'RSI': rsi,'MACD':signal})
    except:
        print('Error in FetchIndicator')

def getSignal(valueMACDHist):
    trends = [value >= 0 for value in valueMACDHist]
    signals = []
    for i in range(1,len(trends)):
        if (not trends[i]) & trends[i-1]:
            signals.append('Buy')
        elif trends[i] & (not trends[i-1]):
            signals.append('Sell')
    try:
        return(signals[0])
    except:
        return('Hold')
def RsiSignal(rsi):
    signals =  list(filter(None,['Sell' if value >= 80 else 'Buy' if value <= 20 else None for value in rsi]))
    try:
        return(signals[0])
    except:
        return('Hold')