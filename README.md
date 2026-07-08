# Axion

Axion is a private AI Operating System / AI Operating Layer. The long-term goal is a world-class personal assistant that can think, remember, plan, use tools, and control the computer safely.

Axion v0.2 does not connect to an AI API yet. It builds a clean local foundation using only the Python standard library.

## Vision

Axion should become a calm, capable operating layer between the user and the computer. It should help the user think clearly, store useful context, plan work, use safe tools, automate carefully, and coordinate future AI agents.

## Current v0.2 Features

- Terminal welcome screen
- Interactive command loop
- Local SQLite memory database
- Memory saving, listing, counting, and searching
- Notes saving, listing, counting, and searching
- Website opening
- Folder opening with common home-folder shortcuts
- Status report
- Axion identity command
- Basic built-in chat responses without an AI API
- Simple safety classification module for future actions
- Activity logging to `logs/axion.log`

## How To Run

From the project root:

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
- `/open <url>` - Open a website
- `/folder <path>` - Open a folder
- `/whoami` - Show Axion identity
- `/status` - Show Axion system status
- `/clear` - Clear the terminal screen

Folder shortcuts:

- `desktop`
- `downloads`
- `documents`
- `pictures`
- `videos`
- `music`

## Future Roadmap

- v0.3 AI Core
- v0.4 Voice
- v0.5 Apps control
- v0.6 Browser automation
- v0.7 Coding agent
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
