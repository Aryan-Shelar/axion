# Axion browser extension

Load this folder as an unpacked Manifest V3 extension in Chrome or Edge. Start `/autofill start`, copy its random session token into the popup, allow the current domain with `/autofill allow-site example.com`, then detect and preview fields before filling. Sensitive fields require `/autofill approve-sensitive` for each attempt. The extension never submits forms and cannot silently attach local files; use its upload hint and choose the file manually.
