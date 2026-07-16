"""Deterministic natural-language productivity previews."""
import re
def translate_intent(text: str) -> str | None:
    value=text.strip()
    m=re.match(r"find (?:my |the )?(.+?)(?: file)? in (downloads|documents|desktop|pictures|videos)$",value,re.I)
    if m:return f"/find-name {m.group(1)} in {m.group(2)}"
    m=re.match(r"(?:remove|trash) files containing (.+?) from (downloads|documents|desktop)$",value,re.I)
    if m:return f"Safety preview only. Run /trash-matches {m.group(1)} in {m.group(2)} to preview; Axion will not move anything without --confirm."
    if re.search(r"fill this form using my profile",value,re.I):return "Start /autofill start, allow the site, then preview and click Fill Safe Fields. Axion never submits the form."
    m=re.match(r"show my (.+)",value,re.I)
    if m:return f"Use /profile files to inspect the registered {m.group(1)}, or /find-name {m.group(1)} in documents."
    return None
