from logzero import logger
from SmartApi.smartConnect import SmartConnect
import requests 
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
# tradingsymbol = 'SENSEX25FEB74600PE'
# tradingsymbol = 'SENSEX25FEB74500CE'
multiple = 25
tradingsymbol = "NIFTY MID SELECT"
symboltoken = "99926074"
tradingsymbollive = "NIFTY MID SELECT"
symboltokenlive = "99926074"
Quantity = '140'
exchlive = "NSE"
livesymbol = ''
livetoken = ''
trigerprice = 0  
time3pm = '15:00:00'
time305 =  '15:05:00'
time310 =  '15:10:00'
time315 =  '15:15:00'
#  NFO     BFO

exch = "NFO"   
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
    if(now == 3):
       exch = "NFO"
       

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
      if(formatted_now >= time305):
        print(datetime.now())
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
        
        scriptcesymbol = 'MIDCPNIFTY' + date + month + year+ livedata  + 'CE'
        scriptpesymbol = 'MIDCPNIFTY' + date + month + year + livedata  + 'PE'
        print(scriptpesymbol)
        result = tokendf[tokendf['symbol'] == scriptcesymbol]
        tokence = result['token'].values[0]
        lotsize = result['lotsize'].values[0]
        lotsize = int(lotsize)
    # Display result
        print(scriptpesymbol)
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

        result = tokendf[tokendf['symbol'] == tradingsymbol]
        symboltoken = result['token'].values[0]
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        buyvalue = float(ltp_value) 
        buyvalue = str(buyvalue)
        # code to get quantity
        # while(True):
        #    if(lotsize*i*float(ltp_value) < margin):
        #     Quantity = lotsize*i
        #     Quantity = str(Quantity)
        #     print(Quantity)
        #     i = i+1
        #    else:
        #       break
        Quantity = str(lotsize)
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
        # orderid = smartApi.placeOrder(orderparams)
        
        print('buy order ')
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp']
        print(ltp_value)
        break
       # Method 2: Place an order and return the full response


    

    while(True):
        # print('here also for sell')
        time.sleep(1)
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1.15*(float(buyvalue))
        highersell = 1.5*(float(buyvalue))
        # print(ltp_value)
        # print(sellvalue)
        if(float(ltp_value) >sellvalue):
            
            
            newselltrigerprice =  math.ceil(0.88*(float(ltp_value)) * 10) / 10
            if(float(ltp_value) >highersell):
              newselltrigerprice =  math.ceil(0.85*(float(ltp_value)) * 10) / 10
            if(newselltrigerprice>= trigerprice):
               trigerprice = newselltrigerprice

             # stoploss at 65% loss
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
            
            # orderid = smartApi.placeOrder(orderparams)
            ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
            ltp_value = ltp_data['data']['ltp'] 
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
        #    orderid = smartApi.placeOrder(orderparams)
           ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
           ltp_value = ltp_data['data']['ltp'] 
           print('sell value')
           print(ltp_value)
           break
    
    







# second order placement
    while(True):
       
      now = datetime.now()
      formatted_now = now.strftime("%H:%M:%S")
      trigerprice = 0
      # Method 1: Place an order and return the order ID
      if(formatted_now == time315):
        print(datetime.now())
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
        
        scriptcesymbol = 'MIDCPNIFTY' + date + month + year+ livedata  + 'CE'
        scriptpesymbol = 'MIDCPNIFTY' + date + month + year + livedata  + 'PE'
        print(scriptpesymbol)
        result = tokendf[tokendf['symbol'] == scriptcesymbol]
        tokence = result['token'].values[0]
        lotsize = result['lotsize'].values[0]
        lotsize = int(lotsize)
    # Display result
        print(scriptpesymbol)
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

        result = tokendf[tokendf['symbol'] == tradingsymbol]
        symboltoken = result['token'].values[0]
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        buyvalue = float(ltp_value) 
        buyvalue = str(buyvalue)
        # code to get quantity
        # while(True):
        #    if(lotsize*i*float(ltp_value) < margin):
        #     Quantity = lotsize*i
        #     Quantity = str(Quantity)
        #     print(Quantity)
        #     i = i+1
        #    else:
        #       break
        Quantity = str(lotsize)
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
        # orderid = smartApi.placeOrder(orderparams)
        
        print('buy order ')
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp']
        print(ltp_value)
        break
       # Method 2: Place an order and return the full response

    while(True):
        # print('here also for sell')
        time.sleep(0.8)
        ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
        ltp_value = ltp_data['data']['ltp'] 
        sellvalue = 1.15*(float(buyvalue))
        highersell = 1.5*(float(buyvalue))
        # print(ltp_value)
        # print(sellvalue)
        if(float(ltp_value) >sellvalue):
            
            
            newselltrigerprice =  math.ceil(0.88*(float(ltp_value)) * 10) / 10
            if(float(ltp_value) >highersell):
              newselltrigerprice =  math.ceil(0.85*(float(ltp_value)) * 10) / 10
            if(newselltrigerprice>= trigerprice):
               trigerprice = newselltrigerprice

             # stoploss at 65% loss
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
            
            # orderid = smartApi.placeOrder(orderparams)
            ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
            ltp_value = ltp_data['data']['ltp'] 
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
        #    orderid = smartApi.placeOrder(orderparams)
           ltp_data=smartApi.ltpData(exch, tradingsymbol, symboltoken)
           ltp_value = ltp_data['data']['ltp'] 
           print('sell value')
           print(ltp_value)
           break


       
    
    
    