"""Tests for the Agent CLI cask updater."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_PATH = Path(__file__).parents[1] / ".github" / "scripts" / "update_agent_cli_cask.py"
spec = importlib.util.spec_from_file_location("update_agent_cli_cask", SCRIPT_PATH)
assert spec is not None
assert spec.loader is not None
update_agent_cli_cask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_agent_cli_cask)


class ReleaseSourceTests(unittest.TestCase):
    def test_release_dispatch_payload_supplies_version_and_asset_url(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8") as event_file:
            json.dump(
                {
                    "client_payload": {
                        "tag_name": "v1.2.3",
                        "asset_url": "https://example.com/AgentCLI.dmg",
                    }
                },
                event_file,
            )
            event_file.flush()

            with patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_NAME": "repository_dispatch",
                    "GITHUB_EVENT_PATH": event_file.name,
                },
                clear=False,
            ):
                self.assertEqual(
                    update_agent_cli_cask.release_from_dispatch_event(),
                    ("1.2.3", "https://example.com/AgentCLI.dmg"),
                )

    def test_non_dispatch_event_does_not_supply_release(self) -> None:
        with patch.dict(os.environ, {"GITHUB_EVENT_NAME": "workflow_dispatch"}, clear=False):
            self.assertIsNone(update_agent_cli_cask.release_from_dispatch_event())


if __name__ == "__main__":
    unittest.main()
