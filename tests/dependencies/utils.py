from io import StringIO
from pathlib import Path
from tomllib import load

from pigar.core import RequirementsAnalyzer
from pigar.parser import DEFAULT_GLOB_EXCLUDE_PATTERNS

from football_data_manager.common.utils.constants import PWD


def read_essential_packages() -> list[str]:
    """
    Reads the essential packages.
    :return: The list of essential packages.
    """
    with open(PWD / "pyproject.toml", "rb") as fp:
        data = load(fp)
    return (
        data.get("tool", {})
        .get("setuptools", {})
        .get("packages", {})
        .get("find", {})
        .get("include", [])
    )


def read_requirements_paths(key: str) -> list[Path]:
    """
    Reads the sub requirements paths.
    :param key: The key of the sub requirements.
    :return: The list of paths.
    """
    if key == "essential":
        return [PWD / "requirements" / "essential.txt"]
    else:
        with open(PWD / "pyproject.toml", "rb") as fp:
            data = load(fp)
        return [
            PWD / path
            for path in data.get("tool", {})
            .get("setuptools", {})
            .get("dynamic", {})
            .get("optional-dependencies", {})
            .get(key, {})
            .get("file", [])
        ]


def read_requirements_from_path(path: Path) -> list[str]:
    """
    Reads the requirements from the given path.
    :param path: The path of the requirements file.
    :return: The list of requirements.
    """
    with open(path, "r") as fp:
        return [
            line.split("==")[0]
            for line in list(
                filter(lambda x: not x.startswith("#"), fp.read().splitlines())
            )
        ]


def read_requirements(key: str) -> list[str]:
    """
    Reads the requirements of the given key.
    :param key: The key of the requirements.
    :return: The list of requirements.
    """
    req_lines = list()
    for sub_req_path in read_requirements_paths(key):
        req_lines.extend(read_requirements_from_path(sub_req_path))
    return req_lines


def read_optional_dependencies_keys() -> list[str]:
    """
    Reads the sub requirements keys.
    :return: The list of keys.
    """
    with open(PWD / "pyproject.toml", "rb") as fp:
        data = load(fp)
    return list(
        data.get("tool", {})
        .get("setuptools", {})
        .get("dynamic", {})
        .get("optional-dependencies", {})
        .keys()
    )


def read_dependencies(path: Path) -> list[str]:
    """
    Reads the dependencies used by the given package directory.
    :param path: The path of the package directory.
    :return: The list of dependencies used in the directory.
    """
    analyzer = RequirementsAnalyzer(str(path))
    buf = StringIO()
    comparison_specifier = "=="
    analyzer.analyze_requirements(
        follow_symbolic_links=False,
        ignores=DEFAULT_GLOB_EXCLUDE_PATTERNS,
        visit_doc_str=False,
    )
    analyzer.write_requirements(
        buf,
        comparison_specifier=comparison_specifier,
        with_banner=False,
        with_ref_comments=False,
        with_unknown_imports=False,
    )
    return [
        dep.split(comparison_specifier)[0]
        for dep in filter(
            lambda x: comparison_specifier in x, buf.getvalue().split("\n")
        )
    ]
