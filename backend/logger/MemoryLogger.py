import logging

from AppConfig import AppConfig
config = AppConfig()

MEMORY_LOGGER_PATH = config.get("logging", "memory_path", True)
USE_MEMORY_LOGGER = config.get("logging", "memory")

class MemoryLogger:
    logger = None
    is_initialised=False

    @staticmethod
    def log(message):
        if not USE_MEMORY_LOGGER:
            return
        if not MemoryLogger.is_initialised:
            MemoryLogger.logger = logging.getLogger("MemoryLogger")
            MemoryLogger.logger.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(MEMORY_LOGGER_PATH)
            file_handler.setFormatter(formatter)
            MemoryLogger.logger.addHandler(file_handler)
            MemoryLogger.logger.info("Memory logger loaded")
            MemoryLogger.is_initialised = True
        MemoryLogger.logger.info(message)