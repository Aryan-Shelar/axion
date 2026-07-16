# Browser extension setup

1. Run Axion and `/autofill start`.
2. Open `chrome://extensions` or `edge://extensions`, enable Developer mode, select **Load unpacked**, and choose `browser_extension`.
3. Paste the bridge port and session token into the popup and save.
4. Run `/autofill allow-site example.com` for the intended domain.
5. Detect and preview mappings, then explicitly click **Fill Safe Fields**. For one sensitive attempt, first run `/autofill approve-sensitive`.

Use `tests/manual/autofill_test.html` for a local safety check. Password, OTP, card, and CVV fields must remain untouched.
