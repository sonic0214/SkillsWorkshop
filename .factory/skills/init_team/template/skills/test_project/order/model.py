"""Order model"""
from payment.webhook import on_payment_success
from utils.helpers import generate_order_id

class Order:
    def __init__(self, order_id):
        self.order_id = order_id
