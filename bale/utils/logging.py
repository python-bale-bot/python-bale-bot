import logging

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', '%Y-%m-%d %H:%M:%S', style='{'))

    library = __name__.partition('.')[0]
    logger = logging.getLogger(library)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)