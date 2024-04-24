import logging

def setup_logging(level: int = logging.INFO, handler: logging.Handler = None, formatter: str = None):
    if handler is None:
        handler = logging.StreamHandler()

    if formatter is None:
        formatter = '[{asctime}] [{levelname:<8}] {name}: {message}'
    formatter = logging.Formatter(formatter, '%Y-%m-%d %H:%M:%S', style='{')
    handler.setFormatter(formatter)

    library = __name__.partition('.')[0]
    logger = logging.getLogger(library)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)