# Axion Roadmap

## v1.3 Smart Laptop Organizer

- Identity and personality foundation
- Improved terminal welcome screen
- Expanded command router
- Local Ollama AI Core
- Runtime model switching
- Fallback responder when Ollama is unavailable
- Local SQLite memory and notes
- Memory and note search
- Browser and folder tools
- Safe app launcher with allowlisted shortcuts
- SQLite task manager
- SQLite project manager
- Active project and open task context for AI chat
- Allowlisted safe terminal command runner
- Safe file search by name and extension
- Safe file moves without overwrite
- Axion Trash for reversible file cleanup
- Screenshot preview and confirmed cleanup
- Optional Windows text-to-speech output
- Voice mode for normal AI chat replies
- Safe Google, YouTube, and GitHub search opening
- Safe direct browser URL opening
- Trash Manager and Restore System
- Agent Mode and Agent Execution Mode
- Smart Laptop Organizer with scan, preview, confirmed apply, and undo-last
- Status reporting
- Basic safety classification
- Activity logging
- Built-in fallback responses when the AI Core is unavailable

## v2.0 Smart Productivity Layer

- Smart filename search and fuzzy matching
- Selective and confirmed bulk file actions through Axion Trash
- Local DPAPI-protected Personal Profile Vault
- Localhost-only, token-authenticated autofill bridge
- Chrome and Edge Manifest V3 extension
- Safe-field previews and explicit browser fill actions
- Intelligent document upload suggestions
- Conservative Windows App Autofill Beta architecture
- Deterministic natural-language productivity previews
- Updated status, help, security documentation, and automated tests

## v2.0 Acceptance and Hardening Plan

- Complete manual CLI acceptance testing with disposable files
- Validate the unpacked extension in current Chrome and Edge releases
- Verify DPAPI behavior directly on Windows
- Expand router, Trash Manager integration, request validation, and log-redaction tests
- Review domain normalization, token lifecycle, path disclosure, and shutdown behavior
- Improve maintainability of compact command and extension handlers
- Run final compilation, complete tests, diff checks, and release review before merging

## Future Browser Automation

- Add broader browser automation helpers beyond safe autofill
- Keep user-visible confirmation for important actions

## Future AI Operating Layer

- Combine memory, projects, tasks, tools, safety, apps, browser, voice, and agents into a reliable personal operating layer
