#!/usr/bin/env python3
"""
创建一个测试项目，用于验证 analyze_existing_project.py

这个测试项目包含：
- 2 处循环依赖
- 1 个上帝模块
- 正常的依赖关系
"""

import os
import sys
from pathlib import Path


def create_test_project(target_dir: str):
    """创建测试项目"""
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)

    print(f"创建测试项目：{target}")

    # 创建模块结构
    modules = {
        "auth": ["__init__.py", "service.py", "validator.py"],
        "user": ["__init__.py", "model.py", "service.py"],
        "permission": ["__init__.py", "check.py", "model.py"],
        "order": ["__init__.py", "model.py", "service.py"],
        "payment": ["__init__.py", "processor.py", "webhook.py"],
        "utils": ["__init__.py", "helpers.py"],
        "api": ["__init__.py", "routes.py"],
        "database": ["__init__.py", "connection.py"]
    }

    for module_name, files in modules.items():
        module_dir = target / module_name
        module_dir.mkdir(exist_ok=True)

        for file_name in files:
            file_path = module_dir / file_name
            content = generate_file_content(module_name, file_name)
            with open(file_path, 'w') as f:
                f.write(content)

    # 创建 requirements.txt
    with open(target / "requirements.txt", 'w') as f:
        f.write("# Test project\n")

    print("✅ 测试项目创建完成")
    print("")
    print("项目结构：")
    print(f"  {target}/")
    for module_name in modules.keys():
        print(f"    ├── {module_name}/")
    print("    └── requirements.txt")
    print("")
    print(f"运行分析：python analyze_existing_project.py {target}")


def generate_file_content(module_name: str, file_name: str) -> str:
    """生成文件内容（包含依赖关系）"""

    # __init__.py
    if file_name == "__init__.py":
        return f'"""Module: {module_name}"""\n'

    # auth 模块
    if module_name == "auth":
        if file_name == "service.py":
            return """\"\"\"Auth service\"\"\"
from user.model import User
from permission.check import check_permission
import utils.helpers as helpers

def authenticate(username, password):
    user = User.get(username)
    if check_permission(user, 'login'):
        return helpers.generate_token(user)
    return None
"""
        elif file_name == "validator.py":
            return """\"\"\"Auth validator\"\"\"
from utils.helpers import validate_email, validate_password

def validate_credentials(username, password):
    return validate_email(username) and validate_password(password)
"""

    # user 模块
    if module_name == "user":
        if file_name == "model.py":
            return """\"\"\"User model\"\"\"
from permission.check import has_permission
from utils.helpers import hash_password

class User:
    def __init__(self, username):
        self.username = username

    @staticmethod
    def get(username):
        return User(username)
"""
        elif file_name == "service.py":
            return """\"\"\"User service\"\"\"
from utils.helpers import send_email
from database.connection import get_db

def create_user(username, email):
    db = get_db()
    send_email(email, 'Welcome!')
    return {'username': username}
"""

    # permission 模块
    if module_name == "permission":
        if file_name == "check.py":
            return """\"\"\"Permission checker\"\"\"
from auth.service import authenticate
from utils.helpers import log_action

def check_permission(user, action):
    log_action(user, action)
    return True

def has_permission(user, resource):
    return True
"""
        elif file_name == "model.py":
            return """\"\"\"Permission model\"\"\"
from utils.helpers import cache_get, cache_set

class Permission:
    pass
"""

    # order 模块
    if module_name == "order":
        if file_name == "model.py":
            return """\"\"\"Order model\"\"\"
from payment.webhook import on_payment_success
from utils.helpers import generate_order_id

class Order:
    def __init__(self, order_id):
        self.order_id = order_id
"""
        elif file_name == "service.py":
            return """\"\"\"Order service\"\"\"
from utils.helpers import send_notification
from database.connection import get_db

def create_order(user_id, items):
    db = get_db()
    send_notification(user_id, 'Order created')
    return {'order_id': 123}
"""

    # payment 模块
    if module_name == "payment":
        if file_name == "processor.py":
            return """\"\"\"Payment processor\"\"\"
from order.model import Order
from utils.helpers import validate_amount

def process_payment(order_id, amount):
    order = Order(order_id)
    if validate_amount(amount):
        return True
    return False
"""
        elif file_name == "webhook.py":
            return """\"\"\"Payment webhook\"\"\"
from payment.processor import process_payment
from utils.helpers import log_webhook

def on_payment_success(order_id):
    log_webhook('payment_success', order_id)
"""

    # utils 模块（上帝模块）
    if module_name == "utils":
        if file_name == "helpers.py":
            return """\"\"\"Utility functions (God Module)\"\"\"

# 认证相关
def generate_token(user):
    return f"token_{user.username}"

def validate_email(email):
    return '@' in email

def validate_password(password):
    return len(password) >= 8

def hash_password(password):
    return f"hash_{password}"

# 订单相关
def generate_order_id():
    return 12345

def validate_amount(amount):
    return amount > 0

# 通知相关
def send_email(email, message):
    pass

def send_notification(user_id, message):
    pass

# 日志相关
def log_action(user, action):
    pass

def log_webhook(event, data):
    pass

# 缓存相关
def cache_get(key):
    return None

def cache_set(key, value):
    pass
"""

    # api 模块
    if module_name == "api":
        if file_name == "routes.py":
            return """\"\"\"API routes\"\"\"
from auth.service import authenticate
from user.service import create_user
from order.service import create_order
from utils.helpers import validate_email

def setup_routes():
    pass
"""

    # database 模块
    if module_name == "database":
        if file_name == "connection.py":
            return """\"\"\"Database connection\"\"\"

def get_db():
    return {}
"""

    return f'"""Module: {module_name}, File: {file_name}"""\n'


if __name__ == "__main__":
    if len(sys.argv) < 2:
        target = "./test_project"
        print(f"使用默认目录：{target}")
    else:
        target = sys.argv[1]

    create_test_project(target)
