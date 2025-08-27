# ================= INSTALAÇÃO DAS BIBLIOTECAS =================
!pip install --upgrade pip
!pip install python-deriv-api==0.1.6 reactivex ta websockets==10.3 nest_asyncio

# ================= IMPORTS =================
import os
import asyncio
import nest_asyncio
from deriv_api import DerivAPI
import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from IPython.display import display, HTML

nest_asyncio.apply()

# ================= VARIÁVEIS DE AMBIENTE =================
os.environ["DERIV_TOKEN"] = "hq5SmvQjftc2xlv"
os.environ["DERIV_APP_ID"] = "1089"

# ================= FUNÇÃO DE GERAÇÃO DE SINAIS =================
def gerar_sinal(candle, indicadores):
    """
    Retorna um dicionário com tipo de sinal e preço
    """
    sinal = {"type": "NO_SIGNAL", "price": candle['close']}

    if indicadores['ema_fast'] > indicadores['ema_slow'] and indicadores['rsi'] < 70:
        sinal["type"] = "BUY"
    elif indicadores['ema_fast'] < indicadores['ema_slow'] and indicadores['rsi'] > 30:
        sinal["type"] = "SELL"

    return sinal

def mostrar_sinal_colab(sinal):
    if sinal["type"] != "NO_SIGNAL":
        cor = "green" if sinal["type"] == "BUY" else "red"
        display(HTML(f"<h3 style='color:{cor}'>Sinal: {sinal['type']} | Preço: {sinal['price']}</h3>"))

# ================= FUNÇÃO PRINCIPAL =================
async def run_bot():
    api = DerivAPI(app_id=int(os.environ["DERIV_APP_ID"]), token=os.environ["DERIV_TOKEN"])
    await api.authorize()
    print("✅ Robô iniciado. Monitorando frxEURUSD 1m...")

    SYMBOL = "frxEURUSD"
    TIMEFRAME = 60  # Velas de 1 minuto
    EMA_FAST = 9
    EMA_SLOW = 21
    RSI_PERIOD = 14

    while True:
        try:
            # ================= BUSCAR CANDLES =================
            candles_data = await api.candles(symbol=SYMBOL, interval=TIMEFRAME, count=50)
            closes = [c['close'] for c in candles_data]

            # ================= CALCULAR INDICADORES =================
            df = pd.DataFrame({"close": closes})
            df["ema_fast"] = EMAIndicator(df["close"], EMA_FAST).ema_indicator()
            df["ema_slow"] = EMAIndicator(df["close"], EMA_SLOW).ema_indicator()
            df["rsi"] = RSIIndicator(df["close"], RSI_PERIOD).rsi()

            candle_atual = candles_data[-1]
            indicadores = {
                "ema_fast": df["ema_fast"].iloc[-1],
                "ema_slow": df["ema_slow"].iloc[-1],
                "rsi": df["rsi"].iloc[-1]
            }

            # ================= GERAR E MOSTRAR SINAL =================
            sinal = gerar_sinal(candle_atual, indicadores)
            mostrar_sinal_colab(sinal)

        except Exception as e:
            print("❌ Erro ao processar candle:", e)

        await asyncio.sleep(1)  # Aguarda 1 segundo antes da próxima vela

# ================= EXECUÇÃO =================
asyncio.run(run_bot())
