from logzero import logger
from SmartApi.smartConnect import SmartConnect
import requests 
import pyotp
import pandas as pd

from datetime import datetime
import math
api_key = 'uQBIgMGv'
username = 'S692948'
pwd = '5472'
# SENSEX25FEB25205PE
# search file
tradingsymbol = 'SENSEX25FEB74600PE'
# tradingsymbol = 'SENSEX25FEB74500CE'
symboltoken = ''
symboltoken = 'NSE'
# mu;tipleof 20
Quantity = '140' 
trigerprice = 0  
time3pm = '17:54:00'
time305 =  '15:05:00'
time310 =  '15:10:00'
time315 =  '15:15:00'
#  NFO     BFO
exch = ""   
smartApi = SmartConnect(api_key)
orderid = ''
buyvalue = ''
lastmodified = ''
i = 0

url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

response = requests.get(url)
d = response.json()
tokendf = pd.DataFrame.from_dict(d)

tokendf['expiry'] = pd.to_datetime(tokendf['expiry'])
tokendf = tokendf.astype({'strike': float})
# Filter for specific trading symbol

result = tokendf[tokendf['symbol'] == tradingsymbol]
token_value = result['token'].values[0]
lotsize = result['lotsize'].values[0]
lotsize = int(lotsize)
print('lotsize')
print(lotsize)
# Display result
symboltoken = str(token_value)
print('back')
response.close()

try:
    token = "CESGV6Z4HHXCIZHQPL3CUFK6ZU"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
data = smartApi.generateSession(username, pwd, totp)
if data['status'] == False:
    logger.error(data)
else:
    # logger.info(f"data: {data}")
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    feedToken = smartApi.getfeedToken()
    # logger.info(f"Feed-Token :{feedToken}")
    res = smartApi.getProfile(refreshToken)
    # logger.info(f"Get Profile: {res}")
    smartApi.generateToken(refreshToken)
    res=res['data']['exchanges']

    now = datetime.now().today().weekday()
    if(now == 1):
       exch = "BFO"
       print
    if(now == 3):
       exch = "NSE"

# Check if 'tradingsymbol' exists
# Get the first matching value




    cash = smartApi.rmsLimit()
    cash = cash['data']
    cash = cash['availablecash']
    cash = float(cash)
    margin = 0.1*cash
    
    while(True):
      now = datetime.now()
      formatted_now = now.strftime("%H:%M:%S")
      # Method 1: Place an order and return the order ID
      if(formatted_now == time3pm):
       
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        buyvalue = float(ltp_value) 
        buyvalue = str(buyvalue)
        # while(True):
        #    if(lotsize*i*float(ltp_value) < margin):
        #     Quantity = lotsize*i
        #     Quantity = str(Quantity)
        #     print(Quantity)
        #     i = i+1
        #    else:
        #       break
        Quantity = lotsize

        orderparams = {
            "variety": "NORMAL",
        "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken,
            "transactiontype": "BUY",
        "exchange": exch,
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": ltp_value,
        "squareoff": "0",
        "stoploss": "0",
        "quantity": Quantity
        }
        orderid = smartApi.placeOrder(orderparams)
        print('buy order ')
        break
       # Method 2: Place an order and return the full response




    while(True):
        # time.sleep(0.1)
        print('here also for sell')
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1.15*(float(buyvalue))
        print(ltp_value)
        print(sellvalue)
        if(float(ltp_value) >sellvalue):
            print('1.20 times buy price')
            print(sellvalue)
            print(ltp_value)
            newselltrigerprice =  math.ceil(0.88*(float(ltp_value)) * 10) / 10
            if(newselltrigerprice>= trigerprice):
               trigerprice = newselltrigerprice

            
        if(float(ltp_value) < 0.35*float(buyvalue)):
            orderparams = {
                "variety": "NORMAL",
              "tradingsymbol": tradingsymbol,
                "symboltoken": symboltoken,
                "transactiontype": "SELL",
               "exchange": exch,
               "ordertype": "MARKET",
               "producttype": "INTRADAY",
               "duration": "DAY",
                "price": "0"  ,
                "squareoff": "0",
              "quantity": Quantity
                }
            print('sell at 0.55')
            orderid = smartApi.placeOrder(orderparams)
            break
    
        if(float(ltp_value)<trigerprice):
           orderparams = {
                "variety": "NORMAL",
              "tradingsymbol": tradingsymbol,
                "symboltoken": symboltoken,
                "transactiontype": "SELL",
               "exchange": exch,
               "ordertype": "MARKET",
               "producttype": "INTRADAY",
               "duration": "DAY",
                "price": "0"  ,
                "squareoff": "0",
              "quantity": Quantity
                }
           print('sell at 2.15')
           orderid = smartApi.placeOrder(orderparams)
           break
    
    
    
    
    
    