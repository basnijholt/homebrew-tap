# Jackielii Tap

My personal homebrew taps, mainly for Linux

- [x] rofi
- [ ] dunst
- [x] skhd-zig (macos koekeishiya/skhd fork)

## How do I install these formulae?

`brew install jackielii/tap/<formula>`

Or `brew tap jackielii/tap` and then `brew install <formula>`.

### skhd-zig is a cask, not a formula

The release artifact is a self-contained `skhd.app`, so `skhd-zig` lives
under `Casks/`, not `Formula/`. On the CLI, `brew install jackielii/tap/skhd-zig`
auto-falls-back to the cask and Just Works.

In a **Brewfile** (or **nix-darwin**'s `homebrew` module) the fallback
does not apply — `brew "..."` is taken literally and resolves only
against formulae. Use `cask`:

```ruby
tap  "jackielii/tap"
cask "jackielii/tap/skhd-zig"   # not: brew "jackielii/tap/skhd-zig"
```

## Documentation

`brew help`, `man brew` or check [Homebrew's documentation](https://docs.brew.sh).
