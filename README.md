# Axion

Axion is a private AI Operating System / AI Operating Layer. The long-term goal is a world-class personal assistant that can think, remember, plan, use tools, and control the computer safely.

Axion v1.3 adds Smart Laptop Organizer. Axion can scan messy folders, preview suggested file moves, apply them only after explicit confirmation, and undo the latest organizer move session.

## Current v1.3 Features

- Local Ollama AI Core with default model `llama3.2:1b`
- Memory and notes
- Project manager
- Task manager
- Safe app launcher
- Safe terminal runner
- Safe File Manager
- Trash Manager and Restore System
- Smart Laptop Organizer
- Browser Research Lite
- Optional Windows voice output
- Agent Mode
- Agent Execution Mode
- Activity logging to `logs/axion.log`

## Run

```bash
ollama pull llama3.2:1b
python -m pip install -e .
python -m axion
```

## Commands

- `/help`
- `/exit`
- `/time`
- `/remember <text>`
- `/memories`
- `/search-memory <keyword>`
- `/note <title> :: <content>`
- `/notes`
- `/search-notes <keyword>`
- `/project create <name>`
- `/project create <name> :: <description>`
- `/projects`
- `/projects active`
- `/projects paused`
- `/projects done`
- `/project show <id_or_name>`
- `/project status <id_or_name> <active|paused|done>`
- `/project folder <id_or_name> :: <folder_path>`
- `/project open <id_or_name>`
- `/project note <id_or_name> :: <note>`
- `/project notes <id_or_name>`
- `/task add <title>`
- `/tasks`
- `/tasks open`
- `/tasks done`
- `/task done <id>`
- `/task delete <id>`
- `/apps`
- `/app <name>`
- `/run <command>`
- `/say <text>`
- `/voice`
- `/voice on`
- `/voice off`
- `/web search <query>`
- `/web open <url>`
- `/web youtube <query>`
- `/web github <query>`
- `/find <query>`
- `/find <query> in <folder>`
- `/find-ext <extension>`
- `/find-ext <extension> in <folder>`
- `/move <source_file_path> :: <destination_folder>`
- `/trash <file_path>`
- `/screenshots preview`
- `/screenshots clean --confirm`
- `/trash-list`
- `/trash-show <id>`
- `/restore <id>`
- `/restore <id> :: <destination_folder>`
- `/empty-trash preview`
- `/empty-trash --confirm`
- `/organize scan downloads`
- `/organize scan desktop`
- `/organize scan documents`
- `/organize scan pictures`
- `/organize scan <folder_path>`
- `/organize preview`
- `/organize apply --confirm`
- `/organize undo-last`
- `/organize status`
- `/organize clear`
- `/open <url>`
- `/folder <path>`
- `/whoami`
- `/status`
- `/ai-status`
- `/model`
- `/model <name>`
- `/clear`

## Safe File Manager

Axion never permanently deletes files. The `/trash` command and screenshot cleaner move files into:

```text
data/trash/YYYY-MM-DD_HHMMSS/
```

File manager safety rules:

- No permanent delete
- No overwrite
- Files only, no folder moves yet
- Trash operations are reversible from Axion Trash
- Screenshot cleanup requires `/screenshots clean --confirm`

## Smart Laptop Organizer

The Smart Laptop Organizer is preview-first. It scans only direct files in a target folder, suggests category folders, and moves files only after `/organize apply --confirm`.

Examples:

- `/organize scan C:\Users\ADMIN\Downloads\axion_organizer_test`
- `/organize preview`
- `/organize status`
- `/organize apply --confirm`
- `/organize undo-last`
- `/organize clear`

Organizer safety rules:

- Scan first
- Preview before moving
- Apply requires `--confirm`
- No permanent deletion
- No overwrites; duplicate names use safe suffixes like `_1`
- `/organize undo-last` reverses only the latest organizer apply session

## Voice Output

Voice output is optional and Windows-only. Axion uses PowerShell with `System.Speech.Synthesis` through Python's standard library. Microphone input is not included yet.

Examples:

- `/say Hello Shelar`
- `/voice`
- `/voice on`
- `/voice off`

## Browser Research Lite

Browser Research Lite opens safe browser URLs and search pages. It does not scrape websites, fill forms, click pages, or control browser sessions yet.

Examples:

- `/web search AI automation tools`
- `/web youtube Python beginner tutorial`
- `/web github ollama python`
- `/web open github.com`

## Safe Run Commands

The `/run` command only supports these allowlisted commands for now:

- `git status`
- `git branch`
- `git log`
- `dir`
- `python --version`
- `python -m axion`
- `ollama list`
- `ollama --version`

Dangerous commands such as `del`, `rmdir`, `format`, `shutdown`, `powershell`, `rm`, and `taskkill` are blocked.

## Examples

```text
/web search AI automation tools
/web youtube Python beginner tutorial
/web github ollama python
/web open github.com
/voice
/say Hello Shelar, Axion can speak now.
/voice on
hello axion
/voice off
hello again
/find axion
/find-ext py in D:\Axion
/screenshots preview
/screenshots clean
/screenshots clean --confirm
/trash C:\Users\ADMIN\Downloads\test.png
/move C:\Users\ADMIN\Downloads\test.txt :: C:\Users\ADMIN\Documents
/organize scan C:\Users\ADMIN\Downloads\axion_organizer_test
/organize preview
/organize apply --confirm
/organize undo-last
/status
/exit
```

If a test file does not exist, Axion shows a friendly error and keeps running.

## Roadmap

- Future Browser Automation
- Safer app control
- Voice input
- Deeper project automation

## Axion v1.2 - Trash Manager + Restore System

Commands:

```text
/trash-list
/trash-show <id>
/restore <id>
/restore <id> :: <destination_folder>
/empty-trash preview
/empty-trash --confirm
```

Safety rules:

- Restore never overwrites existing files.
- Empty trash only touches Axion Trash.
- Permanent deletion requires explicit confirmation.

## Axion v1.3 - Smart Laptop Organizer

Commands:

```text
/organize scan downloads
/organize scan desktop
/organize scan documents
/organize scan pictures
/organize scan <folder_path>
/organize preview
/organize apply --confirm
/organize undo-last
/organize status
/organize clear
```

The organizer stores move sessions in `data/organizer/organizer_state.json`, which is ignored by git. It never deletes files and never overwrites existing files.
