"""Payment processor"""
from order.model import Order
from utils.helpers import validate_amount

def process_payment(order_id, amount):
    order = Order(order_id)
    if validate_amount(amount):
        return True
    return False
