from pydantic import BaseModel


class NewsTranslateObjectResponse(BaseModel):
    en: str
    ko: str
