import datetime
from sys import stdout
from time import sleep

from loguru import logger


def count_comments(comments):
    count = 0
    for _ in comments:
        count += 1
    return count


def setup_logger(channel_id):
    config = {
        "handlers": [
            {"sink": stdout, "format": "<g>{time}</> [<lvl>{level}</>] | {message}",
             "colorize": True, "level": "DEBUG"},
            {"sink": f"logs/{channel_id}.log", "serialize": True, "rotation": "100 MB", "retention": 30},
        ]
    }
    logger.configure(**config)


def split_list_by_type(items: list):
    logger.debug(f"splitting {len(items)}")


minimum_wait_s = 1


# waits until at least one second has passed since the provided datetime
# returns immediately if over one second has passed
def minimum_wait(since: datetime):
    minimum_wait_micros = minimum_wait_s * 1000000
    micros = (datetime.datetime.now() - since).microseconds
    if micros >= minimum_wait_micros:
        logger.debug("over 1s since last ingest, skipping wait")
        return
    wait_micros = minimum_wait_micros - micros
    wait_s = wait_micros / 1000000  # divide by 1M to turn microseconds to seconds
    logger.debug(f"waiting {wait_s} seconds to ingest")
    sleep(wait_s)
