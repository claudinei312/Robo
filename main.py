# ================= INSTALAÇÃO DAS BIBLIOTECAS =================
!pip install --upgrade pip
!pip install python-deriv-api==0.1.6 reactivex ta websockets==10.3 nest_asyncio pandas numpy

# ================= IMPORTS =================
import os
import asyncio
import nest_asyncio
import pandas as pd
import numpy as np
from deriv_api import DerivAPI
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

nest_asyncio.apply()  # Permite rodar asyncio no Colab

# ================= VARIÁVEIS =================
TOKEN = os.environ.get("DERIV_TOKEN", "hq5SmvQjftc2xlv")  # Substitua pelo seu token
APP_ID = os.environ.get("DERIV_APP_ID", "1089")
SYMBOL = "frxEURUSD"
TIMEFRAME = "5m"
EMA_PERIOD = 9
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
RSI_PERIOD = 14

# ================= FUNÇÕES =================
async def fetch_candles(api, symbol, timeframe, count=100):
    """
    Busca candles do Deriv usando a API síncrona via asyncio.
    """
    try:
        candles_data = await api.candles(symbol=symbol, interval=timeframe, count=count)
        df = pd.DataFrame(candles_data)
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print("❌ Erro ao buscar candles:", e)
        return None

def calculate_signals(df):
    """
    Calcula EMA, MACD, RSI e Pullback e retorna sinais.
    """
    signals = []

    # EMA
    ema = EMAIndicator(df['close'], EMA_PERIOD).ema_indicator()

    # MACD
    macd = MACD(df['close'], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    macd_line = macd.macd()
    macd_signal = macd.macd_signal()

    # RSI
    rsi = RSIIndicator(df['close'], RSI_PERIOD).rsi()

    # Pullback simples
    pullback = df['close'].iloc[-2] < df['close'].iloc[-3] and df['close'].iloc[-1] > df['close'].iloc[-2]

    # Condições de compra/venda
    if df['close'].iloc[-1] > ema.iloc[-1] and macd_line.iloc[-1] > macd_signal.iloc[-1] and rsi.iloc[-1] > 50 and pullback:
        signals.append("BUY")
    elif df['close'].iloc[-1] < ema.iloc[-1] and macd_line.iloc[-1] < macd_signal.iloc[-1] and rsi.iloc[-1] < 50 and pullback:
        signals.append("SELL")
    else:
        signals.append("HOLD")

    return signals

# ================= ROBÔ =================
async def run_bot():
    try:
        api = DerivAPI(app_id=APP_ID)
        await api.authorize(TOKEN)
        print(f"✅ Conexão WebSocket estabelecida com sucesso para {SYMBOL}")
    except Exception as e:
        print("❌ Erro na conexão:", e)
        return

    while True:
        df = await fetch_candles(api, SYMBOL, TIMEFRAME, EMA_PERIOD + MACD_SLOW + RSI_PERIOD + 5)
        if df is not None and len(df) >= EMA_PERIOD:
            signals = calculate_signals(df)
            print(f"📊 Último candle: {df['close'].iloc[-1]:.5f} | Sinal: {signals[-1]}")
        await asyncio.sleep(60)  # Aguarda 1 minuto para próxima análise

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    asyncio.run(run_bot())
