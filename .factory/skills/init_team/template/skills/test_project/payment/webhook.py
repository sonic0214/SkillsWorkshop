"""Payment webhook"""
from payment.processor import process_payment
from utils.helpers import log_webhook

def on_payment_success(order_id):
    log_webhook('payment_success', order_id)
