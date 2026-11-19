"""Tests for the app-hotkeys formula updater."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / ".github" / "scripts" / "update_app_hotkeys_formula.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "update-app-hotkeys-formula.yml"
spec = importlib.util.spec_from_file_location("update_app_hotkeys_formula", SCRIPT_PATH)
assert spec is not None
assert spec.loader is not None
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdateFormulaTests(unittest.TestCase):
    def test_bumps_url_and_sha256_only(self) -> None:
        text = updater.FORMULA_PATH.read_text(encoding="utf-8")
        updated = updater.update_formula(text, "9.8.7", "a" * 64)

        self.assertIn(
            '  url "https://github.com/basnijholt/app-hotkeys/releases/download/v9.8.7/'
            'app-hotkeys-9.8.7-macos-universal.tar.gz"',
            updated,
        )
        self.assertIn(f'  sha256 "{"a" * 64}"', updated)
        self.assertEqual(len(updated.splitlines()), len(text.splitlines()))

    def test_formula_url_matches_the_release_asset_name(self) -> None:
        text = updater.FORMULA_PATH.read_text(encoding="utf-8")
        version = text.split("/releases/download/v", 1)[1].split("/", 1)[0]

        self.assertIn(f'  url "{updater.asset_url(version)}"', text)


class ReleaseSourceTests(unittest.TestCase):
    def test_release_dispatch_payload_supplies_version(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as event_file:
            json.dump({"client_payload": {"tag_name": "v1.2.3"}}, event_file)
            event_file.flush()
            env = {"GITHUB_EVENT_NAME": "repository_dispatch", "GITHUB_EVENT_PATH": event_file.name}
            with patch.dict(os.environ, env, clear=False):
                self.assertEqual(updater.version_from_dispatch_event(), "1.2.3")

    def test_non_dispatch_event_does_not_supply_version(self) -> None:
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "schedule"}, clear=False):
            self.assertIsNone(updater.version_from_dispatch_event())

    def test_workflow_authenticates_homebrew_github_api_calls(self) -> None:
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

        self.assertIn("HOMEBREW_GITHUB_API_TOKEN: ${{ github.token }}", workflow)


if __name__ == "__main__":
    unittest.main()
