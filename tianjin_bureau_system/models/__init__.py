# -*- coding: utf-8 -*-
"""
数据模型
"""
from models.user import User
from models.asset import Asset
from models.document import Document
from models.message import Message
from models.organization import Organization

__all__ = ['User', 'Asset', 'Document', 'Message', 'Organization']