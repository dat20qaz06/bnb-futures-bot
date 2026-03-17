from binance.client import Client
import pandas as pd
import ta
import time

API_KEY = " rPtsi022OurZAcBrttav4NkO8JJOMzMUNxhNXuiCQ2bT5zJj9WmgMQuVS4hV8oOC"
API_SECRET = " qFl6wdWCzbL58yMEwudBoI4alse25hte1j4p59uUke6gFnroxa8AeJ8sLjrSCwYZ"

client = Client(API_KEY, API_SECRET)

SYMBOL = "BNBUSDT"
QTY = 0.02
TP = 0.02
SL = 0.01

def get_klines():
    klines = client.futures_klines(symbol=SYMBOL, interval="5m", limit=150)
    df = pd.DataFrame(klines, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","i"])
    df["c"] = df["c"].astype(float)
    return df

def signal(df):
    df["ema20"] = ta.trend.ema_indicator(df["c"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["c"], window=50)
    if df["ema20"].iloc[-1] > df["ema50"].iloc[-1]:
        return "LONG"
    elif df["ema20"].iloc[-1] < df["ema50"].iloc[-1]:
        return "SHORT"
    else:
        return "NONE"

def order(side):
    price = float(client.futures_mark_price(symbol=SYMBOL)["markPrice"])
    if side == "LONG":
        client.futures_create_order(symbol=SYMBOL, side="BUY", type="MARKET", quantity=QTY)
        tp = round(price*(1+TP),2)
        sl = round(price*(1-SL),2)
        exit_side="SELL"
    else:
        client.futures_create_order(symbol=SYMBOL, side="SELL", type="MARKET", quantity=QTY)
        tp = round(price*(1-TP),2)
        sl = round(price*(1+SL),2)
        exit_side="BUY"

    client.futures_create_order(symbol=SYMBOL, side=exit_side, type="TAKE_PROFIT_MARKET", stopPrice=tp, closePosition=True)
    client.futures_create_order(symbol=SYMBOL, side=exit_side, type="STOP_MARKET", stopPrice=sl, closePosition=True)

while True:
    df = get_klines()
    s = signal(df)
    if s!="NONE":
        order(s)
        print("Vào lệnh:",s)
        time.sleep(300)
    else:
        print("Sideway - đứng ngoài")
        time.sleep(60)
