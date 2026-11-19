class MacosHotkeyAppSwitcher < Formula
  desc "Global hotkeys that bring an app to the front, read from a plain text file"
  homepage "https://github.com/basnijholt/macos-hotkey-app-switcher"
  url "https://github.com/basnijholt/macos-hotkey-app-switcher/releases/download/v0.2.0/macos-hotkey-app-switcher-0.2.0-macos-universal.tar.gz"
  sha256 "91f6ec3b91acc1145201618f8cc0567cdac539011523ff4fd050c54f1e6b0914"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on :macos

  def install
    bin.install "macos-hotkey-app-switcher"
    pkgshare.install "hotkeys.conf"
  end

  def caveats
    <<~EOS
      Put your hotkeys in ~/.config/macos-hotkey-app-switcher/hotkeys.conf, one per line:
        ctrl+alt+shift+s = com.apple.Safari
      An example is at #{opt_pkgshare}/hotkeys.conf.
      Edits apply when you save; check the file with:
        macos-hotkey-app-switcher --check

      If another app already holds the same key combination, both fire.
      Turn off the other app's binding first.

      Upgrading from app-hotkeys? Move ~/.config/app-hotkeys/hotkeys.conf
      to the new path above and run: brew services restart macos-hotkey-app-switcher
    EOS
  end

  service do
    run [opt_bin/"macos-hotkey-app-switcher"]
    keep_alive true
    process_type :interactive
    log_path var/"log/macos-hotkey-app-switcher.log"
    error_log_path var/"log/macos-hotkey-app-switcher.log"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/macos-hotkey-app-switcher --version")

    (testpath/"hotkeys.conf").write "ctrl+alt+shift+s = com.apple.Safari\n"
    assert_match "line 1: ctrl+alt+shift+s = com.apple.Safari",
                 shell_output("#{bin}/macos-hotkey-app-switcher --check #{testpath}/hotkeys.conf")

    (testpath/"broken.conf").write "ctrl+bogus+s = com.apple.Safari\n"
    assert_match "line 1: unknown modifier 'bogus'",
                 shell_output("#{bin}/macos-hotkey-app-switcher --check #{testpath}/broken.conf 2>&1", 1)
  end
end
