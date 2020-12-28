import alpaca_trade_api as tradeapi
import config

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.URL)

response = api.close_all_positions()

print(response)