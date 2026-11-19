class AppHotkeys < Formula
  desc "Global hotkeys that bring an app to the front, read from a plain text file"
  homepage "https://github.com/basnijholt/app-hotkeys"
  url "https://github.com/basnijholt/app-hotkeys/releases/download/v0.1.0/app-hotkeys-0.1.0-macos-universal.tar.gz"
  sha256 "4a53673682cf7d2199b77e2367da26c12d7e9beb4de008824e88fab3011de240"
  license "MIT"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on :macos

  def install
    bin.install "app-hotkeys"
    pkgshare.install "hotkeys.conf"
  end

  def caveats
    <<~EOS
      Put your hotkeys in ~/.config/app-hotkeys/hotkeys.conf, one per line:
        ctrl+alt+shift+s = com.apple.Safari
      An example is at #{opt_pkgshare}/hotkeys.conf.
      Edits apply when you save; check the file with:
        app-hotkeys --check

      If another app already holds the same key combination, both fire.
      Turn off the other app's binding first.
    EOS
  end

  service do
    run [opt_bin/"app-hotkeys"]
    keep_alive true
    process_type :interactive
    log_path var/"log/app-hotkeys.log"
    error_log_path var/"log/app-hotkeys.log"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/app-hotkeys --version")

    (testpath/"hotkeys.conf").write "ctrl+alt+shift+s = com.apple.Safari\n"
    assert_match "line 1: ctrl+alt+shift+s = com.apple.Safari",
                 shell_output("#{bin}/app-hotkeys --check #{testpath}/hotkeys.conf")

    (testpath/"broken.conf").write "ctrl+bogus+s = com.apple.Safari\n"
    assert_match "line 1: unknown modifier 'bogus'",
                 shell_output("#{bin}/app-hotkeys --check #{testpath}/broken.conf 2>&1", 1)
  end
end
