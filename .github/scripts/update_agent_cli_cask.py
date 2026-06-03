#!/usr/bin/env python3
"""Update the Agent CLI cask from the latest GitHub release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

REPO = "basnijholt/agent-cli"
ASSET_NAME = "AgentCLI.dmg"
ROOT = Path(__file__).resolve().parents[2]
CASK_PATH = ROOT / "Casks" / "agent-cli.rb"


def api_json(url: str) -> dict[str, object]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def latest_release() -> tuple[str, str]:
    release = api_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    tag_name = str(release["tag_name"])
    version = normalize_version(tag_name)
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        raise RuntimeError("Latest release has no assets list")

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        if asset.get("name") == ASSET_NAME:
            return version, str(asset["browser_download_url"])

    raise RuntimeError(f"Latest release {tag_name} has no {ASSET_NAME} asset")


def normalize_version(value: str) -> str:
    return value[1:] if value.startswith("v") else value


def release_from_dispatch_event() -> tuple[str, str] | None:
    if os.environ.get("GITHUB_EVENT_NAME") != "repository_dispatch":
        return None

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError("GITHUB_EVENT_PATH is required for repository_dispatch")

    with Path(event_path).open(encoding="utf-8") as event_file:
        event = json.load(event_file)

    payload = event.get("client_payload")
    if not isinstance(payload, dict):
        raise RuntimeError("repository_dispatch payload must include client_payload")

    tag_name = payload.get("tag_name")
    asset_url = payload.get("asset_url")
    if not isinstance(tag_name, str) or not tag_name:
        raise RuntimeError("repository_dispatch payload must include tag_name")
    if not isinstance(asset_url, str) or not asset_url:
        raise RuntimeError("repository_dispatch payload must include asset_url")

    return normalize_version(tag_name), asset_url


def download_sha256(url: str) -> str:
    request = Request(url, headers={"User-Agent": "homebrew-tap-cask-updater"})
    digest = hashlib.sha256()
    with tempfile.NamedTemporaryFile() as tmp_file:
        with urlopen(request, timeout=300) as response:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                tmp_file.write(chunk)
    return digest.hexdigest()


def replace_single(pattern: str, replacement: str, text: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected exactly one match for {pattern!r}, found {count}")
    return updated


def update_cask(version: str, sha256: str) -> bool:
    text = CASK_PATH.read_text(encoding="utf-8")
    updated = replace_single(r'^  version "[^"]+"$', f'  version "{version}"', text)
    updated = replace_single(r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{sha256}"', updated)

    if updated == text:
        print(f"agent-cli cask already up to date at {version}")
        return False

    CASK_PATH.write_text(updated, encoding="utf-8")
    print(f"updated agent-cli cask to {version}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="Release version without leading v")
    parser.add_argument("--asset-url", help=f"Download URL for {ASSET_NAME}")
    args = parser.parse_args()

    dispatch_release = release_from_dispatch_event()
    if args.version or args.asset_url:
        if not args.version or not args.asset_url:
            parser.error("--version and --asset-url must be passed together")
        version = normalize_version(args.version)
        asset_url = args.asset_url
    elif dispatch_release:
        version, asset_url = dispatch_release
    else:
        version, asset_url = latest_release()

    sha256 = download_sha256(asset_url)
    update_cask(version, sha256)
    return 0


if __name__ == "__main__":
    sys.exit(main())
