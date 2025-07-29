
from SmartApi.smartConnect import SmartConnect
import requests 
import tkinter as tk
import pyotp
import pandas as pd
from datetime import datetime
import math
import time
api_key = 'uQBIgMGv'
username = 'S692948'
pwd = '5472'
# SENSEX25FEB25205PE
# search file
multiple = 1-0
limit = 1000
# tradingsymbollive = "Nifty 50"
# symboltokenlive = "99926000"
tradingsymbollive = "SENSEX"
symboltokenlive = "99919000"
exchlive = "BSE"
exch = "BFO"
livesymbol = ''
livetoken = ''
trigerprice = 0 
Quan = 0 
time100 = '09:50:00'
time110 =  '09:55:00'
time120 =  '10:00:00'
time3pm = '10:05:00'
time305 =  '10:20:00'
time310 =  '10:25:00'
time315 =  '10:30:00'
time211 = '10:40:00'
timep212 =  '10:35:00'
timempm = '10:45:00'
timep5 =  '10:50:00'
time201 = '10:55:00'
time202 =  '11:00:00'
time203 =  '11:05:00'
time204 =  '11:10:00'
time205 = '11:15:00'
time206 =  '11:20:00'
time207 = '11:25:00'
time208 =  '11:30:00'
time209 =  '10:15:00'
time210 =  '10:10:00'

time1001 = '11:45:00'
time1101 =  '11:50:00'
time1201 =  '11:55:00'
time3pm1 = '12:00:00'
time3051 =  '12:05:00'
time3101 =  '12:10:00'
time3151 =  '12:15:00'
time2111 = '12:20:00'
timep2121 = '12:25:00'
timempm1 = '12:30:00'
timep51 =  '12:35:00'
time2011 = '12:45:00'
time2021 =  '12:40:00'
time2031 =  '12:50:00'
time2041 =  '12:55:00'
time2051 = '13:00:00'
time2061 =  '13:05:00'
time2071 = '13:10:00'
time2081 =  '13:15:00'
time2091 =  '13:20:00'
time2101 =  '09:55:00'





#  NFO     BFO

 
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
response.close()

try:
    token = "CESGV6Z4HHXCIZHQPL3CUFK6ZU"
    totp = pyotp.TOTP(token).now()
except Exception as e:
    print("Invalid Token: The provided token is not valid.")
    raise e

correlation_id = "abcde"
smartApi = SmartConnect(api_key)
data = smartApi.generateSession(username, pwd, totp)
if data['status'] == False:
    print('error')
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
    margin = 7500

while(True):

    while(True):
       
      now = datetime.now()
      trigerprice = 0
      ordercount = 0
      Quan = 0
      i = 1
      formatted_now = now.strftime("%H:%M:%S")
      
      # Method 1: Place an order and return the order ID
      if(formatted_now == time3pm or formatted_now == time310  or formatted_now == time305 or 
         formatted_now == time315 or formatted_now == timempm  or formatted_now == timep5 or
          formatted_now == time201 or formatted_now == time202  or formatted_now == time203 or 
         formatted_now == time204 or formatted_now == time205  or formatted_now == time206 or
          formatted_now == time207 or formatted_now == time208  or formatted_now == time209 or 
         formatted_now == time210 or formatted_now == time211  or formatted_now == timep212 or
          formatted_now == time100 or formatted_now == time110  or formatted_now == time120 
           
            ):
        
        print(exchlive)
        livedata=smartApi.ltpData(exchlive, tradingsymbollive, symboltokenlive)
        livedata=smartApi.ltpData(exchlive, tradingsymbollive, symboltokenlive)
        livedata = livedata['data']    
        livedata = livedata['ltp']
        livedata = round(livedata/multiple)*multiple
        print(int(livedata))
        livedata = str(livedata )
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
        
        # scriptcesymbol = 'NIFTY' + '10'  + "JUL" + year+ livedata  + 'CE'
        # scriptpesymbol = 'NIFTY' + '10' + "JUL" + year + livedata  + 'PE'

        scriptcesymbol = 'SENSEX' + "257" + "15" +  livedata  + 'CE'
        scriptpesymbol = 'SENSEX' + "257"  + "15" +  livedata  + 'PE'
        
        
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
        "price": ltp_value,
        "squareoff": "0",
        "stoploss": "0",
        "quantity": Quantity
        }
        # if(lotsize*i*float(buyvalue) < 4000):
        #    orderid = smartApi.placeOrder(orderparams)

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
        
        
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1.03*(float(buyvalue))
        highersell = 1.05*(float(buyvalue))
        highermore = 1.12*(float(buyvalue))
        # print(ltp_value)
        # print(sellvalue)
        if(float(ltp_value) >sellvalue):
           
            newselltrigerprice =  math.ceil(0.975*(float(ltp_value)) * 10) / 10
            if(float(ltp_value) >highersell):
              newselltrigerprice =  math.ceil(0.965*(float(ltp_value)) * 10) / 10
            
            if(float(ltp_value) > highermore):
              newselltrigerprice =  math.ceil(0.955*(float(ltp_value)) * 10) / 10


            if(newselltrigerprice>= trigerprice):
               trigerprice = newselltrigerprice
               
             # stoploss at 60% loss
        if(float(ltp_value) < 0.92*float(buyvalue)):
            orderparams = {
                "variety": "NORMAL",
              "tradingsymbol": tradingsymbol,
                "symboltoken": symboltoken,
                "transactiontype": "SELL",
               "exchange": exch,
               "ordertype": "MARKET",
               "producttype": "INTRADAY",
               "duration": "DAY",
                "price": ltp_value  ,
                "squareoff": "0",
              "quantity": Quantity
                }
            print(datetime.now())
            orderid = smartApi.placeOrder(orderparams)
            # if(lotsize*i*float(buyvalue) < 4000):
            #   orderid = smartApi.placeOrder(orderparams)

            ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
            ltp_value = ltp_data['data']['ltp'] 
            sellvalue = (float(buyvalue))
            
            
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
                "price": ltp_value  ,
                "squareoff": "0",
              "quantity": Quantity
                }
           orderid = smartApi.placeOrder(orderparams)
          #  if(lotsize*i*float(buyvalue) < 4000):
          #     orderid = smartApi.placeOrder(orderparams)
           ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
           ltp_value = ltp_data['data']['ltp'] 
           sellvalue = (float(buyvalue))
           print(datetime.now())
           print('sell value')
           print(ltp_value)
           break









       
    
    
    