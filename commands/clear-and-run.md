---
description: "Run a command in a fresh context (forked subagent)"
allowed-tools: Bash, Read
argument-hint: <command>
context: fork
agent: general-purpose
---

# Clear and Run

You are running in a **fresh, isolated context** with no prior conversation history.

If `$ARGUMENTS` is not empty, immediately use the Skill tool to invoke `discord-skill:$ARGUMENTS`.

If `$ARGUMENTS` is empty, tell the user: "Context forked. Ready for instructions."
