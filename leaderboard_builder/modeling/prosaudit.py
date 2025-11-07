import pydantic

from ._core import Leaderboard, LeaderboardEntry, LeaderboardScores


class ProsAuditScoreEntity(pydantic.BaseModel):
    score: float
    n: int
    std: float


class ProsAuditEntryScores(LeaderboardScores):
    protosyntax: dict[str, ProsAuditScoreEntity]
    lexical: dict[str, ProsAuditScoreEntity]


class ProsAuditLeaderboardEntry(LeaderboardEntry):
    scores: ProsAuditEntryScores


class ProsAuditLeaderboard(Leaderboard):
    data: list[ProsAuditLeaderboardEntry]
