---
name: discord-notification
description: >
  Send Discord notifications with rich embeds and optionally wait for a human response.
  Trigger phrases: "notify on Discord", "send Discord message", "ask user on Discord",
  "Discord notification", "get response from Discord", "ping me on Discord",
  "tell the user on Discord", "ask for approval on Discord"
---

# Discord Notification Skill

Send a rich embed notification to Discord and optionally wait for a human reply.

## Usage

Run the CLI tool via uv:

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --message "Your message here" \
  [--title "Optional Title"] \
  [--color "#5865F2"] \
  [--fields '[{"name": "Field", "value": "Value", "inline": true}]'] \
  [--file /path/to/file] \
  [--wait] \
  [--timeout 300]
```

## When to use `--wait`

- **With `--wait`**: When you need human input, approval, or a decision before continuing. The bot will block until the user replies in the Discord channel or the timeout expires.
- **Without `--wait`** (fire-and-forget): For status updates, progress reports, or completion notifications where no reply is needed.

**IMPORTANT**: When using `--wait`, you MUST set the Bash tool timeout to 600000 (10 minutes, the maximum). The `--timeout` flag controls how long the bot waits for a Discord reply, but the Bash execution timeout must be at least as long or the command will be killed before a reply arrives. Set `--timeout 86400` (1 day) for the bot and always use `timeout: 600000` on the Bash tool call.

## Parsing the response

The script outputs a single JSON object to stdout:

```json
{
  "success": true,
  "message_id": 123456789,
  "response": "User's reply text or null",
  "author": "username#1234 or null",
  "timestamp": "ISO 8601 timestamp or null",
  "error": "error message or null"
}
```

- If `success` is `false`, check the `error` field.
- If `--wait` was used and the timeout expired, `success` is `true` but `response` is `null` and `error` contains a timeout note.

## Examples

### Fire-and-forget status update
```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --title "Build Complete" \
  --message "All tests passed. Deployment ready." \
  --color "#57F287"
```

### Ask for approval (blocking)
```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --title "Approval Needed" \
  --message "Ready to deploy to production. Reply 'yes' to confirm or 'no' to cancel." \
  --color "#FEE75C" \
  --wait \
  --timeout 600
```

### Send with file attachments
```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --title "Build Artifacts" \
  --message "Here are the build logs and test report." \
  --file /tmp/build.log \
  --file /tmp/test-report.html
```

### Report with fields
```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --title "Test Results" \
  --message "Test suite completed." \
  --fields '[{"name": "Passed", "value": "42", "inline": true}, {"name": "Failed", "value": "0", "inline": true}]'
```

## Setup

If the config file is not found, instruct the user to run `/discord-setup` to configure their bot token and channel ID.
