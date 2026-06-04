cask "agent-cli" do
  version "0.98.4"
  sha256 "391aa2f5fd5ebf6795ff7719a8c223b30a1b5b2a6cbf49b784a3a339dd1352c6"

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
