import sqlite3
import config
import alpaca_trade_api as tradeapi
from  datetime import date,timedelta
import yfinance as yf
import email_notif
import tulipy

current_date = date.today() + timedelta(days=-1)
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.URL)
orders = api.list_orders(status='all', after=f"{current_date}")

connection = sqlite3.connect(config.DB_PATH)
connection.row_factory = sqlite3.Row
messages = []
cursor = connection.cursor()

cursor.execute("""
    SELECT id FROM strategy WHERE name = 'bollinger_bands'
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

existing_order_symbols = [order.symbol for order in orders if order.status != 'canceled']

start_minute_bar = f"{current_date} 09:30:00-05:00"
end_minute_bar = f"{current_date} 16:00:00-05:00"

for symbol in symbols:
    minute_bars = yf.download(symbol, start=current_date, end=current_date + timedelta(days=1), interval = "1m")

    market_open_mask = (minute_bars.index >= start_minute_bar) & (minute_bars.index < end_minute_bar)
    market_open_bars = minute_bars.loc[market_open_mask]

    if len(market_open_bars) >= 20:
        closes = market_open_bars.close.values
        lower, middle, upper = tulipy.bbands(closes, 20, 2)

        current_candle = market_open_bars.iloc[-1]
        previous_candle = market_open_bars.iloc[-2]

        if current_candle.close > lower[-1] and previous_candle < lower[-2]:
            if symbol not in existing_order_symbols:
                limit_price = current_candle.close
                candle_range = curent_candle.high - current_candle.low
                print(f"placing order for {symbol} at {limit_price}")
                api.submit_order(
                    symbol=symbol,
                    side='buy',
                    type='limit',
                    qty=risk.calculate_quantity(limit_price,5),
                    time_in_force='day',
                    order_class='bracket',
                    limit_price=limit_price,
                    take_profit=dict(limit_price = limit_price + candle_range*3),
                    stop_loss=dict(stop_price = previous_candle.low)
                )
                messages.append(f"placing order for {symbol} at {limit_price}")
            else:
                print(f"Error : Already an order for {symbol}")

        elif current_candle.close < upper[-1] and previous_candle > upper[-2]:
            if symbol not in existing_order_symbols:
                limit_price = current_candle.close
                candle_range = curent_candle.high - current_candle.low
                print(f"Shorting {symbol} at {limit_price}")
                api.submit_order(
                    symbol=symbol,
                    side='sell',
                    type='limit',
                    qty=risk.calculate_quantity(limit_price,5),
                    time_in_force='day',
                    order_class='bracket',
                    limit_price=limit_price,
                    take_profit=dict(limit_price = limit_price - candle_range*3),
                    stop_loss=dict(stop_price = previous_candle.high)
                )
                messages.append(f"Shorting {symbol} at {limit_price}")
            else:
                print(f"Error : Already an order for {symbol}")

strategy = "Bollinger Bands"
email_notif.send_email(f"Trade Notifications for {current_date}",messages, strategy)




