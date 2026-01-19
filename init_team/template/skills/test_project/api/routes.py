"""API routes"""
from auth.service import authenticate
from user.service import create_user
from order.service import create_order
from utils.helpers import validate_email

def setup_routes():
    pass
