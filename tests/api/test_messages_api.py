# -*- coding: utf-8 -*-
"""
消息管理接口测试
- 消息列表/详情
- 发送/回复消息
- 消息已读/删除
"""
import pytest
import random
from tests.common.api_client import APIClient
from tests.common.constants import API, HTTPStatus, Roles
from tests.common.config import test_config


class TestMessagesList:
    """消息列表接口测试"""

    def test_get_messages(self, admin_client: APIClient):
        """测试获取消息列表"""
        resp = admin_client.get_messages()
        assert resp.get("code") == 200

    def test_get_messages_pagination(self, admin_client: APIClient):
        """测试消息列表分页"""
        resp = admin_client.get_messages(page=1, page_size=5)
        assert resp.get("code") == 200

    def test_get_message_detail(self, admin_client: APIClient):
        """测试获取消息详情"""
        list_resp = admin_client.get_messages(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))

        if items and len(items) > 0:
            msg_id = items[0].get("id", items[0].get("message_id"))
            if msg_id:
                resp = admin_client.get_message(msg_id)
                assert resp.get("code") == 200

    def test_get_message_not_found(self, admin_client: APIClient):
        """测试获取不存在的消息"""
        resp = admin_client.get_message(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)


class TestMessagesSend:
    """消息发送测试"""

    def test_send_message(self, admin_client: APIClient):
        """测试发送消息"""
        suffix = random.randint(10000, 99999)

        resp = admin_client.send_message(
            receiver_id=test_config.normal.user_id,
            title=f"测试消息_{suffix}",
            content=f"这是测试消息的内容_{suffix}",
        )

        assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.OK)

    def test_reply_message(self, admin_client: APIClient):
        """测试回复消息"""
        list_resp = admin_client.get_messages(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            msg_id = items[0].get("id", items[0].get("message_id"))
            if msg_id:
                resp = admin_client.reply_message(msg_id, content="这是回复内容")
                assert resp.get("_status_code") in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.FORBIDDEN)


class TestMessagesStatus:
    """消息状态测试"""

    def test_mark_as_read(self, admin_client: APIClient):
        """测试标记消息已读"""
        list_resp = admin_client.get_messages(page=1, page_size=1)
        items = list_resp.get("data", {}).get("items", list_resp.get("data", {}).get("data", []))
        if items and len(items) > 0:
            msg_id = items[0].get("id", items[0].get("message_id"))
            if msg_id:
                resp = admin_client.mark_message_read(msg_id)
                assert resp.get("code") in (HTTPStatus.OK, HTTPStatus.OK)

    def test_delete_message(self, admin_client: APIClient):
        """测试删除消息"""
        resp = admin_client.delete_message(99999)
        assert resp.get("_status_code") in (HTTPStatus.NOT_FOUND, HTTPStatus.OK)

    def test_get_unread_count(self, admin_client: APIClient):
        """测试获取未读消息数"""
        resp = admin_client.get_unread_count()
        assert resp.get("code") == 200