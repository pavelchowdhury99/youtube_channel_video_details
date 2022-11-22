import logging
from utils_and_configs.config import LOG_FILE_LOCATION

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler(LOG_FILE_LOCATION, mode='w+'),
                              logging.StreamHandler()])
