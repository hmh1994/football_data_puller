from pydantic import BaseModel


class NewsTranslateSummaryResponse(BaseModel):
    summary: int
    en: list[str]
    ko: list[str]
    teams: list[str] = []
