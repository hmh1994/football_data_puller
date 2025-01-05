from os import path
from pathlib import Path

# Path constants
PWD: Path = Path(path.join(path.dirname(path.realpath(__file__)), "../../"))
CONFIG_PATH: Path = PWD / "configs" / ".env"
