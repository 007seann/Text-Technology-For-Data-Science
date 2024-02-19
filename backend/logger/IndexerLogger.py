import logging

from AppConfig import AppConfig
config = AppConfig()

INDEXER_LOGGER_PATH = config.get("logging", "indexer_path", True)
USE_INDEXER_LOGGER = config.get("logging", "indexer")

class IndexerLogger:
    logger = None
    is_initialised = False

    def log(message):
        if not USE_INDEXER_LOGGER:
            return
        if not IndexerLogger.is_initialised:
            IndexerLogger.logger = logging.getLogger("IndexerLogger")
            IndexerLogger.logger.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(INDEXER_LOGGER_PATH)
            file_handler.setFormatter(formatter)
            IndexerLogger.logger.addHandler(file_handler)
            IndexerLogger.logger.info("Indexer logger loaded")
            IndexerLogger.is_initialised = True
        IndexerLogger.logger.info(message)