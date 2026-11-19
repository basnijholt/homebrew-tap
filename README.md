# homebrew-tap

Homebrew tap for [Agent CLI](https://github.com/basnijholt/agent-cli) and [macos-hotkey-app-switcher](https://github.com/basnijholt/macos-hotkey-app-switcher).

## Install

| Package | Install |
|---|---|
| [Agent CLI](https://github.com/basnijholt/agent-cli): local-first AI voice and text tools with menu bar integration | `brew install --cask basnijholt/tap/agent-cli` |
| [macos-hotkey-app-switcher](https://github.com/basnijholt/macos-hotkey-app-switcher): global hotkeys that bring an app to the front | `brew install basnijholt/tap/macos-hotkey-app-switcher` |

Run macos-hotkey-app-switcher in the background with `brew services start macos-hotkey-app-switcher`. It was called `app-hotkeys` before 0.2.0; `formula_renames.json` migrates old installs on `brew update`.

## Updates

Scheduled workflows keep both in sync with the latest GitHub releases (`.github/workflows/`). Run one by hand with `gh workflow run`.
