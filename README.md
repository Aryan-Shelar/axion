# Axion

Axion is a private AI Operating System / AI Operating Layer. The long-term goal is a world-class personal assistant that can think, remember, plan, use tools, and control the computer safely.

Axion v0.5 adds a Project Manager so Axion can track long-term projects, project notes, project folders, project status, and use active projects as AI context.

## Current v0.5 Features

- Local Ollama AI Core with default model `llama3.2:1b`
- Memory and notes
- Project manager with statuses, folders, and notes
- Task manager for open and completed tasks
- Active project and open task context for AI chat
- Safe app launcher with allowlisted shortcuts
- Website and folder opening
- Status report with AI, project, and task counts
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
- `/open <url>`
- `/folder <path>`
- `/whoami`
- `/status`
- `/ai-status`
- `/model`
- `/model <name>`
- `/clear`

## Examples

```text
/project create Axion :: AI Operating System built with Python and Ollama
/projects
/project show Axion
/project folder Axion :: D:\Axion
/project open Axion
/project note Axion :: Build v0.5 Project Manager
/project notes Axion
/task add Push Axion v0.5 to GitHub
/status
what should I work on next?
/exit
```

## Roadmap

- v0.6 Safe Terminal Commands
- v0.7 File Search
- v0.8 Voice
- v0.9 Browser Automation
- v1.0 Agent System
