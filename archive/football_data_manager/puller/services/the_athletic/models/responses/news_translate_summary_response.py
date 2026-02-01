from pydantic import BaseModel


class NewsTranslateSummaryResponse(BaseModel):
    en: list[str]
    ko: list[str]
