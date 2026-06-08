cask "skhd-zig" do
  # `#{arch}` resolves to arm64 / x86_64 — matches the release tarball names.
  arch arm: "arm64", intel: "x86_64"

  version "0.1.8"
  sha256 arm:   "d5cafd686be823e456e491e5e922db11b4d7659ffe647b4df6a18a517cfd773d",
         intel: "18953af3fb39c7ea3480343fe16df01d0f810e704896bd77c933894a3ef90a25"

  url "https://github.com/jackielii/skhd.zig/releases/download/v#{version}/skhd-#{arch}-macos.tar.gz"
  name "skhd.zig"
  desc "Simple hotkey daemon written in Zig"
  homepage "https://github.com/jackielii/skhd.zig"

  # Intel builds are cross-compiled from the arm64 runner (see release.yml).
  depends_on macos: :big_sur

  app "skhd.app"
  # The CLI lives inside the bundle; surface it on PATH so `skhd ...` works
  # regardless of the cask token. Replaces the old formula's bin symlink.
  binary "#{appdir}/skhd.app/Contents/MacOS/skhd"

  # No Apple Developer ID / notarization: the bundle is self-signed, so a
  # cask-downloaded copy carries com.apple.quarantine and Gatekeeper would
  # block it. Strip the quarantine so launchd can run it. TCC grants
  # (Accessibility / Input Monitoring) remain manual one-time grants keyed
  # to the self-signed cert — same as the previous formula install.
  postflight do
    # Self-signed bundle + cask quarantine = Gatekeeper block. Strip so
    # launchd can run it. TCC grants stay manual one-time.
    system_command "/usr/bin/xattr",
                   args: ["-dr", "com.apple.quarantine", "#{appdir}/skhd.app"]

    # Restart the agent so install/upgrade picks up the new binary (ported
    # from the old formula's post_install). Best-effort — on a fresh
    # install before `skhd --start-service` has ever run there is no service
    # to restart; don't abort the install over it.
    system_command "#{appdir}/skhd.app/Contents/MacOS/skhd",
                   args:         ["--restart-service"],
                   must_succeed: false
  end

  # Stop the user LaunchAgent on uninstall. The root skhd-grabber
  # LaunchDaemon needs sudo to remove, so that stays a documented manual
  # step (see caveats) rather than an uninstall directive.
  uninstall launchctl: "com.jackielii.skhd",
            quit:      "com.jackielii.skhd"

  zap trash: "~/Library/Logs/skhd.log"

  caveats <<~EOS
    Configuration:
      touch ~/.config/skhd/skhdrc

    Syntax reference:
      https://github.com/jackielii/skhd.zig/blob/main/SYNTAX.md

    Setup (idempotent — safe to re-run anytime):
      skhd --start-service
      # Registers the LaunchAgent and prompts for Accessibility + Input
      # Monitoring on first launch. If your config has .remap / .taphold /
      # fn_layer rules, also prompts (sudo) to install skhd-grabber and the
      # Karabiner-DriverKit-VirtualHIDDevice .pkg.
      skhd --status   # verify

    Logs:
      ~/Library/Logs/skhd.log    (agent)
      /var/log/skhd-grabber.log  (grabber, if installed)

    Full teardown of the root grabber (cask uninstall can't sudo):
      sudo skhd --uninstall-grabber

    Migrating from the old formula (one-time):
      brew uninstall skhd-zig      # removes the formula
      brew install skhd-zig        # reinstalls as this cask
  EOS
end
