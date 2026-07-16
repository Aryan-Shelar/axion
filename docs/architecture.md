# Axion Architecture

Axion v2.0 is a modular Python terminal app built primarily with the Python standard library. It preserves the local Ollama AI Core, projects, tasks, memory, notes, safe tools, Safe File Manager, Trash Manager, Browser Research Lite, voice output, Agent Mode, Agent Execution Mode, and Smart Laptop Organizer while adding the Smart Productivity Layer.

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
* Publish and review Axion v2.0 on its feature branch
```

## Tools

Tools are safe, focused helpers that interact with the computer. In v1.3, Axion can open websites, folders, saved project folders, allowlisted apps, allowlisted terminal commands, safe file operations, trash files safely, restore files from Axion Trash, organize messy folders after preview, and open browser research searches.

Important files:

- `src/axion/tools/browser.py`
- `src/axion/tools/folder_opener.py`
- `src/axion/tools/app_launcher.py`
- `src/axion/tools/safe_runner.py`
- `src/axion/tools/file_manager.py`
- `src/axion/tools/trash_manager.py`
- `src/axion/tools/organizer.py`
- `src/axion/tools/web_research.py`

## Browser Research Lite

Browser Research Lite powers `/web search`, `/web open`, `/web youtube`, and `/web github`. It uses `webbrowser` to open browser pages and `urllib.parse.quote_plus` to safely encode search queries.

Axion still does not scrape websites or control website sessions. The v2.0 extension can detect and fill conservatively mapped fields only after explicit user action through the token-authenticated localhost bridge, and it never submits forms.

Supported destinations:

- Google search
- YouTube search
- GitHub search
- Direct `http` and `https` URLs

## Voice Output

The voice output module powers `/say`, `/voice`, `/voice on`, and `/voice off`. On Windows, it uses PowerShell with `System.Speech.Synthesis` through `subprocess.run(..., shell=False)`.

Important files:

- `src/axion/voice/__init__.py`
- `src/axion/voice/speaker.py`

Voice output is optional. When voice mode is on, normal AI chat replies are spoken aloud after they are printed. Command responses are not automatically spoken yet, except `/say`.

Microphone input is not included yet. Voice input can be added later with separate safety and privacy controls.

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

## Trash Manager

The Trash Manager tracks Axion Trash metadata in `data/trash/trash_index.json`. The File Manager moves files to `data/trash/`, and the Trash Manager can list, inspect, restore, and preview emptying trash.

Safety rules:

- Restore never overwrites existing files
- Empty trash only touches Axion Trash
- Permanent deletion requires `/empty-trash --confirm`

## Smart Organizer

The Smart Laptop Organizer powers `/organize scan`, `/organize preview`, `/organize apply --confirm`, `/organize undo-last`, `/organize status`, and `/organize clear`.

Important file:

- `src/axion/tools/organizer.py`

The organizer has five small parts:

- Scanner: scans only direct files in the target folder
- Classifier: maps filenames and extensions into categories like screenshots, PDFs, receipts, code, and unknown
- Destination mapper: chooses safe folders under known Windows home folders such as Documents, Pictures, Downloads, and Videos
- Move session logger: records each applied move in `data/organizer/organizer_state.json`
- Undo system: reverses only the latest organizer apply session when it can do so without overwriting

Safety rules:

- Never move files without preview first
- Apply requires `/organize apply --confirm`
- Never overwrite existing files
- Never permanently delete files
- Default scans are shallow and skip hidden, dependency, virtual environment, source control, and system folders

## Safety

The safety layer classifies future actions as:

- `safe`
- `needs_confirmation`
- `blocked`

Dangerous actions are not executed in v1.3. This module exists so future automation has a clear safety checkpoint.

## Logs

Important actions are logged to `logs/axion.log`. The log folder is created automatically when Axion starts or writes its first log entry.

Logged actions include app start, command use, saved memories, saved notes, opened folders, opened URLs, app launches, app launch failures, task changes, project changes, safe command execution, command blocks, command rejections, file searches, file moves, file trashing, screenshot cleanup, trash manager activity, organizer scan, organizer preview, organizer apply, organizer undo, organizer clear, file operation failures, web searches, opened web URLs, voice output, voice failures, voice mode changes, AI response routing, model changes, and app exit.

## Future Agents

Future versions can add deeper agents on top of this foundation. Agents should use the command, project, memory, task, AI Core, tool, safety, file manager, trash manager, organizer, voice, and log systems rather than bypassing them.
## Axion v2.0 Smart Productivity Layer

The command router coordinates the Smart File Finder, DPAPI-backed Profile Vault, localhost Autofill Bridge, browser extension, and conservative Windows Autofill beta. Search persists result metadata for selective actions; all trash operations pass through the Axion Trash Manager. Bulk and natural-language destructive intents stop at preview unless the explicit command includes `--confirm`.
