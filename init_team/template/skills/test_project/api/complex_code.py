#!/usr/bin/env python3
"""
复杂代码示例 - 用于测试复杂度检测
"""


def very_complex_function(data, mode, config):
    """高复杂度函数 - 包含大量分支"""
    result = []

    if mode == 'advanced':
        for item in data:
            if item.get('status') == 'active':
                if item.get('priority') == 'high':
                    if config.get('strict_mode'):
                        if item.get('verified'):
                            result.append(item)
                        elif config.get('allow_unverified'):
                            result.append(item)
                    else:
                        result.append(item)
                elif item.get('priority') == 'medium':
                    if config.get('include_medium'):
                        result.append(item)
                else:
                    if config.get('include_low') and item.get('age') > 30:
                        result.append(item)
            elif item.get('status') == 'pending':
                if config.get('include_pending'):
                    result.append(item)
    elif mode == 'simple':
        for item in data:
            if item.get('status') == 'active':
                result.append(item)
    else:
        result = data

    return result


def very_long_function(user_id):
    """超长函数 - 超过 50 行"""
    # Line 1
    user = get_user(user_id)
    # Line 2
    # Line 3
    if not user:
        return None
    # Line 4
    # Line 5
    # Line 6
    profile = get_profile(user_id)
    # Line 7
    # Line 8
    # Line 9
    # Line 10
    orders = get_orders(user_id)
    # Line 11
    # Line 12
    # Line 13
    # Line 14
    # Line 15
    payments = get_payments(user_id)
    # Line 16
    # Line 17
    # Line 18
    # Line 19
    # Line 20
    preferences = get_preferences(user_id)
    # Line 21
    # Line 22
    # Line 23
    # Line 24
    # Line 25
    history = get_history(user_id)
    # Line 26
    # Line 27
    # Line 28
    # Line 29
    # Line 30
    analytics = calculate_analytics(user_id)
    # Line 31
    # Line 32
    # Line 33
    # Line 34
    # Line 35
    recommendations = get_recommendations(user_id)
    # Line 36
    # Line 37
    # Line 38
    # Line 39
    # Line 40
    notifications = get_notifications(user_id)
    # Line 41
    # Line 42
    # Line 43
    # Line 44
    # Line 45
    stats = calculate_stats(user_id)
    # Line 46
    # Line 47
    # Line 48
    # Line 49
    # Line 50
    badges = get_badges(user_id)
    # Line 51
    # Line 52
    return {
        'user': user,
        'profile': profile,
        'orders': orders,
        'payments': payments,
        'preferences': preferences,
        'history': history,
        'analytics': analytics,
        'recommendations': recommendations,
        'notifications': notifications,
        'stats': stats,
        'badges': badges
    }


def process_data_v1(items):
    """重复代码示例 1"""
    filtered = []
    for item in items:
        if item['value'] > 0:
            filtered.append(item)
    return filtered


def process_data_v2(elements):
    """重复代码示例 2 - 与 v1 结构相同"""
    filtered = []
    for element in elements:
        if element['value'] > 0:
            filtered.append(element)
    return filtered


def process_data_v3(records):
    """重复代码示例 3 - 与 v1 结构相同"""
    filtered = []
    for record in records:
        if record['value'] > 0:
            filtered.append(record)
    return filtered


# Dummy functions
def get_user(user_id): return {}
def get_profile(user_id): return {}
def get_orders(user_id): return []
def get_payments(user_id): return []
def get_preferences(user_id): return {}
def get_history(user_id): return []
def calculate_analytics(user_id): return {}
def get_recommendations(user_id): return []
def get_notifications(user_id): return []
def calculate_stats(user_id): return {}
def get_badges(user_id): return []
