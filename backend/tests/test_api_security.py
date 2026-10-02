import os
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient

import main


client = TestClient(main.app)
ALLOWED = "http://127.0.0.1:8000"


def session_token():
    response = client.get(
        "/api/session",
        headers={"Host": "127.0.0.1:8000", "Origin": ALLOWED},
    )
    assert response.status_code == 200
    return response.json()["csrf_token"]


def protected_headers(origin=ALLOWED, host="127.0.0.1:8000"):
    return {
        "Host": host,
        "Origin": origin,
        "X-InterAI-CSRF": session_token(),
    }


def test_unallowed_origin_rejected_before_capture(monkeypatch):
    screenshot = Mock()
    clipboard = Mock()
    monkeypatch.setattr(main.hotkey_mgr, "on_screenshot", screenshot)
    monkeypatch.setattr(main.hotkey_mgr, "on_clip_save", clipboard)

    response = client.post(
        "/api/debug/trigger",
        headers={
            "Host": "127.0.0.1:8000",
            "Origin": "https://attacker.invalid",
            "X-InterAI-CSRF": session_token(),
        },
    )
    assert response.status_code == 403
    screenshot.assert_not_called()
    clipboard.assert_not_called()


def test_originless_api_request_rejected():
    response = client.get(
        "/api/cases",
        headers={"Host": "127.0.0.1:8000", "X-InterAI-CSRF": session_token()},
    )
    assert response.status_code == 403


def test_same_origin_browser_metadata_allows_originless_get():
    response = client.get(
        "/api/cases",
        headers={
            "Host": "127.0.0.1:8000",
            "Referer": ALLOWED + "/",
            "Sec-Fetch-Site": "same-origin",
            "X-InterAI-CSRF": session_token(),
        },
    )
    assert response.status_code == 200


def test_host_mismatch_rejected():
    response = client.get(
        "/api/cases",
        headers={
            "Host": "evil.invalid:8000",
            "Origin": ALLOWED,
            "X-InterAI-CSRF": session_token(),
        },
    )
    assert response.status_code == 403


def test_state_change_requires_csrf(monkeypatch):
    screenshot = Mock()
    clipboard = Mock()
    monkeypatch.setattr(main.hotkey_mgr, "on_screenshot", screenshot)
    monkeypatch.setattr(main.hotkey_mgr, "on_clip_save", clipboard)

    response = client.post(
        "/api/debug/trigger",
        headers={"Host": "127.0.0.1:8000", "Origin": ALLOWED},
    )
    assert response.status_code == 403
    screenshot.assert_not_called()
    clipboard.assert_not_called()


def test_allowed_capture_uses_mocked_devices(monkeypatch):
    screenshot = Mock()
    clipboard = Mock()
    monkeypatch.setattr(main.hotkey_mgr, "on_screenshot", screenshot)
    monkeypatch.setattr(main.hotkey_mgr, "on_clip_save", clipboard)

    response = client.post("/api/debug/trigger", headers=protected_headers())
    assert response.status_code == 200
    screenshot.assert_called_once()
    clipboard.assert_called_once()


def test_open_folder_is_case_scoped_directory_only(tmp_path, monkeypatch):
    case_root = tmp_path / "MessengerCases"
    input_dir = case_root / "case-1" / "input"
    input_dir.mkdir(parents=True)

    monkeypatch.setattr(main, "CASE_ROOT", case_root.resolve())
    startfile = Mock()
    monkeypatch.setattr(main.os, "startfile", startfile, raising=False)

    ok = client.post(
        "/api/cases/case-1/open-folder?subdir=input",
        headers=protected_headers(),
    )
    assert ok.status_code == 200
    startfile.assert_called_once_with(str(input_dir.resolve()))

    startfile.reset_mock()
    bad = client.post(
        "/api/cases/case-1/open-folder?subdir=program.exe",
        headers=protected_headers(),
    )
    assert bad.status_code == 400
    startfile.assert_not_called()


def test_old_arbitrary_path_endpoint_cannot_launch_file(tmp_path, monkeypatch):
    executable = tmp_path / "payload.exe"
    executable.write_bytes(b"MZ")
    startfile = Mock()
    monkeypatch.setattr(main.os, "startfile", startfile, raising=False)

    response = client.post(
        "/api/open_folder",
        params={"path": str(executable)},
        headers=protected_headers(),
    )
    assert response.status_code == 404
    startfile.assert_not_called()


def test_case_traversal_rejected(tmp_path, monkeypatch):
    case_root = tmp_path / "MessengerCases"
    case_root.mkdir()
    monkeypatch.setattr(main, "CASE_ROOT", case_root.resolve())

    try:
        main._validate_case_name("../outside")
    except main.HTTPException as exc:
        assert exc.status_code == 400
    else:
        raise AssertionError("path traversal was accepted")
