# ================= INSTALAÇÃO DAS BIBLIOTECAS =================
!pip install --upgrade pip
!pip install python-deriv-api==0.1.6 reactivex ta websockets==10.3 nest_asyncio

# ================= CONFIGURAÇÃO =================
import os
import asyncio
import nest_asyncio
import pandas as pd
from deriv_api import DerivAPI
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

nest_asyncio.apply()  # necessário para rodar asyncio no Colab/GitHub

# ================= VARIÁVEIS =================
TOKEN = "hq5SmvQjftc2xlv"  # seu token
APP_ID = 1089              # seu app_id
SYMBOL = "frxEURUSD"
TIMEFRAME = "1m"           # velas de 1 minuto
EMA_PERIOD = 10
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
RSI_PERIOD = 14

# ================= FUNÇÃO DE CONEXÃO E ROBÔ =================
async def run_bot():
    try:
        api = DerivAPI(app_id=APP_ID, token=TOKEN)
        await api.authorize(TOKEN)
        print("✅ Robô iniciado. Monitorando", SYMBOL, TIMEFRAME)
    except Exception as e:
        print("❌ Erro ao iniciar API:", e)
        return

    while True:
        try:
            # Busca candles corretos usando candles_history
            candles_data = await api.candles_history(
                symbol=SYMBOL,
                interval=TIMEFRAME,
                count=EMA_PERIOD + MACD_SLOW + RSI_PERIOD + 5
            )

            # Extrai preços de fechamento
            closes = [candle['close'] for candle in candles_data]

            # Converte em DataFrame
            df = pd.DataFrame({"close": closes})

            # Indicadores
            ema = EMAIndicator(df['close'], EMA_PERIOD).ema_indicator()
            macd = MACD(df['close'], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
            macd_line = macd.macd()
            macd_signal = macd.macd_signal()
            rsi = RSIIndicator(df['close'], RSI_PERIOD).rsi()

            # ================= LÓGICA DE SINAIS =================
            signal = "NAO_ENTRAR"
            if df['close'].iloc[-1] > ema.iloc[-1] and macd_line.iloc[-1] > macd_signal.iloc[-1] and rsi.iloc[-1] > 50:
                signal = "COMPRA"
            elif df['close'].iloc[-1] < ema.iloc[-1] and macd_line.iloc[-1] < macd_signal.iloc[-1] and rsi.iloc[-1] < 50:
                signal = "VENDA"

            print("Último fechamento:", df['close'].iloc[-1], "| Sinal:", signal)

            await asyncio.sleep(60)  # aguarda 1 vela de 1 minuto
        except Exception as e:
            print("❌ Erro ao buscar candles ou processar:", e)
            await asyncio.sleep(5)

# ================= EXECUÇÃO =================
asyncio.run(run_bot())
