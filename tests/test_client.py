from __future__ import annotations

import asyncio
import tempfile
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from discord_bot.client import BotConfig, parse_config, send_notification
from discord_bot.models import EmbedField, NotifyRequest


@pytest.fixture
def bot_config() -> BotConfig:
    return BotConfig(bot_token="fake-token", channel_id=123456, default_timeout=30)


@pytest.fixture
def basic_request() -> NotifyRequest:
    return NotifyRequest(message="Hello world")


@pytest.fixture
def wait_request() -> NotifyRequest:
    return NotifyRequest(message="Need approval", wait=True, timeout=5)


class TestParseConfig:
    def test_valid_config(self, tmp_path: Any) -> None:
        config_file = tmp_path / "config.md"
        config_file.write_text(
            "---\n"
            "bot_token: my-secret-token\n"
            "channel_id: 999888777\n"
            "default_timeout: 120\n"
            "---\n"
            "# Config\n"
        )
        config = parse_config(str(config_file))
        assert config.bot_token == "my-secret-token"
        assert config.channel_id == 999888777
        assert config.default_timeout == 120

    def test_default_timeout(self, tmp_path: Any) -> None:
        config_file = tmp_path / "config.md"
        config_file.write_text(
            "---\n"
            "bot_token: tok\n"
            "channel_id: 111\n"
            "---\n"
        )
        config = parse_config(str(config_file))
        assert config.default_timeout == 300

    def test_missing_token(self, tmp_path: Any) -> None:
        config_file = tmp_path / "config.md"
        config_file.write_text("---\nchannel_id: 111\n---\n")
        with pytest.raises(ValueError, match="bot_token is required"):
            parse_config(str(config_file))

    def test_missing_channel(self, tmp_path: Any) -> None:
        config_file = tmp_path / "config.md"
        config_file.write_text("---\nbot_token: tok\n---\n")
        with pytest.raises(ValueError, match="channel_id is required"):
            parse_config(str(config_file))

    def test_missing_frontmatter(self, tmp_path: Any) -> None:
        config_file = tmp_path / "config.md"
        config_file.write_text("no frontmatter here\n")
        with pytest.raises(ValueError, match="missing YAML frontmatter"):
            parse_config(str(config_file))

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            parse_config("/nonexistent/path.md")


class TestSendNotification:
    @pytest.mark.asyncio
    async def test_fire_and_forget(
        self, bot_config: BotConfig, basic_request: NotifyRequest
    ) -> None:
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_message = MagicMock()
        mock_message.id = 42
        mock_channel.send = AsyncMock(return_value=mock_message)

        with patch("discord_bot.client.discord.Client") as MockClient:
            instance = MockClient.return_value
            instance.get_channel = MagicMock(return_value=mock_channel)
            instance.close = AsyncMock()

            # Simulate on_ready being called during start
            async def fake_start(token: str) -> None:
                # Find the on_ready handler and call it
                for attr_name in dir(instance):
                    if attr_name == "event":
                        break
                # Call the on_ready callback that was registered
                if instance._on_ready:
                    await instance._on_ready()

            # Capture the on_ready handler
            instance._on_ready = None
            original_event = instance.event

            def capture_event(func: Any) -> Any:
                if func.__name__ == "on_ready":
                    instance._on_ready = func
                return func

            instance.event = capture_event
            instance.start = AsyncMock(side_effect=fake_start)

            result = await send_notification(bot_config, basic_request)

        assert result.success is True
        assert result.message_id == 42
        assert result.response is None

    @pytest.mark.asyncio
    async def test_embed_construction(
        self, bot_config: BotConfig
    ) -> None:
        """Test that embed fields are correctly added."""
        request = NotifyRequest(
            title="Test",
            message="Body",
            color=0xFF0000,
            fields=[
                EmbedField(name="F1", value="V1", inline=True),
                EmbedField(name="F2", value="V2", inline=False),
            ],
        )

        mock_channel = AsyncMock(spec=discord.TextChannel)
        sent_embed: discord.Embed | None = None

        async def capture_send(**kwargs: Any) -> MagicMock:
            nonlocal sent_embed
            sent_embed = kwargs.get("embed")
            msg = MagicMock()
            msg.id = 99
            return msg

        mock_channel.send = capture_send  # type: ignore[assignment]

        with patch("discord_bot.client.discord.Client") as MockClient:
            instance = MockClient.return_value
            instance.get_channel = MagicMock(return_value=mock_channel)
            instance.close = AsyncMock()
            instance._on_ready = None

            def capture_event(func: Any) -> Any:
                if func.__name__ == "on_ready":
                    instance._on_ready = func
                return func

            instance.event = capture_event

            async def fake_start(token: str) -> None:
                if instance._on_ready:
                    await instance._on_ready()

            instance.start = AsyncMock(side_effect=fake_start)

            result = await send_notification(bot_config, request)

        assert result.success is True
        assert sent_embed is not None
        assert sent_embed.title == "Test"
        assert sent_embed.description == "Body"
        assert sent_embed.color is not None
        assert sent_embed.color.value == 0xFF0000
        assert len(sent_embed.fields) == 2
        assert sent_embed.fields[0].name == "F1"
        assert sent_embed.fields[0].inline is True
        assert sent_embed.fields[1].name == "F2"
        assert sent_embed.fields[1].inline is False

    @pytest.mark.asyncio
    async def test_wait_with_reply(
        self, bot_config: BotConfig, wait_request: NotifyRequest
    ) -> None:
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_sent = MagicMock()
        mock_sent.id = 55
        mock_channel.send = AsyncMock(return_value=mock_sent)

        mock_reply = MagicMock()
        mock_reply.content = "approved"
        mock_reply.author = MagicMock()
        mock_reply.author.__str__ = lambda self: "user#1234"
        mock_reply.author.bot = False
        mock_reply.channel = MagicMock()
        mock_reply.channel.id = bot_config.channel_id
        mock_reply.created_at = datetime(2026, 1, 1, tzinfo=UTC)

        with patch("discord_bot.client.discord.Client") as MockClient:
            instance = MockClient.return_value
            instance.get_channel = MagicMock(return_value=mock_channel)
            instance.close = AsyncMock()
            instance.wait_for = AsyncMock(return_value=mock_reply)
            instance._on_ready = None

            def capture_event(func: Any) -> Any:
                if func.__name__ == "on_ready":
                    instance._on_ready = func
                return func

            instance.event = capture_event

            async def fake_start(token: str) -> None:
                if instance._on_ready:
                    await instance._on_ready()

            instance.start = AsyncMock(side_effect=fake_start)

            result = await send_notification(bot_config, wait_request)

        assert result.success is True
        assert result.message_id == 55
        assert result.response == "approved"
        assert result.author == "user#1234"

    @pytest.mark.asyncio
    async def test_wait_timeout(
        self, bot_config: BotConfig, wait_request: NotifyRequest
    ) -> None:
        mock_channel = AsyncMock(spec=discord.TextChannel)
        mock_sent = MagicMock()
        mock_sent.id = 77
        mock_channel.send = AsyncMock(return_value=mock_sent)

        with patch("discord_bot.client.discord.Client") as MockClient:
            instance = MockClient.return_value
            instance.get_channel = MagicMock(return_value=mock_channel)
            instance.close = AsyncMock()
            instance.wait_for = AsyncMock(side_effect=asyncio.TimeoutError)
            instance._on_ready = None

            def capture_event(func: Any) -> Any:
                if func.__name__ == "on_ready":
                    instance._on_ready = func
                return func

            instance.event = capture_event

            async def fake_start(token: str) -> None:
                if instance._on_ready:
                    await instance._on_ready()

            instance.start = AsyncMock(side_effect=fake_start)

            result = await send_notification(bot_config, wait_request)

        assert result.success is True
        assert result.message_id == 77
        assert result.response is None
        assert result.error is not None
        assert "Timed out" in result.error

    @pytest.mark.asyncio
    async def test_invalid_channel_type(
        self, bot_config: BotConfig, basic_request: NotifyRequest
    ) -> None:
        mock_channel = MagicMock(spec=discord.VoiceChannel)

        with patch("discord_bot.client.discord.Client") as MockClient:
            instance = MockClient.return_value
            instance.get_channel = MagicMock(return_value=mock_channel)
            instance.close = AsyncMock()
            instance._on_ready = None

            def capture_event(func: Any) -> Any:
                if func.__name__ == "on_ready":
                    instance._on_ready = func
                return func

            instance.event = capture_event

            async def fake_start(token: str) -> None:
                if instance._on_ready:
                    await instance._on_ready()

            instance.start = AsyncMock(side_effect=fake_start)

            result = await send_notification(bot_config, basic_request)

        assert result.success is False
        assert result.error is not None
        assert "not a text channel" in result.error
