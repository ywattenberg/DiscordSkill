---
description: Send a Discord notification with an optional wait for reply
allowed-tools: Bash, Read
argument-hint: <message>
---

# Discord Notify

Send a notification to Discord. The user's message after `/discord-notify` is the notification body.

## Steps

1. Read the plugin config from `.claude/discord-skill.local.md`. If it doesn't exist, tell the user to run `/discord-setup` first.

2. Build and run the command:

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --message "$ARGUMENTS" \
  --config ".claude/discord-skill.local.md"
```

If the user included flags like `--wait`, `--title`, `--fields`, or `--timeout` in their arguments, pass them through directly.

3. Parse the JSON output and present the result to the user:
   - On success: confirm the message was sent and show the message ID
   - If a response was received: show the responder and their message
   - On error: show the error message
