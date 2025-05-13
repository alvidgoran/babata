import ccxt
import pandas as pd
import time
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configurar Binance
exchange = ccxt.binance({
    'apiKey': os.getenv('API_KEY'),
    'secret': os.getenv('SECRET_KEY'),
    'enableRateLimit': True,
})

# Parámetros
symbol = 'BTC/USDT'
timeframe = '1m'  # Velas de 1 minuto
investment = 10  # USDT a invertir por operación (ajusta esto)

# Función para calcular RSI
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Función para obtener señal
def get_signal():
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['rsi'] = calculate_rsi(df)
    
    last_rsi = df['rsi'].iloc[-1]
    last_close = df['close'].iloc[-1]
    
    # Señal de compra: RSI bajo y precio subiendo
    if last_rsi < 30 and df['close'].iloc[-1] > df['close'].iloc[-2]:
        return 'buy', last_close
    # Señal de venta: RSI alto y precio bajando
    elif last_rsi > 70 and df['close'].iloc[-1] < df['close'].iloc[-2]:
        return 'sell', last_close
    else:
        return 'hold', last_close

# Función principal
def run_bot():
    print("🚀 Bot de Scalping en 30 segundos activado...")
    print(f"Par: {symbol} | Timeframe: {timeframe}")
    print("--------------------------------------------------")
    
    while True:
        try:
            signal, price = get_signal()
            
            if signal == 'buy':
                print(f"\n✅ Señal COMPRA a {price:.2f} USDT")
                print("⏳ Esperando 30 segundos para verificar...")
                time.sleep(30)
                new_price = exchange.fetch_ticker(symbol)['last']
                
                if new_price > price:
                    profit = (new_price - price) / price * 100
                    print(f"🎉 Ganaste! Precio subió a {new_price:.2f} USDT (+{profit:.2f}%)")
                else:
                    loss = (price - new_price) / price * 100
                    print(f"🔴 Perdiste. Precio bajó a {new_price:.2f} USDT (-{loss:.2f}%)")
            
            elif signal == 'sell':
                print(f"\n📉 Señal VENTA a {price:.2f} USDT")
                print("⏳ Esperando 30 segundos para verificar...")
                time.sleep(30)
                new_price = exchange.fetch_ticker(symbol)['last']
                
                if new_price < price:
                    profit = (price - new_price) / price * 100
                    print(f"🎉 Ganaste! Precio bajó a {new_price:.2f} USDT (+{profit:.2f}%)")
                else:
                    loss = (new_price - price) / price * 100
                    print(f"🔴 Perdiste. Precio subió a {new_price:.2f} USDT (-{loss:.2f}%)")
            
            else:
                print(f"\n⏱️ Sin señales. Precio actual: {price:.2f} USDT", end='\r')
            
            time.sleep(5)  # Espera 5 segundos entre chequeos
            
        except Exception as e:
            print(f"\n❌ Error: {e}. Reintentando...")
            time.sleep(10)

if __name__ == '__main__':
    run_bot()