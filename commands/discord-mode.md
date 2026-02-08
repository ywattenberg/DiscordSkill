---
description: "Enter Discord-only mode — all interactions happen via Discord"
allowed-tools: Bash, Read
---

# Discord-Only Mode

You are now in **Discord-only mode**. All communication with the user happens through Discord — not the terminal. Treat Discord as your sole interface for questions, status updates, progress reports, and results.

## Rules

1. **Every message goes through Discord.** Use `discord-notify --wait` for all communication: asking questions, reporting progress, sharing results, requesting clarification, or checking in. **Never ask the user anything in the terminal — all questions, confirmations, and prompts MUST be sent via Discord.** Do not use the AskUserQuestion tool or any other terminal-based interaction method.

2. **Minimize terminal output.** Only print brief mechanical status lines like `Sending to Discord...` or `Received reply from user.` Do not duplicate message content or questions in the terminal.

3. **Always use `--wait`** since this is interactive mode — every message expects a reply.

4. **Always set timeouts high:**
   - Bash tool timeout: `600000` (maximum)
   - Bot `--timeout 86400` (1 day) so the user has plenty of time to respond

5. **Parse replies and act on them.** When the user replies on Discord, treat their response exactly as if they typed it in the terminal. Continue working based on their instructions.

6. **Exit conditions.** If the user replies with "exit", "stop", or "done" (case-insensitive), end Discord-only mode and return to normal terminal interaction. Confirm in the terminal that Discord-only mode has ended.

## Command Template

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --message "<your message here>" \
  --wait \
  --timeout 86400 \
  --config ".claude/discord-skill.local.md"
```

## Getting Started

Right now, send an initial greeting to Discord to confirm the mode is active:

```bash
uv run --project ${CLAUDE_PLUGIN_ROOT} discord-notify \
  --message "Discord-only mode is active. I'll send all messages here. Reply with your instructions, or say **done** to exit this mode." \
  --wait \
  --timeout 86400 \
  --config ".claude/discord-skill.local.md"
```

Then read the user's reply and proceed accordingly. Stay in Discord-only mode until the user says "exit", "stop", or "done".
