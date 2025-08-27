# ================= main.py =================
import asyncio
import os
import json
import websockets

# ================= CONFIGURAÇÃO =================
DERIV_TOKEN = os.getenv("DERIV_TOKEN")  # Certifique-se de definir no Colab
APP_ID = os.getenv("DERIV_APP_ID")      # Certifique-se de definir no Colab
SYMBOL = "frxEURUSD"
TIMEFRAME = "1m"  # Velas de 1 minuto

# ================= FUNÇÃO DE CONEXÃO =================
async def connect_deriv():
    url = f"wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}&l=EN&brand=deriv&token={DERIV_TOKEN}"
    print("Tentando conectar ao WebSocket:")
    print(url)
    connection = await websockets.connect(url)
    print("✅ Conexão WebSocket estabelecida com sucesso")
    return connection

# ================= FUNÇÃO DE OUVIR CANDLES =================
async def listen_candles():
    conn = await connect_deriv()
    
    # Solicitar candles
    request = {
        "ticks_history": SYMBOL,
        "adjust_start_time": 1,
        "count": 10,
        "end": "latest",
        "start": 1,
        "style": "candles",
        "granularity": 60  # 1 minuto
    }
    await conn.send(json.dumps(request))

    while True:
        try:
            response = await conn.recv()
            data = json.loads(response)
            # Aqui você pode processar os candles e emitir sinais
            # Exemplo básico:
            if "candles" in data:
                last_candle = data["candles"][-1]
                close = last_candle["close"]
                high = last_candle["high"]
                low = last_candle["low"]

                # Exemplo simples de sinal
                if close > high * 0.995:
                    signal = "COMPRA"
                elif close < low * 1.005:
                    signal = "VENDA"
                else:
                    signal = "NÃO ENTRAR"

                print(f"Sinal: {signal} | Close: {close}")
        except Exception as e:
            print("❌ Erro ao processar candle:", e)
            await asyncio.sleep(1)

# ================= FUNÇÃO PRINCIPAL =================
async def sample_calls():
    await listen_candles()

# ================= EXECUÇÃO =================
if __name__ == "__main__":
    asyncio.run(sample_calls())
