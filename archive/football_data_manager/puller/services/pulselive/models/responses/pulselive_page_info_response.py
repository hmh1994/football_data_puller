from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulselivePageInfoResponse(CamelCaseModel):
    page: int
    num_pages: int
    page_size: int
    num_entries: int
