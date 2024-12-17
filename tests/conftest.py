import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    pass


def pytest_configure(config: pytest.Config) -> None:
    pass


def pytest_collection_modifyitems(
        config: pytest.Config, items: list[pytest.Item]
) -> None:
    pass
