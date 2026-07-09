# Axion Architecture

Axion v0.7 is a modular Python terminal app that uses only the Python standard library. It keeps the local Ollama AI Core, projects, tasks, memory, notes, and safe tools, then adds a Safe File Manager for reversible file operations.

## Core

Core modules own the app loop, identity, status reporting, safety classification, activity logging, response validation, and fallback built-in chat responses.

Important files:

- `src/axion/core/app.py`
- `src/axion/core/identity.py`
- `src/axion/core/status.py`
- `src/axion/core/safety.py`
- `src/axion/core/activity_log.py`
- `src/axion/core/basic_responder.py`

## AI Core

The AI Core builds the final prompt and asks the local model for a response. It can include recent memories, active projects, and open tasks as context.

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

If the AI Core cannot return a valid response, normal chat falls back to a small built-in responder.

Important file:

- `src/axion/core/basic_responder.py`

## Commands

The command router receives terminal input and decides what system should handle it. Slash commands are routed to specific handlers. Normal text is handled by the app loop and routed to the AI Core.

Important file:

- `src/axion/commands/router.py`

## Memory

Memory uses SQLite at `data/axion.db`. It stores memories and notes with ids, content, and timestamps. It also supports counts and simple keyword search.

Important file:

- `src/axion/memory/sqlite_memory.py`

## Project Store

Projects use SQLite at `data/axion.db`. Projects are long-term containers for meaningful work. They have names, descriptions, statuses, optional folder paths, and project notes.

Important file:

- `src/axion/projects/project_store.py`

Project statuses are `active`, `paused`, and `done`.

## Task Store

Tasks use the same SQLite database at `data/axion.db`. The task store keeps open and done tasks in Axion's own `tasks` table. Deleting a task only removes a row from this table; it never deletes files.

Important file:

- `src/axion/tasks/task_store.py`

## Projects, Tasks, Notes, And AI

Projects are long-term containers. Tasks are action items. Project notes are project knowledge. The AI Core uses active project and open task context to answer better when the user asks what to work on next or asks for a plan.

```text
ACTIVE PROJECTS:
* Axion: AI Operating System built with Python and Ollama

OPEN TASKS:
* Push Axion v0.7 to GitHub
```

## Tools

Tools are safe, focused helpers that interact with the computer. In v0.7, Axion can open websites, folders, saved project folders, allowlisted apps, allowlisted terminal commands, and safe file operations.

Important files:

- `src/axion/tools/browser.py`
- `src/axion/tools/folder_opener.py`
- `src/axion/tools/app_launcher.py`
- `src/axion/tools/safe_runner.py`
- `src/axion/tools/file_manager.py`

## App Launcher

The app launcher uses an allowlist for safety. Users can launch known shortcuts like `notepad`, `calculator`, or `explorer`, but Axion does not accept raw paths and does not run arbitrary shell commands. The launcher uses `subprocess.Popen(..., shell=False)`.

This keeps app control useful while avoiding unsafe command execution.

## Safe Terminal Runner

The safe terminal runner powers `/run <command>`. It uses exact normalized allowlist matching and blocks dangerous keywords before attempting to run anything.

Allowlisted commands:

- `git status`
- `git branch`
- `git log`
- `dir`
- `python --version`
- `python -m axion`
- `ollama list`
- `ollama --version`

The runner uses `subprocess.run(..., shell=False)` and captures stdout and stderr. It does not execute arbitrary user commands.

## Safe File Manager

The Safe File Manager powers `/find`, `/find-ext`, `/move`, `/trash`, and `/screenshots`. It uses `pathlib` for paths and searches filenames case-insensitively.

Safety rules:

- No permanent delete
- No overwrite
- No folder moves yet, only file moves
- Trash operations move files to `data/trash/YYYY-MM-DD_HHMMSS/`
- Duplicate destination filenames get safe suffixes like `_1` and `_2`
- Screenshot cleanup requires `/screenshots clean --confirm`

Search skips heavy or system folders such as `.git`, `.venv`, `__pycache__`, `node_modules`, `.pnpm-store`, `AppData`, `Windows`, and `Program Files`.

## Safety

The safety layer classifies future actions as:

- `safe`
- `needs_confirmation`
- `blocked`

Dangerous actions are not executed in v0.7. This module exists so future automation has a clear safety checkpoint.

## Logs

Important actions are logged to `logs/axion.log`. The log folder is created automatically when Axion starts or writes its first log entry.

Logged actions include app start, command use, saved memories, saved notes, opened folders, opened URLs, app launches, app launch failures, task changes, project changes, safe command execution, command blocks, command rejections, file searches, file moves, file trashing, screenshot cleanup, file operation failures, AI response routing, model changes, and app exit.

## Future Agents

Future versions can add agents on top of this foundation. Agents should use the command, project, memory, task, AI Core, tool, safety, file manager, and log systems rather than bypassing them.
