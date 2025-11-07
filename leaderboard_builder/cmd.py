import typing as t
from pathlib import Path

import clypi

from .utils import LeaderboardNames, get_preview, load_data, load_template


class MakeHtml(clypi.Command):
    """Build html from template."""

    name: LeaderboardNames | t.Literal["all"] = clypi.arg(inherited=True)
    source_dir: Path = clypi.arg(inherited=True)
    target_dir: Path = clypi.arg(inherited=True)
    force_update: bool = clypi.arg(inherited=True)

    def build(self, name: LeaderboardNames) -> None:
        """Build Table from HTML template."""
        snippet_tmpl = load_template(name)
        preview_tmpl = get_preview()
        ld_data = load_data(
            name=self.name,
            data_dir=self.source_dir,
            force_update=self.force_update,
        )
        tableHTML = snippet_tmpl.render(leaderboard=ld_data, tableID=f"{name.value}")

        (self.target_dir / "snippets").mkdir(exist_ok=True, parents=True)
        (self.target_dir / "snippets" / f"{name.value}.html").write_text(tableHTML)

        # Make preview
        (self.target_dir / "preview").mkdir(exist_ok=True, parents=True)
        (self.target_dir / "preview" / f"{name.value}.html").write_text(
            preview_tmpl.render(name=self.name.value.capitalize(), tableHTML=tableHTML)
        )

        print(
            f"Succesfully wrote {self.target_dir}/{{preview | snippet}}/{name.value}.html"
        )

    async def run(self) -> None:
        if self.name == "all":
            for name in LeaderboardNames:
                self.build(name)
        else:
            self.build(self.name)


class CheckEntries(clypi.Command):
    """Check Entries."""


class LeaderboardManager(clypi.Command):
    """Command line tool for managing leaderboards."""

    subcommand: MakeHtml | CheckEntries
    name: LeaderboardNames | t.Literal["all"] = clypi.arg(
        short="n", help="Name of the leaderboard"
    )
    force_update: bool = clypi.arg(
        default=False, help="Force update of index file from entries."
    )
    source_dir: Path = clypi.arg(default=Path.cwd() / "leaderboards", short="d")
    target_dir: Path = clypi.arg(default=Path.cwd() / "static", short="t")
