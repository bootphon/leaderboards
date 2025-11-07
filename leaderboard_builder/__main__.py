from .cmd import LeaderboardManager


def run() -> None:
    """Run Command"""
    cmd = LeaderboardManager.parse()
    cmd.start()


if __name__ == "__main__":
    run()
