# Axion

Axion is a private AI Operating System / AI Operating Layer. The long-term goal is a world-class personal assistant that can think, remember, plan, use tools, and control the computer safely.

Axion v0.7 adds a Safe File Manager. It can search for files, move files without overwriting, and move unwanted files into Axion Trash instead of permanently deleting them.

## Current v0.7 Features

- Local Ollama AI Core with default model `llama3.2:1b`
- Memory and notes
- Project manager with statuses, folders, and notes
- Task manager for open and completed tasks
- Active project and open task context for AI chat
- Safe app launcher with allowlisted shortcuts
- Safe terminal runner with allowlisted commands
- Safe File Manager for search, move, trash, and screenshot cleanup
- Website and folder opening
- Status report with AI, project, task, runner, and file manager details
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
- `/find <query>`
- `/find <query> in <folder>`
- `/find-ext <extension>`
- `/find-ext <extension> in <folder>`
- `/move <source_file_path> :: <destination_folder>`
- `/trash <file_path>`
- `/screenshots preview`
- `/screenshots clean --confirm`
- `/open <url>`
- `/folder <path>`
- `/whoami`
- `/status`
- `/ai-status`
- `/model`
- `/model <name>`
- `/clear`

## Safe File Manager

Axion v0.7 never permanently deletes files. The `/trash` command and screenshot cleaner move files into:

```text
data/trash/YYYY-MM-DD_HHMMSS/
```

File manager safety rules:

- No permanent delete
- No overwrite
- Files only, no folder moves yet
- Trash operations are reversible from Axion Trash
- Screenshot cleanup requires `/screenshots clean --confirm`

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
/find axion
/find-ext py in D:\Axion
/screenshots preview
/screenshots clean
/screenshots clean --confirm
/trash C:\Users\ADMIN\Downloads\test.png
/move C:\Users\ADMIN\Downloads\test.txt :: C:\Users\ADMIN\Documents
/status
/exit
```

If a test file does not exist, Axion shows a friendly error and keeps running.

## Roadmap

- v0.8 Voice
- v0.9 Browser Automation
- v1.0 Agent System
