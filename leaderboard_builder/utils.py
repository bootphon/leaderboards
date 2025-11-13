import enum
import json
import typing as t
import warnings
from importlib.resources import files
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from .modeling import Leaderboard, LeaderboardEntry


class LeaderboardNames(str, enum.Enum):
    """Enumeration of leaderboard names"""

    zrc_prosaudit = "zrc_prosaudit"


def get_template_dir() -> Path:
    """Find where templates are stored."""
    try:
        template_dir = Path(files("leaderboard-builder")) / "templates"
        if template_dir.exists():
            return template_dir
    except (ModuleNotFoundError, TypeError, FileNotFoundError):
        pass

    current_file = Path(__file__).resolve()
    template_dir = current_file.parent / "templates"
    if template_dir.exists():
        return template_dir
    raise FileNotFoundError("Could not locate templates directory")


def get_preview() -> Template:
    """Load preview template"""
    return Environment(loader=FileSystemLoader(get_template_dir())).get_template(
        "preview.html.jinja2"
    )


def load_table_template(name: LeaderboardNames) -> Template:
    """Load jinja2 html template."""
    return Environment(loader=FileSystemLoader(get_template_dir())).get_template(
        f"{name.value}.html.jinja2"
    )


def load_javascript_template(name: LeaderboardNames) -> Template:
    """Load javascript file for a given leaderboard."""
    tmpl_env = Environment(loader=FileSystemLoader(get_template_dir()))
    try:
        return tmpl_env.get_template(f"{name.value}.js.jinja2")
    except TemplateNotFound:
        # If no override return base
        return tmpl_env.get_template("base.leaderboard.js.jinja2")


def get_leaderboard_type(name: LeaderboardNames) -> t.Type[Leaderboard]:
    """Match leaderboard name with its corresponding schema."""
    match name:
        case LeaderboardNames.zrc_prosaudit:
            from .modeling.prosaudit import ProsAuditLeaderboard

            return ProsAuditLeaderboard
        case _:
            raise ValueError(f"Could not find leaderboard schema for {name.value}")


def build_index(
    ld_type: t.Type[Leaderboard],
    entries_locations: list[Path],
    index_file: Path,
) -> None:
    """Build index from entries."""
    entries_obj = []
    for entry_dir in entries_locations:
        entry_file = entry_dir / "entry.json"
        if not entry_file.is_file():
            warnings.warn(f"Empty entry found {entry_dir} !!", stacklevel=2)
            continue
        with entry_file.open() as fh:
            entries_obj.append(json.load(fh))

    ld = ld_type.model_validate({"data": entries_obj})
    with index_file.open("w") as fh:
        json.dump(ld.model_dump(mode="json"), fh, indent=4)


def build_readme(name: LeaderboardNames, entry: LeaderboardEntry) -> str:
    """Get a basic readme from entry."""
    return (
        Environment(loader=FileSystemLoader(get_template_dir()))
        .get_template("readme.md.jinja2")
        .render(leaderboad_name=name.value, entry=entry)
    )


def load_data(
    name: LeaderboardNames, data_dir: Path, *, force_update: bool = False
) -> Leaderboard:
    """Load leaderboard model from data directory"""
    location = data_dir / name.value

    if not location.is_dir():
        raise ValueError(f"Could not find data for leaderboard {name.value}")

    index_file = location / "index.json"
    ld_type = get_leaderboard_type(name)

    if not index_file.is_file() or force_update:
        ld_entries = sorted(
            [ent for ent in location.iterdir() if ent.is_dir()], key=lambda x: x.name
        )
        build_index(lb_type=ld_type, entries=ld_entries, index_file=index_file)

    with index_file.open() as fh:
        return ld_type.model_validate(json.load(fh))
