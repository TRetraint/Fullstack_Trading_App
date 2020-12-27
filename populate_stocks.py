import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_PATH)

cursor = connection.cursor()
connection.row_factory = sqlite3.Row

cursor.execute("""SELECT symbol, name FROM stock""")

rows = cursor.fetchall()
symbols = [row[0] for row in rows]

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.URL)
assets = api.list_assets()

for asset in assets:
    try:
        if asset.status == "active" and asset.tradable:
            cursor.execute("INSERT INTO stock (symbol, name, exchange, shortable) VALUES (?,?,?,?)", (asset.symbol, asset.name, asset.exchange, asset.shortable))
    except Exception as e:
        print(asset.symbol)
        print(e)
connection.commit()