# ================= INSTALAÇÃO DAS BIBLIOTECAS =================
!pip install --upgrade pip
!pip install python-deriv-api==0.1.6 reactivex ta websockets==10.3 nest_asyncio

# ================= DEFINIÇÃO DE VARIÁVEIS DE AMBIENTE =================
import os
import asyncio
import nest_asyncio
nest_asyncio.apply()  # Permite rodar asyncio no Colab

# Substitua pelo seu token do Deriv
os.environ["DERIV_TOKEN"] = "hq5SmvQjftc2xlv"
# Substitua pelo seu app_id
os.environ["DERIV_APP_ID"] = "1089"

# ================= IMPORTAÇÃO DO CÓDIGO DO ROBÔ =================
from deriv_api import DerivAPI  # mantém o código original
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
import pandas as pd
import numpy as np

# ================= CONFIGURAÇÕES =================
SYMBOL = "frxEURUSD"
TIMEFRAME = "1m"  # Alterado para 1 minuto
EMA_PERIOD = 20
MACD_SLOW = 26
MACD_FAST = 12
RSI_PERIOD = 14

# ================= FUNÇÃO PRINCIPAL =================
async def run_bot():
    token = os.environ["DERIV_TOKEN"]
    app_id = int(os.environ["DERIV_APP_ID"])
    
    # Inicializa a API
    api = DerivAPI(app_id=app_id, token=token)
    print("Tentando conectar ao WebSocket...")
    
    try:
        await api.authorize(token)
        print("✅ Conexão WebSocket estabelecida com sucesso")
    except Exception as e:
        print("❌ Erro na conexão WebSocket:", e)
        return
    
    # Loop principal
    while True:
        try:
            # Pega candles M1
            candles_data = await api.candles(symbol=SYMBOL, interval=TIMEFRAME, count=EMA_PERIOD+MACD_SLOW+RSI_PERIOD+5)
            closes = [candle['close'] for candle in candles_data]
            
            # Calcula indicadores
            ema = EMAIndicator(pd.Series(closes), EMA_PERIOD).ema_indicator()[-1]
            macd = MACD(pd.Series(closes), MACD_FAST, MACD_SLOW).macd()[-1]
            rsi = RSIIndicator(pd.Series(closes), RSI_PERIOD).rsi()[-1]
            
            # Condições de exemplo (adaptáveis)
            signal = "Não entrar"
            if closes[-1] > ema and macd > 0 and rsi < 70:
                signal = "Comprar"
            elif closes[-1] < ema and macd < 0 and rsi > 30:
                signal = "Vender"
            
            print(f"Candle mais recente: {closes[-1]:.5f} | Sinal: {signal}")
            
            await asyncio.sleep(60)  # Espera 1 minuto até próximo candle
            
        except Exception as e:
            print("❌ Erro ao buscar candle ou processar:", e)
            await asyncio.sleep(5)
            continue

# ================= EXECUÇÃO =================
asyncio.run(run_bot())
