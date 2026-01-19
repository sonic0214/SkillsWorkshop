"""Auth validator"""
from utils.helpers import validate_email, validate_password

def validate_credentials(username, password):
    return validate_email(username) and validate_password(password)
