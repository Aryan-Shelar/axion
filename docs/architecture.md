# Axion Architecture

Axion v0.3 is a small, modular Python terminal app. It uses only the Python standard library and adds a local AI Core through Ollama.

## Core

Core modules own the app loop, identity, status reporting, safety classification, activity logging, and fallback built-in chat responses.

Important files:

- `src/axion/core/app.py`
- `src/axion/core/identity.py`
- `src/axion/core/status.py`
- `src/axion/core/safety.py`
- `src/axion/core/activity_log.py`
- `src/axion/core/basic_responder.py`

## AI Core

The AI Core builds the final prompt and asks the local model for a response. It can include recent memories as context.

Important file:

- `src/axion/ai/ai_core.py`

## Ollama Client

The Ollama client talks to the local Ollama HTTP API at `http://localhost:11434`. It checks availability and calls `/api/generate`.

Important file:

- `src/axion/ai/ollama_client.py`

## Prompt Layer

The prompt layer stores Axion's system prompt separately from the client and command router.

Important file:

- `src/axion/ai/prompts.py`

## Fallback Responder

If Ollama is unavailable, normal chat falls back to a small built-in responder. This keeps Axion useful even before the local model is running.

Important file:

- `src/axion/core/basic_responder.py`

## Commands

The command router receives terminal input and decides what system should handle it. Slash commands are routed to specific handlers. Normal text is routed through the AI Core when Ollama is available.

Important file:

- `src/axion/commands/router.py`

## Memory

Memory uses SQLite at `data/axion.db`. It stores memories and notes with ids, content, and timestamps. It also supports counts and simple keyword search.

Important file:

- `src/axion/memory/sqlite_memory.py`

## Tools

Tools are safe, focused helpers that interact with the computer. In v0.3, Axion can open websites and folders.

Important files:

- `src/axion/tools/browser.py`
- `src/axion/tools/folder_opener.py`

## Safety

The safety layer classifies future actions as:

- `safe`
- `needs_confirmation`
- `blocked`

Dangerous actions are not executed in v0.3. This module exists so future automation has a clear safety checkpoint.

## Logs

Important actions are logged to `logs/axion.log`. The log folder is created automatically when Axion starts or writes its first log entry.

Logged actions include app start, command use, saved memories, saved notes, opened folders, opened URLs, AI response requests, Ollama unavailability, model changes, and app exit.

## Future Agents

Future versions can add agents on top of this foundation. Agents should use the command, memory, AI Core, tool, safety, and log systems rather than bypassing them.
