# homebrew-tap

Homebrew tap for [Agent CLI](https://github.com/basnijholt/agent-cli) and [app-hotkeys](https://github.com/basnijholt/app-hotkeys).

## Install

| Package | Install |
|---|---|
| [Agent CLI](https://github.com/basnijholt/agent-cli): local-first AI voice and text tools with menu bar integration | `brew install --cask basnijholt/tap/agent-cli` |
| [app-hotkeys](https://github.com/basnijholt/app-hotkeys): global hotkeys that bring an app to the front | `brew install basnijholt/tap/app-hotkeys` |

Run app-hotkeys in the background with `brew services start app-hotkeys`.

## Updates

Scheduled workflows keep both in sync with the latest GitHub releases (`.github/workflows/`). Run one by hand with `gh workflow run`.
