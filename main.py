# main.py (versão híbrida)

import os
import asyncio
import pandas as pd
import numpy as np
from deriv_api import DerivAPI
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

# ================= VARIÁVEIS =================
TOKEN = os.getenv("DERIV_TOKEN")          # Token do Deriv
APP_ID = os.getenv("DERIV_APP_ID")        # App ID do Deriv
SYMBOL = "frxEURUSD"
TIMEFRAME = "5m"
EMA_PERIOD = 20
MACD_FAST = 12
MACD_SLOW = 26
RSI_PERIOD = 14

# ================= FUNÇÃO DE CONEXÃO =================
async def connect_deriv():
    api = DerivAPI(app_id=int(APP_ID), token=TOKEN)
    print("✅ Conectado ao Deriv WebSocket")
    return api

# ================= FUNÇÃO PARA OBTER CANDLES =================
async def get_candles(api, symbol, interval, count):
    # Pega os últimos candles
    candles = await api.candles(symbol=symbol, interval=interval, count=count)
    closes = [candle['close'] for candle in candles]
    return closes

# ================= FUNÇÃO DE SINAIS =================
def calcular_sinais(candles):
    df = pd.DataFrame(candles, columns=["close"])
    
    # EMA
    df["EMA"] = EMAIndicator(df["close"], EMA_PERIOD).ema_indicator()
    
    # MACD
    macd = MACD(df["close"], MACD_FAST, MACD_SLOW)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    
    # RSI
    df["RSI"] = RSIIndicator(df["close"], RSI_PERIOD).rsi()
    
    # Pullback simples: fechamento atual maior que EMA e MACD positivo
    sinal = ""
    if df["close"].iloc[-1] > df["EMA"].iloc[-1] and df["MACD"].iloc[-1] > df["MACD_signal"].iloc[-1] and df["RSI"].iloc[-1] < 70:
        sinal = "COMPRA"
    elif df["close"].iloc[-1] < df["EMA"].iloc[-1] and df["MACD"].iloc[-1] < df["MACD_signal"].iloc[-1] and df["RSI"].iloc[-1] > 30:
        sinal = "VENDA"
    else:
        sinal = "NEUTRO"
    
    return sinal

# ================= LOOP PRINCIPAL =================
async def run_bot():
    api = await connect_deriv()
    count = EMA_PERIOD + MACD_SLOW + RSI_PERIOD + 5
    
    while True:
        try:
            closes = await get_candles(api, SYMBOL, TIMEFRAME, count)
            sinal = calcular_sinais(closes)
            print(f"🚀 Último candle: {closes[-1]}, Sinal: {sinal}")
            await asyncio.sleep(60)  # Aguarda 1 minuto (M5)
        except Exception as e:
            print("❌ Erro ao buscar candle ou processar:", e)
            await asyncio.sleep(5)
            continue

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    asyncio.run(run_bot())
