from alpaca_trade_api.entity import Quote
from alpaca_trade_api.rest import Positions
import config
import alpaca_trade_api as tradeapi
import risk

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.URL)

symbols = ["SPY" , "IWM", "DIA"]

for symbol in symbols:
    quote = api.get_last_quote(symbol)

    api.submit_order(
        symbol=symbol,
        side='buy',
        type='market',
        qty=risk.calculate_quantity(quote.bidprice, 5),
        time_in_force='day'
    )
positions = api.list_positions()
print(positions)

api.submit_order(
    symbol='IWM',
    side='sell',
    qty=75,
    type='trailing_stop',
    trail_percent=2,
    time_in_force='day'
)
