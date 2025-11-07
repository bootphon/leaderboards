from datetime import datetime

import pydantic


class EntryDetails(pydantic.BaseModel):
    train_set: str | None
    gpu_budget: str | None
    parameters: dict = pydantic.Field(default_factory=dict)


class PublicationEntry(pydantic.BaseModel):
    author_short: str | None
    authors: str | None
    paper_title: str | None
    paper_ref: str | None
    bib_ref: str | None
    paper_url: pydantic.AnyHttpUrl | str | None
    pub_year: int | None
    team_name: str | None
    institution: str
    code: pydantic.AnyHttpUrl | None
    DOI: str | None
    open_science: bool = False


class LeaderboardScores(pydantic.BaseModel):
    pass


class LeaderboardExtras(pydantic.BaseModel):
    pass


class LeaderboardEntry(pydantic.BaseModel):
    model_id: str | None
    submission_id: str = ""
    index: int | None
    submission_date: datetime | None
    submitted_by: str | None
    description: str
    publication: PublicationEntry
    details: EntryDetails
    scores: LeaderboardScores
    extras: LeaderboardExtras | None


class Leaderboard(pydantic.BaseModel):
    last_modified: datetime = pydantic.Field(default_factory=lambda: datetime.now())
    data: list[LeaderboardEntry]

    def sort_by(self, key: str):
        """Sort entries of leaderboard by a specific key"""
        self.data.sort(key=lambda x: getattr(x, key))
