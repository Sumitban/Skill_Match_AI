import logging
import logging.handlers
import pathlib

# file path 
base_dir = pathlib.Path(__file__).resolve().parent.parent.parent
file_path = base_dir/"logs"/"app.log"

# creating logger
logger = logging.getLogger("main_logger")
logger.setLevel(logging.INFO)

# creating handler
file = logging.handlers.TimedRotatingFileHandler(
    filename= file_path,
    when= "midnight",
    backupCount= 7
)

# setting formatter
fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

file.setFormatter(fmt)

logger.addHandler(file)