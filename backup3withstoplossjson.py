from logzero import logger
from SmartApi.smartConnect import SmartConnect
import requests 
import pyotp
import pandas as pd
import time
from datetime import datetime
import math
api_key = 'uQBIgMGv'
username = 'S692948'
pwd = '5472'
# SENSEX25FEB25205PE
# search file
tradingsymbol = 'NIFTY27FEB2522550PE'
# tradingsymbol = 'SENSEX25FEB74500CE'
symboltoken = ''
symboltoken = 'NSE'
# mu;tipleof 20
Quantity = '140'   
time3pm = '16:39:00'
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
print(result)
token_value = result['token'].values[0]
lotsize = result['lotsize'].values[0]
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
    # if(now == 1):
    #    exch = "BFO"
    #    print
    # if(now == 3):
    #    exch = "NSE"

# Check if 'tradingsymbol' exists
# Get the first matching value
        
    
    while(True):
      now = datetime.now()
      formatted_now = now.strftime("%H:%M:%S")
      # Method 1: Place an order and return the order ID
      if(formatted_now <= time3pm):
       
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        buyvalue = float(ltp_value) 
        buyvalue = str(buyvalue)
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
        print(datetime.now())
        
        break
       # Method 2: Place an order and return the full response
    while(True):
        # time.sleep(0.1)
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1.15*(float(buyvalue))
        
        
        if(float(ltp_value) >sellvalue):
            print('1.20 times buy price')
            print(sellvalue)
            print(ltp_value)
            newsell = str(math.ceil(0.87* (float(buyvalue)) * 10) / 10)
            price =  math.ceil(0.87* (float(buyvalue)) * 10) / 10
            price = 0.97*price
            price =  math.ceil((float(price)) * 10) / 10
            price = str(price)
            orderparams = {
                "variety": "STOPLOSS",
              "tradingsymbol": tradingsymbol,
                "symboltoken": symboltoken,
                "transactiontype": "SELL",
               "exchange": exch,
               "ordertype": "STOPLOSS_LIMIT",
               "producttype": "INTRADAY",
               "duration": "DAY",
                "price": price  ,
                "squareoff": "0",
              "triggerprice": newsell,
              "quantity": Quantity
                }
            orderid = smartApi.placeOrder(orderparams)
            
            print('sell order' )
            print(datetime.now())
            print(newsell)
            break
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
            orderid = smartApi.placeOrder(orderparams)
            break
    while(True):
        # time.sleep(0.1)
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1.20* (float(buyvalue))
        
        if(float(ltp_value)>sellvalue):
        #   newsell = math.floor((0.85* (int(ltp_value)) * 10) / 10) - 130)
          
          if(i==0):
           newsell = str(math.ceil(0.88* (float(ltp_value)) * 10) / 10)
           
           price =  math.ceil(0.88* (float(ltp_value)) * 10) / 10
           price = 0.97*price
           price =  math.ceil((float(price)) * 10) / 10
           price = str(price)


           print('first modify')
           print(datetime.now())
           print(newsell)
           modifyparams = {
        "variety": "STOPLOSS",
        "orderid": orderid,
        "ordertype": "STOPLOSS_LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": price,
        "quantity": Quantity,
        "triggerprice": newsell,
        "tradingsymbol": tradingsymbol,
        "symboltoken": symboltoken,
        "exchange": exch
        
        }
           smartApi.modifyOrder(modifyparams)
           i = i + 1
           lastmodified = float(ltp_value)
           print( i)
          if(i>0 and lastmodified < float(ltp_value) ):
             newsell = str(math.ceil(0.88* (float(ltp_value)) * 10) / 10)
             
             price =  math.ceil(0.88* (float(ltp_value)) * 10) / 10
             price = 0.97*price
             price =  math.ceil((float(price)) * 10) / 10
             price = str(price)


             print('2nd modify')
             print(datetime.now())
             print(newsell)
             modifyparams = {
        "variety": "STOPLOSS",
        "orderid": orderid,
        "ordertype": "STOPLOSS_LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": price,
        "quantity": Quantity,
        "triggerprice": newsell,
        "tradingsymbol": tradingsymbol,
        "symboltoken": symboltoken,
        "exchange": exch
        }    
             smartApi.modifyOrder(modifyparams)
             i = i + 1
             lastmodified = float(ltp_value)
             

    

    

    

    

    

    

    
    

    

    ########################### SmartWebSocket OrderUpdate Sample Code Start Here ###########################
    
    ########################### SmartWebSocket OrderUpdate Sample Code End Here ###########################