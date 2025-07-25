from logzero import logger
from SmartApi.smartConnect import SmartConnect
import requests 
import tkinter as tk
import pyotp
import pandas as pd
from datetime import datetime
import math
import time
api_key = ''
username = ''
pwd = ''
# SENSEX25FEB25205PE
# search file
multiple = 50
limit = 1800
tradingsymbollive = "Nifty 50"
symboltokenlive = "99926000"
# tradingsymbollive = "SENSEX"
# symboltokenlive = "99919000"
exchlive = "NSE"
exch = "NFO"
livesymbol = ''
livetoken = ''
trigerprice = 0 
Quan = 0 
time100 = '14:15:00'
time110 =  '14:25:00'
time120 =  '10:20:00'
time3pm = '14:30:00'
time305 =  '14:40:00'
time310 =  '14:35:00'

time315 =  '11:20:00'
timempm = '11:30:00'
timep5 =  '11:40:00'
time201 = '11:50:00'
time202 =  '12:00:00'
time203 =  '12:10:00'
time204 =  '12:20:00'
time205 = '12:30:00'
time206 =  '12:40:00'
time207 = '12:50:00'
time208 =  '13:00:00'
time209 =  '13:10:00'
time210 =  '13:40:00'
time211 = '13:20:00'
timep212 =  '13:30:00'

#  NFO     BFO

   
orderid = ''
buyvalue = ''
lastmodified = ''


url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'

response = requests.get(url)
d = response.json()
tokendf = pd.DataFrame.from_dict(d)
tokendf['expiry'] = pd.to_datetime(tokendf['expiry'])
tokendf = tokendf.astype({'strike': float})
# Filter for specific trading symbol
response.close()

try:
    token = ""
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
smartApi = SmartConnect(api_key)
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

    # now = datetime.now().today().weekday()
    # if(now == 1):
    #    exch = "BFO"
    # if(now == 3):
    #    exch = "NFO"
       

# Check if 'tradingsymbol' exists
# Get the first matching value
    
    

    cash = smartApi.rmsLimit()
    cash = cash['data']
    cash = cash['availablecash']
    cash = float(cash)
    margin = 7000

    
while(True):

    while(True):
       
      now = datetime.now()
      trigerprice = 0
      ordercount = 0
      i = 1
      
      formatted_now = now.strftime("%H:%M:%S")
      # Method 1: Place an order and return the order ID
      if(formatted_now == time3pm or formatted_now == time310  or formatted_now == time305 or 
         formatted_now == time315 or formatted_now == timempm  or formatted_now == timep5 or
          formatted_now == time201 or formatted_now == time202  or formatted_now == time203 or 
         formatted_now == time204 or formatted_now == time205  or formatted_now == time206 or
          formatted_now == time207 or formatted_now == time208  or formatted_now == time209 or 
         formatted_now == time210 or formatted_now == time211  or formatted_now == timep212 or
          formatted_now == time100 or formatted_now == time110  or formatted_now == time120 ):
        
        print(exchlive)
        livedata=smartApi.ltpData(exchlive, tradingsymbollive, symboltokenlive)
        livedata=smartApi.ltpData(exchlive, tradingsymbollive, symboltokenlive)
        livedata = livedata['data']    
        livedata = livedata['ltp']
        livedata = round(livedata/multiple)*multiple
        print(int(livedata))
        livedata = str(livedata)
        now = str(datetime.now().today().date())
        
        year = now[2:4]
        month = now[5:7]
        date =  now[8:11]
        
        if(month == "02"):
          month = "FEB"
        if(month == "03"):
          month = "MAR"
        if(month == "04"):
          month = "APR"   
        if(month == "05"):
          month = "MAY"  
        
        scriptcesymbol = 'NIFTY' + "03" + "APR" + year+ livedata  + 'CE'
        scriptpesymbol = 'NIFTY' + "03" + "APR" + year + livedata  + 'PE'

        # scriptcesymbol = 'SENSEX' + "25" + "4"+ "01" + livedata  + 'CE'
        # scriptpesymbol = 'SENSEX' + "25"  + "4"+ "01" + livedata  + 'PE'
        
        
        result = tokendf[tokendf['symbol'] == scriptcesymbol]
        
        tokence = result['token'].values[0]
        lotsize = result['lotsize'].values[0]
        lotsize = int(lotsize)
    # Display result
        # print(scriptpesymbol)
        result = tokendf[tokendf['symbol'] == scriptpesymbol]
        tokenpe = result['token'].values[0]
        lotsize = result['lotsize'].values[0]
        lotsize = int(lotsize)
        celtp = smartApi.ltpData(exch, scriptcesymbol, tokence)
        celtp = celtp['data']['ltp']
        peltp = smartApi.ltpData(exch, scriptpesymbol, tokenpe)
        peltp = peltp['data']['ltp']
        # print(celtp)
        # print(peltp)
        if(float(celtp)>=float(peltp)):
         tradingsymbol = scriptpesymbol
        else:
         tradingsymbol =   scriptcesymbol
        print(tradingsymbol)
        Quan = lotsize
        result = tokendf[tokendf['symbol'] == tradingsymbol]
        symboltoken = result['token'].values[0]
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        buyvalue = float(ltp_value) 
        buyvalue = str(buyvalue)
        # code to get quantity
        while(True):
          if(lotsize*i*float(ltp_value) < margin and float(Quan) < limit):
            Quan = lotsize*i
            # print(Quan)
            i = i+1
          else:
              break
        Quantity = str(Quan)   
        # Quantity = str(lotsize)
        
        
        # placing buy order
        orderparams = {
            "variety": "NORMAL",
        "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken,
            "transactiontype": "BUY",
        "exchange": exch,
        "ordertype": "MARKET",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": "0",
        "squareoff": "0",
        "stoploss": "0",
        "quantity": Quantity
        }
        # if(Quan >= limit - lotsize):
        #    while(Quan*i*float(1)*ordercount <= margin):
        #      orderid = smartApi.placeOrder(orderparams)
        #      print(Quan*i*float(1)*ordercount)
        #      ordercount = ordercount + 1

        orderid = smartApi.placeOrder(orderparams)
        print(datetime.now())
        print('buy order ')
        print(buyvalue)
        
        # ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        # ltp_value = ltp_data['data']['ltp']
        # print(ltp_value)
        break
       # Method 2: Place an order and return the full response

    while(True):
        time.sleep(0.35)
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1*(float(buyvalue))
        highersell = 1*(float(buyvalue))
        # print(ltp_value)
        # print(sellvalue)
        if(float(ltp_value) >sellvalue):
           
            newselltrigerprice =  math.ceil(*(float(ltp_value)) * 10) / 10
            if(float(ltp_value) >highersell):
              newselltrigerprice =  math.ceil(*(float(ltp_value)) * 10) / 10
            if(newselltrigerprice>= trigerprice):
               trigerprice = newselltrigerprice
               
             # stoploss at 60% loss
        if(float(ltp_value) < 0.75*float(buyvalue)):
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
            print(datetime.now())
            orderid = smartApi.placeOrder(orderparams)
            
            
            print('sell value')
            print(ltp_value)
            
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
           orderid = smartApi.placeOrder(orderparams)
           print(datetime.now())
           print('sell value')
           print(ltp_value)
           break









       
    
    
    
