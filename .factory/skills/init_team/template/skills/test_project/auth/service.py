"""Auth service"""
from user.model import User
from permission.check import check_permission
import utils.helpers as helpers

def authenticate(username, password):
    user = User.get(username)
    if check_permission(user, 'login'):
        return helpers.generate_token(user)
    return None
