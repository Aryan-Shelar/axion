"""Safe architecture for Windows UI Automation beta."""
class WindowsAutofill:
    def detect(self): return "Windows App Autofill Beta: reliable UI Automation is unavailable with current dependencies; no fields were accessed."
    def preview(self): return self.detect()
    def fill(self,confirm=False):
        if not confirm:return "Preview required. No fields were filled. Re-run /appfill fill --confirm."
        return self.detect()
