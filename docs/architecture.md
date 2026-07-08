# Axion Architecture

Axion v0.2 is a small, modular Python terminal app. It uses only the Python standard library and keeps each system simple enough to understand.

## Core

Core modules own the app loop, identity, status reporting, safety classification, activity logging, and built-in non-AI chat responses.

Important files:

- `src/axion/core/app.py`
- `src/axion/core/identity.py`
- `src/axion/core/status.py`
- `src/axion/core/safety.py`
- `src/axion/core/activity_log.py`
- `src/axion/core/basic_responder.py`

## Commands

The command router receives terminal input and decides what system should handle it. Slash commands are routed to specific handlers. Normal text is routed to the basic responder until the future AI Core exists.

Important file:

- `src/axion/commands/router.py`

## Memory

Memory uses SQLite at `data/axion.db`. It stores memories and notes with ids, content, and timestamps. It also supports counts and simple keyword search.

Important file:

- `src/axion/memory/sqlite_memory.py`

## Tools

Tools are safe, focused helpers that interact with the computer. In v0.2, Axion can open websites and folders.

Important files:

- `src/axion/tools/browser.py`
- `src/axion/tools/folder_opener.py`

## Safety

The safety layer classifies future actions as:

- `safe`
- `needs_confirmation`
- `blocked`

Dangerous actions are not executed in v0.2. This module exists so future automation has a clear safety checkpoint.

## Logs

Important actions are logged to `logs/axion.log`. The log folder is created automatically when Axion starts or writes its first log entry.

Logged actions include app start, command use, saved memories, saved notes, opened folders, opened URLs, and app exit.

## Future Agents

Future versions can add agents on top of this foundation. Agents should use the command, memory, tool, safety, and log systems rather than bypassing them.
