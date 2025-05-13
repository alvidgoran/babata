import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Descargar datos
btc = yf.download("BTC-USD", start="2022-01-01", end="2024-12-31")
btc = btc[['Close']]

# Calcular medias móviles
btc['MA20'] = btc['Close'].rolling(window=20).mean()
btc['MA50'] = btc['Close'].rolling(window=50).mean()

# Generar señales de trading (1 = comprar, 0 = nada)
btc['Signal'] = 0
btc.loc[20:, 'Signal'] = (btc['MA20'].iloc[20:] > btc['MA50'].iloc[20:]).astype(int)

# Crear columna 'Position' (la diferencia de señales)
btc['Position'] = btc['Signal'].diff()

# Inicializar variables
capital_inicial = 1000
capital = capital_inicial
btc_actual = 0
en_posicion = False
historial = []

# Backtest
for fecha, fila in btc.iterrows():
    precio = fila['Close']
    posicion = fila['Position']

    if posicion == 1 and not en_posicion:
        btc_actual = capital / precio
        capital = 0
        en_posicion = True
        historial.append((fecha, 'Compra', precio))

    elif posicion == -1 and en_posicion:
        capital = btc_actual * precio
        btc_actual = 0
        en_posicion = False
        historial.append((fecha, 'Venta', precio))

# Venta final si aún se tiene BTC
if en_posicion:
    capital = btc_actual * btc['Close'].iloc[-1]
    historial.append((btc.index[-1], 'Venta final', btc['Close'].iloc[-1]))

# Resultados
ganancia = capital - capital_inicial
porcentaje = (ganancia / capital_inicial) * 100
print(f"\n📈 Capital final: ${capital:.2f}")
print(f"💰 Ganancia/pérdida: ${ganancia:.2f} ({porcentaje:.2f}%)")
print("\n📜 Historial de operaciones:")
for h in historial:
    print(f"{h[0].date()} - {h[1]} a ${h[2]:.2f}")

# Gráfico
plt.figure(figsize=(14,7))
plt.plot(btc['Close'], label='Precio BTC', alpha=0.5)
plt.plot(btc['MA20'], label='MA20', linestyle='--')
plt.plot(btc['MA50'], label='MA50', linestyle='--')
plt.plot(btc[btc['Position'] == 1].index,
         btc['MA20'][btc['Position'] == 1],
         '^', markersize=10, color='g', label='Compra')
plt.plot(btc[btc['Position'] == -1].index,
         btc['MA20'][btc['Position'] == -1],
         'v', markersize=10, color='r', label='Venta')
plt.title('Bot de Trading con Backtest')
plt.xlabel('Fecha')
plt.ylabel('Precio (USD)')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
