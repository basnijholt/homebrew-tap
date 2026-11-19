#!/usr/bin/env python3
"""Update the app-hotkeys formula from the latest GitHub release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "basnijholt/app-hotkeys"
ROOT = Path(__file__).resolve().parents[2]
FORMULA_PATH = ROOT / "Formula" / "app-hotkeys.rb"


def asset_name(version: str) -> str:
    return f"app-hotkeys-{version}-macos-universal.tar.gz"


def asset_url(version: str) -> str:
    return f"https://github.com/{REPO}/releases/download/v{version}/{asset_name(version)}"


def normalize_version(value: str) -> str:
    return value[1:] if value.startswith("v") else value


def api_json(url: str) -> dict[str, object]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def latest_version() -> str:
    release = api_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    version = normalize_version(str(release["tag_name"]))
    names = {asset.get("name") for asset in release.get("assets", []) if isinstance(asset, dict)}
    if asset_name(version) not in names:
        raise RuntimeError(f"Latest release v{version} has no {asset_name(version)} asset")
    return version


def version_from_dispatch_event() -> str | None:
    if os.environ.get("GITHUB_EVENT_NAME") != "repository_dispatch":
        return None
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    tag_name = (event.get("client_payload") or {}).get("tag_name")
    if not isinstance(tag_name, str) or not tag_name:
        raise RuntimeError("repository_dispatch payload must include client_payload.tag_name")
    return normalize_version(tag_name)


def download_sha256(url: str) -> str:
    digest = hashlib.sha256()
    with urlopen(Request(url, headers={"User-Agent": "homebrew-tap-formula-updater"}), timeout=300) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def replace_single(pattern: str, replacement: str, text: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match for {pattern!r}, found {count}")
    return updated


def update_formula(text: str, version: str, sha256: str) -> str:
    updated = replace_single(r'^  url "[^"]+"$', f'  url "{asset_url(version)}"', text)
    return replace_single(r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{sha256}"', updated)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="Release version (default: the latest release)")
    args = parser.parse_args()

    if args.version:
        version = normalize_version(args.version)
    else:
        version = version_from_dispatch_event() or latest_version()

    text = FORMULA_PATH.read_text(encoding="utf-8")
    if f'  url "{asset_url(version)}"' in text:
        print(f"app-hotkeys formula already up to date at {version}")
        return 0

    FORMULA_PATH.write_text(update_formula(text, version, download_sha256(asset_url(version))), encoding="utf-8")
    print(f"updated app-hotkeys formula to {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
