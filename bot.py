from os import environ
import time
import robin_stocks as rs
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import pyotp

EMAIL = environ['EMAIL']
ROBINHOOD_PASSWORD = environ['ROBINHOOD_PASSWORD']
ALPHA_VANTAGE_KEY = environ['ALPHA_VANTAGE_KEY']
AUTH = environ['AUTH']

scheduler = BlockingScheduler()

# authenticate
totp = pyotp.TOTP(AUTH).now()
print("Current OTP:", totp)
rs.login(EMAIL, ROBINHOOD_PASSWORD, mfa_code=totp)
         
def get_stock_data(symbol):
    # make API  request to get stock data
    response = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + symbol + '&apikey=' + ALPHA_VANTAGE_KEY)
    data = response.json()['Time Series (Daily)']
    thirtyDayAVG = 0.0
    hundredDayAVG = 0.0
    counter = 0
    closingData = []
    thirtyAndHundred = []

    for key, value in data.items():
        currentClose = value['4. close']
        closingData.append(currentClose)
    
    #Calculates the 30 day avg
    for closingPrice in closingData:
        if counter < 30:
            thirtyDayAVG += float(closingPrice)
        hundredDayAVG += float(closingPrice)
        counter += 1

    thirtyDayAVG /= 30
    hundredDayAVG /= 100
    thirtyAndHundred.append(thirtyDayAVG)
    thirtyAndHundred.append(hundredDayAVG)

    print("The thirty day moving average: $" + str(thirtyDayAVG))
    print("The hundred day moving average: $" + str(hundredDayAVG))

    return thirtyAndHundred

def buy_stock(ammountInDollars, symbol):
    try:
        rs.orders.order_buy_fractional_by_price(symbol,
                                        ammountInDollars,
                                        timeInForce='gfd',
                                        extendedHours=False)
        print("purchased " + symbol) #pretty this up
    except Exception as e:
        print("Error Buying:", e)

def sell_stock(ammountInDollars, symbol):
    try:
        rs.orders.order_sell_fractional_by_price(symbol,
                                        ammountInDollars,
                                        timeInForce='gfd',
                                        extendedHours=False)
        print("purchased " + symbol) #pretty this up
    except Exception as e:
        print("Error Selling:", e)

    

AMOUNT_IN_DOLLARS = 1.0
SYMBOL = 'AMD'

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=18)
def start_bot():
    stockInfo = get_stock_data(SYMBOL)
    
    thirtyDayAvg = stockInfo[0]
    hunderedDatAvg = stockInfo[1]

    if thirtyDayAvg > hunderedDatAvg:
        buy_stock(AMOUNT_IN_DOLLARS, SYMBOL)
    else: 
        # sell_stock(AMOUNT_IN_DOLLARS, SYMBOL)
    rs.logout()

