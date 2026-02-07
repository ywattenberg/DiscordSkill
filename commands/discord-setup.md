---
description: Configure the Discord notification bot (token, channel, timeout)
allowed-tools: Read, Write, Bash
---

# Discord Setup

Guide the user through configuring the Discord notification skill.

## Steps

1. **Ask for the bot token**: Ask the user for their Discord bot token. Remind them they can get one from the [Discord Developer Portal](https://discord.com/developers/applications) by creating a bot and copying the token. The bot needs the following permissions/intents:
   - Send Messages
   - Read Message History
   - Message Content Intent (privileged, must be enabled in the bot settings)

2. **Ask for the channel ID**: Ask for the Discord channel ID where notifications should be sent. Remind them they can get this by enabling Developer Mode in Discord settings, then right-clicking a channel and selecting "Copy Channel ID".

3. **Ask for default timeout**: Ask what the default wait timeout should be in seconds (default: 300).

4. **Write the config file** at `.claude/discord-skill.local.md`:

```markdown
---
bot_token: <their token>
channel_id: <their channel id>
default_timeout: <their timeout>
---

# Discord Skill Configuration

This file contains local configuration for the Discord notification skill.
Do not commit this file to version control — it contains your bot token.
```

5. **Update .gitignore**: Check if `.gitignore` exists and if it already contains a rule for `.claude/*.local.md`. If not, append the rule:

```
# Discord skill local config (contains secrets)
.claude/*.local.md
```

6. **Install dependencies**: Run:

```bash
uv sync --project ${CLAUDE_PLUGIN_ROOT}
```

7. **Confirm**: Tell the user setup is complete and they can now use `/discord-notify` or the auto-invoked skill.
