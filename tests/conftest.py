import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR: Path = Path(__file__).resolve().parent.parent
ENV_PATH: Path = ROOT_DIR / ".env.test"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    print(
        f"\n[Warning] No configuration file found at {ENV_PATH}. Falling back to system environment variables."
    )
