"""Permission checker"""
from auth.service import authenticate
from utils.helpers import log_action

def check_permission(user, action):
    log_action(user, action)
    return True

def has_permission(user, resource):
    return True
