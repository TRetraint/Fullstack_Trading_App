import sqlite3
import config
import alpaca_trade_api as tradeapi
from  datetime import date,timedelta
import yfinance as yf
import email_notif


current_date = date.today() + timedelta(days=-1)
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.URL)
orders = api.list_orders(status='open', after=f"{current_date + timedelta(days=-1)}")

connection = sqlite3.connect(config.DB_PATH)
connection.row_factory = sqlite3.Row
messages = []
cursor = connection.cursor()

cursor.execute("""
    SELECT id FROM strategy WHERE name = 'opening_range_breakout'

 """)

strategy_id = cursor.fetchone()['id']

cursor.execute(""" 
    SELECT symbol, name
    FROM stock
    JOIN stock_strategy ON stock_strategy.stock_id = stock.id
    WHERE stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock[0] for stock in stocks]

existing_order_symbols = [order.symbol for order in orders]


start_minute_bar = f"{current_date} 09:35:00-05:00"
end_minute_bar = f"{current_date} 09:50:00-05:00"

for symbol in symbols:
    minute_bars = yf.download(symbol, start=current_date, end=current_date + timedelta(days=1), interval = "1m")
    opening_range_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    opening_range_bars = minute_bars.loc[opening_range_mask]

    opening_range_low = opening_range_bars['Low'].min()
    opening_range_high = opening_range_bars['High'].max()
    opening_range = opening_range_high - opening_range_low

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['Close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            limit_price = after_opening_range_breakout.iloc[0]['Close']
            print(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")
            messages.append(f"placing order for {symbol} at {limit_price}, closed above {opening_range_high}\n\n{after_opening_range_breakout.iloc[0]}\n\n")
            """
            api.submit_order(
                symbol=symbol,
                side='buy',
                type='limit',
                qty='100',
                time_in_force='day',
                order_class='bracket',
                limit_price=limit_price,
                take_profit=dict(limit_price = limit_price + opening_range),
                stop_loss=dict(stop_price = limit_price - opening_range)
            )
        """

        else:
            print(f"Error : Already an order for {symbol}")

print(messages)
strategy = "Opening Range Breakout"
email_notif.send_email(f"Trade Notifications for {current_date}",messages, strategy)


