---
description: "Clear conversation context and run a command"
allowed-tools: Bash, Read
argument-hint: <command>
---

# Clear and Run

Clear the conversation context, then invoke another slash command.

## Steps

1. Tell the user you are about to clear context and run `/$ARGUMENTS` (or just clear context if no argument was provided).

2. Invoke the built-in `/clear` command to reset conversation history.

3. After context is cleared:
   - If an argument was provided, immediately invoke `/$ARGUMENTS` as a slash command.
   - If no argument was provided, confirm to the user that context has been reset.
