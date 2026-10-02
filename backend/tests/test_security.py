import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

import main


class LocalApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.case_dir = self.root / "20261002_120000_auto"
        (self.case_dir / "input").mkdir(parents=True)
        (self.case_dir / "output").mkdir()
        (self.case_dir / "handoff").mkdir()
        (self.case_dir / "input" / "clip.txt").write_text("clip", encoding="utf-8")
        (self.case_dir / "input" / "page.png").write_bytes(b"not-a-real-image")
        (self.case_dir / "input" / "payload.exe").write_bytes(b"MZ")

        self.old_case_root = main.CASE_ROOT
        self.old_manager_root = main.case_manager.root_dir
        main.CASE_ROOT = self.root
        main.case_manager.root_dir = str(self.root)

        self.listener = patch.object(main.hotkey_mgr, "start_listener")
        self.listener.start()
        self.client_ctx = TestClient(
            main.app,
            base_url="http://127.0.0.1:8000",
        )
        self.client = self.client_ctx.__enter__()
        self.good_headers = {
            "Origin": "http://127.0.0.1:8000",
            "X-InterAI-CSRF": main.CSRF_TOKEN,
        }

    def tearDown(self):
        self.client_ctx.__exit__(None, None, None)
        self.listener.stop()
        main.CASE_ROOT = self.old_case_root
        main.case_manager.root_dir = self.old_manager_root
        self.tmp.cleanup()

    def test_untrusted_origin_is_rejected_without_side_effects(self):
        with patch.object(main.hotkey_mgr, "on_screenshot") as screenshot,              patch.object(main.hotkey_mgr, "on_clip_save") as clip:
            response = self.client.post(
                "/api/debug/trigger",
                headers={
                    "Origin": "https://example.invalid",
                    "X-InterAI-CSRF": main.CSRF_TOKEN,
                },
            )
        self.assertEqual(response.status_code, 403)
        screenshot.assert_not_called()
        clip.assert_not_called()

    def test_originless_sensitive_request_is_rejected(self):
        response = self.client.get(
            "/api/cases",
            headers={"X-InterAI-CSRF": main.CSRF_TOKEN},
        )
        self.assertEqual(response.status_code, 403)

    def test_host_mismatch_is_rejected(self):
        response = self.client.get(
            "/api/session",
            headers={"Host": "evil.invalid:8000"},
        )
        self.assertEqual(response.status_code, 403)

    def test_valid_local_trigger_calls_only_mocked_capture_actions(self):
        with patch.object(main.hotkey_mgr, "on_screenshot") as screenshot,              patch.object(main.hotkey_mgr, "on_clip_save") as clip:
            response = self.client.post("/api/debug/trigger", headers=self.good_headers)
        self.assertEqual(response.status_code, 200)
        screenshot.assert_called_once_with()
        clip.assert_called_once_with()

    def test_open_folder_accepts_only_real_allowed_case_directories(self):
        case_name = self.case_dir.name
        with patch.object(main.os, "startfile", create=True) as startfile:
            ok = self.client.post(
                f"/api/cases/{case_name}/open-folder?subdir=input",
                headers=self.good_headers,
            )
            bad_file = self.client.post(
                f"/api/cases/{case_name}/open-folder?subdir=input/payload.exe",
                headers=self.good_headers,
            )
            traversal = self.client.post(
                f"/api/cases/{case_name}/open-folder?subdir=..",
                headers=self.good_headers,
            )

        self.assertEqual(ok.status_code, 200)
        startfile.assert_called_once_with(str((self.case_dir / "input").resolve()))
        self.assertEqual(bad_file.status_code, 400)
        self.assertEqual(traversal.status_code, 400)

    def test_absolute_and_executable_paths_are_not_an_api_surface(self):
        # The endpoint no longer accepts an arbitrary path parameter at all.
        with patch.object(main.os, "startfile", create=True) as startfile:
            response = self.client.post(
                f"/api/cases/{self.case_dir.name}/open-folder"
                "?subdir=C:%5CWindows%5CSystem32%5Ccmd.exe",
                headers=self.good_headers,
            )
        self.assertEqual(response.status_code, 400)
        startfile.assert_not_called()


if __name__ == "__main__":
    unittest.main()
