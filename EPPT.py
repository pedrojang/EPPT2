from numpy.core.einsumfunc import _einsum_path_dispatcher
import tensorflow as tf
import pandas as pd
import ccxt
import numpy as np
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
apiKey = 'Y3dcAaJ0BtLZdQpk9YTryEaft7wQQNMPZc7UJcZAGLKRbDFbtvw2GkRGVeadkvsL'
secKey = 'DA9aVE2d9fs7QWL6YfDs7Q3mJYHblnhJoPdO4tWjbDw4kGJCXviTSlZNroF99Dk9'



lastBol_low = 0.0
lastBol_high = 0.0
binanceFUTURE = ccxt.binance(config={
    'apiKey': apiKey,
    'secret': secKey,
    'enableRateLimit': True, 
})

binanceFR = ccxt.binance(config={
    'apiKey': apiKey, 
    'secret': secKey,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

markets = binanceFR.load_markets()
symbol = "ETH/USDT"
market = binanceFR.market(symbol)
leverage = 30

resp = binanceFR.fapiPrivate_post_leverage({
    'symbol': market['id'],
    'leverage': leverage
})


balance = binanceFUTURE.fetch_balance(params={"type": "future"})


def btcc():
    btc = binanceFR.fetch_ohlcv(
        symbol="ETH/USDT", 
        timeframe='15m', 
        since=None, 
        limit=41)


    return btc

def GetPD():
    dff = pd.DataFrame(btcc(), columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    dff['datetime'] = pd.to_datetime(dff['datetime'], unit='ms')
    dff['dec'] = dff['high'] - dff['low']
    dff['RD'] = dff['close'] - dff['open']
    dff['GS'] = dff['dec']/dff['volume']
    dff['uptail'] = dff['high'] - ((dff['open'] + dff['close'])/2 + abs(dff['RD'])/2)
    dff['downtail'] = ((dff['open'] + dff['close'])/2 - abs(dff['RD'])/2) - dff['low']
    dff['open1'] = dff['open'].shift(1)
    dff['high1'] = dff['high'].shift(1)
    dff['low1'] = dff['low'].shift(1)
    dff['close1'] = dff['close'].shift(1)
    dff['volume1'] = dff['volume'].shift(1)
    dff['dec1'] = dff['dec'].shift(1)
    dff['RD1'] = dff['RD'].shift(1)
    dff['uptail1'] = dff['uptail'].shift(1)
    dff['downtail1'] = dff['downtail'].shift(1)
    dff['GS1'] = dff['GS'].shift(1)
    dff['open2'] = dff['open1'].shift(1)
    dff['high2'] = dff['high1'].shift(1)
    dff['low2'] = dff['low1'].shift(1)
    dff['close2'] = dff['close1'].shift(1)
    dff['volume2'] = dff['volume1'].shift(1)
    dff['dec2'] = dff['dec1'].shift(1)
    dff['RD2'] = dff['RD1'].shift(1)
    dff['uptail2'] = dff['uptail1'].shift(1)
    dff['downtail2'] = dff['downtail1'].shift(1)
    dff['GS2'] = dff['GS1'].shift(1)
    dff.set_index('datetime', inplace=True)
    dff['tMA1'] = dff['close1'].rolling(window=20).mean()
    dff['std1'] = dff['close1'].rolling(window=20).std()
    dff['tMA2'] = dff['tMA1'].shift(1)
    dff['RR'] = dff['tMA1'] - dff['tMA2']
    dff1= dff.dropna()
    dff1['bollow1'] = dff1['tMA1'] - 2*dff1['std1']
    dff1['bolhigh1'] = dff1['tMA1'] + 2*dff1['std1']
    dff1.isnull().sum()
    return dff1


# 고가 - 저가 
def getdec():

    lst = GetPD().dec.tolist()
    return lst

# 시가 - 종가 리스트
def getRD():
    lst = GetPD().RD.tolist()
    return lst

# 시가
def getopen():

    lst = GetPD().open.tolist()
    return lst
# 종가 
def getclose():

    lst = GetPD().close.tolist()
    return lst
# 고가
def gethigh():
    lst = GetPD().high.tolist()
    return lst
#저가 
def getlow():
    lst = GetPD().low.tolist()
    return lst

def printer(y):
    print('open:',ls3[y])
    print('close:',ls4[y])
    print('high:',ls5[y])
    print('low:',ls6[y])
    print('predicted:',ls1[y])

def mail(text,PN):
    now = datetime.now()
    
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('pedrojang777@gmail.com','mpgzxiggfdjbarqz')

    msg =  MIMEText(text)
    msg['Subject'] = PN + str(now)

    s.sendmail('pedrojang777@gmail.com','peter000520@naver.com',msg.as_string())

    s.quit()

def nownow():
    now = datetime.now().minute

    return now

def nowhour():
    NH = datetime.now().hour

    return NH

# 선물 계좌 구하기 
def BGDF():
    balance = binanceFUTURE.fetch_balance(params={"type": "future"})

    return balance['USDT']['free']
# 현재가 구하기
def getcurrent():
    symbol = "ETH/USDT"
    btc = binanceFR.fetch_ticker(symbol)
    return btc['last']

def amountgetter():
    money = BGDF()
    if BGDF() > 20000:
        money = 20000
    amountget = round(money/getcurrent(),6)*0.985
    return amountget

#롱 - 풀매수 -
def buybit(a):
    order = binanceFR.create_market_buy_order(
    symbol=symbol,
    amount=a*leverage,
)

#숏 - 풀매도 -
def sellbit(a):
    order = binanceFR.create_market_sell_order(
    symbol=symbol,
    amount=a*leverage,
)
mail('start','start')
pos15 = False
LP = False
SP = False
nowmin = -1
nowH = -1
etheramount = 0
SM = BGDF()
while True:
    try:
        if not nownow()//15 == nowmin:
            # 포지션 정리 알고리즘 추가할 것
            if SP == True:
                buybit(etheramount)
                SP = False
            if LP == True:
                sellbit(etheramount)
                LP = False
            if not nowH == nowhour():
                profit = BGDF()/SM
                TEXT = 'it is...'
                PN = 'profit till now...' + str(profit)
                mail(TEXT,PN)
                nowH = nowhour()
            nowmin = nownow()//15
            EtherPrice = GetPD()

            IV = EtherPrice[['high1', 'low1', 'close1','open1', 'open2', 'high2', 'low2', 'close2','tMA1','RR']]
            DV = EtherPrice[['close']]

            X = tf.keras.layers.Input(shape=[10])
            Y = tf.keras.layers.Dense(1)(X)
            model = tf.keras.models.Model(X, Y)
            model.compile(loss='mse', optimizer = 'adam')
            model.fit(IV, DV, epochs=3000)

            ls = model.predict(IV)
            ls1 = []
            i = 0

            while i < len(ls):
              a = str(ls[i])
              b = a[1:-1]
              ls1.append(b)
              i = i + 1
            ls3 = EtherPrice.open.tolist()
            ls4 = EtherPrice.close.tolist()
            ls5 = EtherPrice.high.tolist()
            ls6 = EtherPrice.low.tolist()
            lsma = EtherPrice.tMA1.tolist()
            lsrr = EtherPrice.RR.tolist()
            lsbl = EtherPrice.bollow1.tolist()
            lsbh = EtherPrice.bolhigh1.tolist()
            pos15 = False
        # 숏잡을때
        if float(ls3[-1]) > float(ls1[-1]) and SP == False and pos15 == False:
            sellprice = getcurrent()
            etheramount = amountgetter()
            sellbit(etheramount)
            print(datetime.now(),'sell')
            SP = True
            pos15 = True
        #숏 정리 
        if SP == True and getcurrent() < sellprice * 0.999 :
            buybit(etheramount)
            SP = False
            print(datetime.now(),'short possition END')
        # 롱 잡을 때 
        if float(ls3[-1]) < float(ls1[-1]) and LP == False and pos15 == False:
            buyprice = getcurrent()
            etheramount = amountgetter()
            buybit(etheramount)
            print(datetime.now(),'buy')
            LP = True
            pos15 = True
        # 롱 정리 
        if LP == True and getcurrent() > buyprice * 1.001:
            sellbit(etheramount)
            LP = False
            print(datetime.now(),'long possition END')



    except Exception as e:
            print(e)
            time.sleep(1)