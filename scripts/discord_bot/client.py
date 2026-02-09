from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

import discord

from discord_bot.models import NotifyRequest, NotifyResponse

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB Discord limit


@dataclass
class BotConfig:
    bot_token: str
    channel_id: int
    default_timeout: int = 300


async def send_notification(config: BotConfig, request: NotifyRequest) -> NotifyResponse:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.guild_messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)
    result_future: asyncio.Future[NotifyResponse] = asyncio.get_event_loop().create_future()

    @client.event
    async def on_ready() -> None:
        try:
            channel = client.get_channel(config.channel_id)
            if channel is None:
                channel = await client.fetch_channel(config.channel_id)

            if not isinstance(channel, discord.TextChannel):
                result_future.set_result(
                    NotifyResponse(success=False, error="Channel is not a text channel")
                )
                await client.close()
                return

            embed = discord.Embed(
                title=request.title,
                description=request.message,
                color=request.color,
            )
            for field in request.fields:
                embed.add_field(name=field.name, value=field.value, inline=field.inline)

            # Validate file attachments
            for file_path in request.files:
                p = Path(file_path)
                if not p.is_file():
                    result_future.set_result(
                        NotifyResponse(success=False, error=f"File not found: {file_path}")
                    )
                    await client.close()
                    return
                if p.stat().st_size > MAX_FILE_SIZE:
                    result_future.set_result(
                        NotifyResponse(
                            success=False,
                            error=f"File exceeds 25MB limit: {file_path}",
                        )
                    )
                    await client.close()
                    return

            # Build discord.File objects after all validation passes
            discord_files = [discord.File(fp) for fp in request.files]

            sent = await channel.send(embed=embed, files=discord_files)

            if not request.wait:
                result_future.set_result(NotifyResponse(success=True, message_id=sent.id))
                await client.close()
                return

            # Wait for a human reply in the same channel
            timeout = request.timeout or config.default_timeout

            def check(m: discord.Message) -> bool:
                return m.channel.id == config.channel_id and not m.author.bot

            try:
                reply = await client.wait_for("message", check=check, timeout=timeout)
                result_future.set_result(
                    NotifyResponse(
                        success=True,
                        message_id=sent.id,
                        response=reply.content,
                        author=str(reply.author),
                        timestamp=reply.created_at.isoformat(),
                    )
                )
            except TimeoutError:
                result_future.set_result(
                    NotifyResponse(
                        success=True,
                        message_id=sent.id,
                        error=f"Timed out after {timeout}s waiting for a response",
                    )
                )
            finally:
                await client.close()

        except Exception as exc:
            if not result_future.done():
                result_future.set_result(NotifyResponse(success=False, error=str(exc)))
            await client.close()

    await client.start(config.bot_token)
    # Allow aiohttp connector to finalize cleanup
    await asyncio.sleep(0.25)
    return await result_future


def parse_config(path: str) -> BotConfig:
    """Parse a markdown settings file with YAML frontmatter to extract bot config."""
    with open(path) as f:
        content = f.read()

    # Extract YAML frontmatter between --- markers
    if not content.startswith("---"):
        raise ValueError(f"Config file {path} missing YAML frontmatter (must start with ---)")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Config file {path} has malformed YAML frontmatter")

    frontmatter = parts[1]

    config_vals: dict[str, str | int] = {}
    for line in frontmatter.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        config_vals[key.strip()] = value.strip()

    bot_token = config_vals.get("bot_token")
    channel_id = config_vals.get("channel_id")

    if not bot_token or not isinstance(bot_token, str):
        raise ValueError("bot_token is required in config frontmatter")
    if not channel_id:
        raise ValueError("channel_id is required in config frontmatter")

    default_timeout = int(config_vals.get("default_timeout", 300))

    return BotConfig(
        bot_token=bot_token,
        channel_id=int(channel_id),
        default_timeout=default_timeout,
    )
