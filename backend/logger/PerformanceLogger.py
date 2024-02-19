import logging

from AppConfig import AppConfig
config = AppConfig()

PERFORMANCE_LOGGER_PATH = config.get("logging", "performance_path", True)
USE_PERFORMANCE_LOGGER = config.get("logging", "performance")

class PerformanceLogger:
    logger = None
    is_initialised = False

    def log(message):
        if not USE_PERFORMANCE_LOGGER:
            return
        if not PerformanceLogger.is_initialised:
            PerformanceLogger.logger = logging.getLogger("PerformanceLogger")
            PerformanceLogger.logger.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler = logging.FileHandler(PERFORMANCE_LOGGER_PATH)
            file_handler.setFormatter(formatter)
            PerformanceLogger.logger.addHandler(file_handler)
            PerformanceLogger.logger.info("Performance logger loaded")
            PerformanceLogger.is_initialised = True
        PerformanceLogger.logger.info(message)