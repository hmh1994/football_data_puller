from football_data_manager.common.utils.pydantic_helper.camelcase_model import CamelCaseModel


class TheAthleticArticleAuthorResponse(CamelCaseModel):
    name: str
    url: str
    sameAs: str | None = None
