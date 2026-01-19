"""User model"""
from permission.check import has_permission
from utils.helpers import hash_password

class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def get(username):
        return User(username)
