"""This allows to have individual entries for imported leaderboards

WARNING: will override entries do not use with non-imported leaderboards.
"""

import json
import sys
from pathlib import Path

import clypi

from .utils import LeaderboardNames, build_readme, get_leaderboard_type


class SplitIndex(clypi.Command):
    """Split index into entries (Not that needed)."""

    name: clypi.Positional[LeaderboardNames]
    data_dir: Path = Path.cwd() / "leaderboards"

    def split_index(self, name: LeaderboardNames) -> None:
        """Split the index into individual entries."""
        ld_type = get_leaderboard_type(name)
        index_file = self.data_dir / name.value / "index.json"

        if not index_file.is_file():
            print(f"Cannot find index for {name}", file=sys.stderr)
            sys.exit(1)

        with index_file.open() as fh:
            leaderboard = ld_type.model_validate(json.load(fh))

        for entry in leaderboard.data:
            entry_dir = (
                index_file.parent / f"{entry.index}_{entry.publication.author_short}"
            )
            entry_dir.mkdir(exist_ok=True, parents=True)
            with (entry_dir / "entry.json").open("w") as fh:
                json.dump(entry.model_dump(mode="json"), fh, indent=4)

            # Add a readme to the entry
            (entry_dir / "README.md").write_text(build_readme(name=name, entry=entry))
        print(f"Succesfully created entries for {name.value} in {index_file.parent}")

    async def run(self) -> None:
        if self.name == "all":
            for name in LeaderboardNames:
                self.split_index(name)
        else:
            self.split_index(self.name)


def run() -> None:
    cmd = SplitIndex.parse()
    cmd.start()


if __name__ == "__main__":
    run()
