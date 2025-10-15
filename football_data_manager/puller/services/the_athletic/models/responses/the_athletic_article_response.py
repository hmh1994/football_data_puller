from football_data_manager.common.utils.pydantic_helper.camelcase_model import CamelCaseModel
from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_article_author_response import \
    TheAthleticArticleAuthorResponse


class TheAthleticArticleResponse(CamelCaseModel):
    author: list[TheAthleticArticleAuthorResponse]
    dateCreated: str
    datePublished: str
    dateModified: str
    articleBody: str | None = None
    description: str
    headline: str
    thumbnailUrl: str
