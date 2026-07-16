import json, tempfile, unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from axion.tools.smart_file_finder import SmartFileFinder, match_filename, safe_destination
from axion.profile.profile_vault import ProfileVault, mask_value
from axion.autofill.field_mapper import document_label, is_prohibited, map_field
from axion.autofill.autofill_bridge import AutofillBridge

class FakeCrypto:
    available=True
    def protect(self,v):return "enc:"+v[::-1]
    def unprotect(self,v):return v[4:][::-1]

class SmartFinderTests(unittest.TestCase):
    def test_matching_modes(self):
        self.assertEqual(match_filename("resume","resume.pdf")[1],"exact")
        self.assertEqual(match_filename("sum","resume.pdf")[1],"contains")
        self.assertEqual(match_filename("aryan resume","Resume Aryan Final.pdf")[1],"all-word/token")
        self.assertEqual(match_filename("aryan resme","Aryan Resume.pdf")[1],"fuzzy")
    def test_persistence_and_safe_name_and_preview(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"resume.pdf").write_text("x"); state=root/"state.json"
            finder=SmartFileFinder(state,root)
            self.assertEqual(len(finder.search("resume",str(root))),1); self.assertEqual(len(finder.latest()),1)
            self.assertEqual(safe_destination(root,"resume.pdf").name,"resume_1.pdf")
            result=finder.bulk("resume",str(root),"move",str(root/"missing")); self.assertIn("No files were moved",result); self.assertTrue((root/"resume.pdf").exists())
    def test_confirmed_move(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); dest=root/"dest";dest.mkdir();(root/"old resume.txt").write_text("x")
            result=SmartFileFinder(root/"state.json",root).bulk("old resume",str(root),"move",str(dest),confirm=True)
            self.assertIn("Confirmed move",result);self.assertTrue((dest/"old resume.txt").exists())

class ProfileTests(unittest.TestCase):
    def test_validation_masking_and_encryption(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"vault.json"; vault=ProfileVault(path,FakeCrypto());vault.set("phone","9876543210")
            self.assertEqual(vault.get("phone"),"9876543210");self.assertNotIn("9876543210",path.read_text());self.assertEqual(mask_value("phone","9876543210"),"******3210")
            with self.assertRaises(ValueError):vault.set("email","bad")

class AutofillTests(unittest.TestCase):
    def test_mapping_prohibited_and_documents(self):
        self.assertEqual(map_field({"label":"GitHub profile"})["profile_field"],"github")
        self.assertTrue(is_prohibited({"name":"otp_code"}));self.assertEqual(document_label("Upload your CV"),"resume")
    def test_settings_approval_and_localhost(self):
        with tempfile.TemporaryDirectory() as td:
            bridge=AutofillBridge(settings_path=Path(td)/"settings.json",port=0);self.assertEqual(bridge.host,"127.0.0.1")
            bridge.update_site("example.com",True);self.assertTrue(bridge.site_allowed("example.com"));bridge.update_site("example.com",False);self.assertFalse(bridge.site_allowed("example.com"))
            bridge.approve_sensitive();self.assertTrue(bridge.consume_sensitive());self.assertFalse(bridge.consume_sensitive())
    def test_invalid_token_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            bridge=AutofillBridge(settings_path=Path(td)/"s.json",port=0);bridge.start()
            try:
                req=Request(f"http://127.0.0.1:{bridge.port}/v1/fields",data=b'{"domain":"example.com","fields":[]}',headers={"Content-Type":"application/json","X-Axion-Token":"wrong"},method="POST")
                with self.assertRaises(HTTPError) as caught:urlopen(req,timeout=2)
                self.assertEqual(caught.exception.code,403)
            finally:bridge.stop()

if __name__=="__main__":unittest.main()
