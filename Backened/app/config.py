
import tomllib
from pathlib import Path
import sys
from Backened.app.utils.logger import get_logger

logger = get_logger("main")

def load_config(file_name : str = "pyproject.toml") -> dict:
    try:
        file_path = Path(file_name)
        
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        logger.error(f"Configuration file is corrupted/invalied : {e}")
        raise SystemExit("Application cannot start with invalid config.")from e
    except FileNotFoundError as e:
        logger.error(f"Configuration file is missing : {e}")
        raise SystemExit("Application cannot start without config file.")from e
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        sys.Exit(1)