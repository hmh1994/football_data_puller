from football_data_puller.utils.constants import PWD
from tests.dependencies.utils import (
    read_requirements_paths,
    read_dependencies,
    read_essential_packages,
    read_requirements,
    read_optional_dependencies_keys,
    read_requirements_from_path,
)


class TestDependencies:
    """
    Tests the dependency status.
    """

    optional_package_paths = {
        "all": PWD,
        "dev": PWD / "football_data_puller",
        "test": PWD / "tests",
    }

    def test_requirements_file_exists(self):
        """
        Tests the requirements file exists.
        """
        optional_dependencies_keys = read_optional_dependencies_keys()
        # Assertion #1: The optional dependencies keys are set correctly.
        assert len(self.optional_package_paths) + 1 == len(
            optional_dependencies_keys
        ), "Optional dependencies keys not set correctly."
        for key in optional_dependencies_keys:
            # Assertion #2: The key in the optional dependencies is in the optional package.
            assert (
                key in self.optional_package_paths if key != "essential" else True
            ), f"Key {key} not found."
            # Assertion #3: The requirement file path exists.
            assert (
                    len(read_requirements_paths(key)) != 0
            ), f"Requirements file not found for {key}."

    def test_requirements_alphabetical_order(self):
        """
        Tests the requirements are in alphabetical order.
        """
        requirements_dir = PWD / "requirements"
        for path in requirements_dir.iterdir():
            if path.is_file() and path.name.endswith(".txt"):
                requirements = read_requirements_from_path(path)
                # Assertion #1: The requirements are in alphabetical order.
                assert requirements == sorted(
                    requirements
                ), f"Requirements in {path} are not in alphabetical order."

    def test_essential_dependencies(self):
        """
        Tests the essential dependencies are in the requirements.
        """
        install_dependencies = [
            dep
            for deps in [
                read_dependencies(PWD / package.removesuffix("*").replace(".", "/"))
                for package in read_essential_packages()
            ]
            for dep in deps
        ]
        install_requirements = read_requirements("essential")
        for dependency in set(install_dependencies):
            # Assertion #1: The dependency is in the requirements.
            assert any(
                dependency == requirement for requirement in install_requirements
            ), f"Dependency {dependency} not found in essentials requirements."

    def test_optional_dependencies(self):
        """
        Tests the optional dependencies are in the requirements.
        """
        for key, path in self.optional_package_paths.items():
            requirements = read_requirements(key)
            dependencies = read_dependencies(path)
            for dependency in set(dependencies):
                # Assertion #1: The dependency is in the requirements.
                assert any(
                    dependency == requirement for requirement in requirements
                ), f"Dependency {dependency} not found in {key}'s requirements."
