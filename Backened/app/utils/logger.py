import logging
import logging.config
import yaml
import pathlib

# 1. Define the path relative to this file
CONFIG_PATH = pathlib.Path(__file__).parent.parent / "config" / "logging.yaml"

def setup_logging():
    """
    Initializes the logging system ONCE.
    Call this at the very start of your main file.
    """
    try:
        if not CONFIG_PATH.exists():
            raise FileNotFoundError(f"Config not found at {CONFIG_PATH}")
            
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
            
        # Ensure the logs directory exists so RotatingFileHandler doesn't fail
        # This extracts the directory from your YAML file paths
        for handler in config.get('handlers', {}).values():
            if 'filename' in handler:
                pathlib.Path(handler['filename']).parent.mkdir(parents=True, exist_ok=True)

        logging.config.dictConfig(config)
        
    except Exception as e:
        # Production fallback: Log to console so the app doesn't go silent
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to load logging config: {e}. Using basicConfig.")

def get_logger(name: str) -> logging.Logger:
    """
    fetch a configured logger.
    """
    return logging.getLogger(name)
