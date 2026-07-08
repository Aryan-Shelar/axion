# Axion

Axion is a private AI Operating System / AI Operating Layer. The long-term goal is a world-class personal assistant that can think, remember, plan, use tools, and control the computer safely.

Axion v0.4 adds safe app launching and a local task manager while keeping the Ollama AI Core, memory, notes, folders, websites, status, and logs.

## Vision

Axion should become a calm, capable operating layer between the user and the computer. It should help the user think clearly, store useful context, plan work, use safe tools, automate carefully, and coordinate future AI agents.

## Current v0.4 Features

- Terminal welcome screen
- Interactive command loop
- Local Ollama AI Core
- Default model: `llama3.2:1b`
- Runtime model switching
- Recent memory and open task context for AI chat
- Fallback built-in responder when AI Core cannot answer
- Local SQLite memory database
- Memory saving, listing, counting, and searching
- Notes saving, listing, counting, and searching
- Task manager for open and completed tasks
- Safe app launcher with allowlisted shortcuts
- Website opening
- Folder opening with common home-folder shortcuts
- Status report with AI and task counts
- Axion identity command
- Simple safety classification module for future actions
- Activity logging to `logs/axion.log`

## Ollama Setup

Install and start Ollama, then pull the default local model:

```bash
ollama pull llama3.2:1b
```

Then run Axion:

```bash
python -m pip install -e .
python -m axion
```

## Commands

- `/help` - Show commands
- `/exit` - Exit Axion
- `/time` - Show the current local time
- `/remember <text>` - Save a memory
- `/memories` - List saved memories
- `/search-memory <keyword>` - Search saved memories
- `/note <title> :: <content>` - Save a note
- `/notes` - List saved notes
- `/search-notes <keyword>` - Search saved notes
- `/task add <title>` - Save a task
- `/tasks` - List all tasks
- `/tasks open` - List open tasks
- `/tasks done` - List completed tasks
- `/task done <id>` - Mark a task done
- `/task delete <id>` - Delete a task from Axion's task table
- `/apps` - List available app shortcuts
- `/app <name>` - Open an allowlisted app
- `/open <url>` - Open a website
- `/folder <path>` - Open a folder
- `/whoami` - Show Axion identity
- `/status` - Show Axion system status
- `/ai-status` - Show local AI Core status
- `/model` - Show the current AI model
- `/model <name>` - Change the current AI model for this session
- `/clear` - Clear the terminal screen

App shortcuts:

- `notepad`
- `calculator`
- `calc`
- `chrome`
- `edge`
- `vscode`
- `cmd`
- `explorer`

Folder shortcuts:

- `desktop`
- `downloads`
- `documents`
- `pictures`
- `videos`
- `music`

## Examples

```text
/apps
/app notepad
/app calculator
/task add Build Axion v0.4
/task add Push Axion to GitHub
/tasks
/task done 1
/tasks open
/tasks done
/status
what should I do next?
/exit
```

## Future Roadmap

- v0.5 Project Manager
- v0.6 Safe Terminal Commands
- v0.7 File Search
- v0.8 Voice
- v1.0 AI Operating Layer

## Project Layout

```text
.
|-- README.md
|-- pyproject.toml
|-- docs/
|-- src/
|   `-- axion/
|-- data/
|-- logs/
`-- tests/
```
