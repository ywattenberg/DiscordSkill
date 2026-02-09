# DiscordSkill

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that sends rich embed notifications to Discord and optionally waits for a human response.

Use it to reach out via Discord during long-running tasks, ask for approval or input, or report status — and receive a reply back as structured JSON.

## Features

- Rich embed notifications (title, description, color, fields)
- File attachments (up to 25MB each, multiple supported)
- Fire-and-forget status updates
- Blocking wait for human reply with configurable timeout
- Structured JSON output
- Auto-invocable skill + manual `/discord-notify` slash command

## Installation

Load the plugin when starting Claude Code:

```bash
claude --plugin-dir /path/to/DiscordSkill
```

Then run `/discord-setup` to configure your bot token and channel ID.

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and add a bot
3. Enable the **Message Content** privileged intent in the bot settings
4. Invite the bot to your server with **Send Messages**, **Read Message History**, and **Attach Files** permissions
5. Copy the bot token and a channel ID for use during `/discord-setup`

## Usage

### Slash Commands

**`/discord-notify <message>`** — Send a notification manually.

**`/discord-setup`** — Interactive configuration wizard for bot token, channel ID, and default timeout.

### Auto-Invocation

Claude can trigger the skill automatically when it needs to notify you or ask for input on Discord. Trigger phrases include "notify on Discord", "ask user on Discord", "send Discord message", etc.

### CLI

```bash
uv run --project /path/to/DiscordSkill discord-notify \
  --message "Your message here" \
  --title "Optional Title" \
  --color "#5865F2" \
  --fields '[{"name": "Field", "value": "Value", "inline": true}]' \
  --file /path/to/attachment \
  --wait \
  --timeout 300
```

### JSON Output

```json
{
  "success": true,
  "message_id": 123456789,
  "response": "User reply text or null",
  "author": "username#1234 or null",
  "timestamp": "ISO 8601 or null",
  "error": "error message or null"
}
```

## Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                        # install dependencies
uv run pytest tests/                           # run tests
uv run mypy scripts/discord_bot/               # type check
uv run ruff check scripts/discord_bot/         # lint
uv run ruff format scripts/discord_bot/        # format
```

## License

MIT
