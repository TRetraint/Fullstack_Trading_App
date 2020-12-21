import config, sqlite3
import alpaca_trade_api as tradeapi
import tulipy
import numpy as np

connection = sqlite3.connect(config.DB_PATH)
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.URL)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor.execute("""SELECT id, symbol, name FROM stock""")

rows = cursor.fetchall()

symbols = []
stock_dict = {}
for row in rows:
    symbol = row[1]
    symbols.append(symbol)
    stock_dict[symbol] = row[0]

chunk_size = 200
for i in range(0, len(symbols), chunk_size):
    symbol_chunk = symbols[i:i+chunk_size]
    barsets = api.get_barset(symbol_chunk, 'day')
    for symbol in barsets:
        print(f"processing symbol {symbol}")
        recent_closes = [bar.c for bar in barsets[symbol]]
        count = len(barsets[symbol])
        init = count + 50
        for bar in barsets[symbol]:
            stock_id = stock_dict[symbol]
            if count <= 50 and init >= 150:
                sma_20 = tulipy.sma(np.array(recent_closes), period = 20)[-count]
                sma_50 = tulipy.sma(np.array(recent_closes), period = 50)[-count]
                rsi_14 = tulipy.rsi(np.array(recent_closes), period = 14)[-count]
            else:
                sma_20, sma_50, rsi_14 = None, None, None
            cursor.execute("""
                INSERT INTO stock_price (stock_id, date, open, high, low, close, volume, sma_20, sma_50, rsi_14)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v, sma_20, sma_50, rsi_14))
            count -= 1
connection.commit()