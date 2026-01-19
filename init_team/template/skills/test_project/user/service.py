"""User service"""
from utils.helpers import send_email
from database.connection import get_db

def create_user(username, email):
    db = get_db()
    send_email(email, 'Welcome!')
    return {'username': username}
