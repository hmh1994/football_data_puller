from os import path
from pathlib import Path
from zoneinfo import ZoneInfo

# Path constants
PWD: Path = Path(path.join(path.dirname(path.realpath(__file__)), "../../"))
CONFIG_PATH: Path = PWD / "configs" / ".env"

# Timezone constants
BST: ZoneInfo = ZoneInfo("Europe/London")
KST: ZoneInfo = ZoneInfo("Asia/Seoul")
