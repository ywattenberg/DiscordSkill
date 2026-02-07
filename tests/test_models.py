from __future__ import annotations

import json

from discord_bot.models import EmbedField, NotifyRequest, NotifyResponse


class TestEmbedField:
    def test_defaults(self) -> None:
        field = EmbedField(name="Status", value="OK")
        assert field.name == "Status"
        assert field.value == "OK"
        assert field.inline is False

    def test_inline(self) -> None:
        field = EmbedField(name="Count", value="5", inline=True)
        assert field.inline is True


class TestNotifyRequest:
    def test_defaults(self) -> None:
        req = NotifyRequest(message="hello")
        assert req.title == "Notification"
        assert req.message == "hello"
        assert req.color == 0x5865F2
        assert req.fields == []
        assert req.wait is False
        assert req.timeout == 300

    def test_custom_values(self) -> None:
        fields = [EmbedField(name="F1", value="V1", inline=True)]
        req = NotifyRequest(
            title="Custom",
            message="body",
            color=0xFF0000,
            fields=fields,
            wait=True,
            timeout=60,
        )
        assert req.title == "Custom"
        assert req.color == 0xFF0000
        assert len(req.fields) == 1
        assert req.wait is True
        assert req.timeout == 60

    def test_serialization_roundtrip(self) -> None:
        req = NotifyRequest(
            message="test",
            fields=[EmbedField(name="A", value="B")],
        )
        data = json.loads(req.model_dump_json())
        req2 = NotifyRequest(**data)
        assert req == req2


class TestNotifyResponse:
    def test_success_minimal(self) -> None:
        resp = NotifyResponse(success=True, message_id=123)
        assert resp.success is True
        assert resp.message_id == 123
        assert resp.response is None
        assert resp.author is None
        assert resp.timestamp is None
        assert resp.error is None

    def test_success_with_response(self) -> None:
        resp = NotifyResponse(
            success=True,
            message_id=123,
            response="yes",
            author="user#1234",
            timestamp="2026-01-01T00:00:00+00:00",
        )
        assert resp.response == "yes"
        assert resp.author == "user#1234"

    def test_failure(self) -> None:
        resp = NotifyResponse(success=False, error="something broke")
        assert resp.success is False
        assert resp.error == "something broke"
        assert resp.message_id is None

    def test_json_output(self) -> None:
        resp = NotifyResponse(success=True, message_id=456)
        data = json.loads(resp.model_dump_json())
        assert data["success"] is True
        assert data["message_id"] == 456
        assert data["response"] is None
        assert data["error"] is None

    def test_timeout_response(self) -> None:
        resp = NotifyResponse(
            success=True,
            message_id=789,
            error="Timed out after 300s waiting for a response",
        )
        assert resp.success is True
        assert resp.response is None
        assert "Timed out" in (resp.error or "")
