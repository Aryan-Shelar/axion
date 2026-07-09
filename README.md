# Axion

Axion is a private AI Operating System / AI Operating Layer. The long-term goal is a world-class personal assistant that can think, remember, plan, use tools, and control the computer safely.

Axion v0.6 adds a safe terminal runner. It can run a small allowlist of useful commands through `/run`, blocks dangerous commands, and never uses `shell=True`.

## Current v0.6 Features

- Local Ollama AI Core with default model `llama3.2:1b`
- Memory and notes
- Project manager with statuses, folders, and notes
- Task manager for open and completed tasks
- Active project and open task context for AI chat
- Safe app launcher with allowlisted shortcuts
- Safe terminal runner with allowlisted commands
- Website and folder opening
- Status report with AI, project, task, and safe runner details
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
- `/open <url>`
- `/folder <path>`
- `/whoami`
- `/status`
- `/ai-status`
- `/model`
- `/model <name>`
- `/clear`

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
/project create Axion :: AI Operating System built with Python and Ollama
/task add Push Axion v0.6 to GitHub
/run git status
/run python --version
/run del test.txt
/status
what should I work on next?
/exit
```

## Roadmap

- v0.7 File Search
- v0.8 Voice
- v0.9 Browser Automation
- v1.0 Agent System
