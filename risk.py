import math
import config

buying_power = config.BUYING_POWER

def calculate_quantity(price, pourcentage):
    amount = buying_power*(pourcentage/100)
    quantity = math.floor(amount / price)
    return quantity
