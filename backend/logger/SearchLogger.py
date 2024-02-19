import logging

from AppConfig import AppConfig
config = AppConfig()

SEARCH_LOGGER_PATH = config.get("logging", "search_path", True)
USE_SEARCH_LOGGER = config.get("logging", "search")

class SearchLogger:
    logger = None
    is_initialised = False

    def log(message):
        if not USE_SEARCH_LOGGER:
            return
        if not SearchLogger.is_initialised:
            SearchLogger.logger = logging.getLogger("SearchLogger")
            SearchLogger.logger.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(SEARCH_LOGGER_PATH)
            file_handler.setFormatter(formatter)
            SearchLogger.logger.addHandler(file_handler)
            SearchLogger.logger.info("Search logger loaded")
            SearchLogger.is_initialised = True
        SearchLogger.logger.info(message)