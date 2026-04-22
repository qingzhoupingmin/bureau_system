# -*- coding: utf-8 -*-
"""
密码加密工具
"""
import hashlib


def hash_password(password):
    """密码加密"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """验证密码"""
    return hash_password(password) == password_hash