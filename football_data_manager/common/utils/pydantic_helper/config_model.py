from pydantic import BaseModel

from football_data_manager.common.utils.type_helper.dict_helper import lower_keys


class ConfigModel(BaseModel):
    """
    Base model to store configuration.
    """

    def __init__(self, **data):
        super().__init__(**lower_keys(data))
