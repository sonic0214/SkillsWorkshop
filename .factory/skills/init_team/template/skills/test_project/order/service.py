"""Order service"""
from utils.helpers import send_notification
from database.connection import get_db

def create_order(user_id, items):
    db = get_db()
    send_notification(user_id, 'Order created')
    return {'order_id': 123}
