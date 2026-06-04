cask "agent-cli" do
  version "0.97.0"
  sha256 "a8c8c63682f17c6e94271c9210c66601eb8329df407418da150b84adb86e220e"

  url "https://github.com/basnijholt/agent-cli/releases/download/v#{version}/AgentCLI.dmg"
  name "Agent CLI"
  desc "Local-first AI voice and text tools with menu bar integration"
  homepage "https://github.com/basnijholt/agent-cli"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on arch: :arm64
  depends_on macos: :ventura

  app "AgentCLI.app"

  uninstall launchctl: "com.agent_cli.whisper",
            quit:      "lt.nijho.agent-cli.menubar"

  zap trash: [
    "~/Library/Application Support/AgentCLI",
    "~/Library/LaunchAgents/com.agent_cli.whisper.plist",
    "~/Library/Logs/agent-cli-whisper",
    "~/Library/Preferences/lt.nijho.agent-cli.menubar.plist",
  ]
end
