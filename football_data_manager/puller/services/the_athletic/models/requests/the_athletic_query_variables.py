from pydantic import BaseModel


class TheAthleticQueryVariables(BaseModel):
    feed: str = "league"
    feed_id: int
    is_mobile_web: bool = False
    locale: str = "en-gb"
    show_long_titles: bool = False
    page: int = 0
    retrieveMeta: bool = False
