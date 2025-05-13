from pydantic import BaseModel

from football_data_manager.puller.services.the_athletic.models.responses.news_translate_object_response import (
    NewsTranslateObjectResponse,
)
from football_data_manager.puller.services.the_athletic.models.responses.news_translate_summary_response import (
    NewsTranslateSummaryResponse,
)


class NewsTranslateResponse(BaseModel):
    article: int
    authors: list[NewsTranslateObjectResponse]
    title: NewsTranslateObjectResponse
    summaries: list[NewsTranslateSummaryResponse]
