import os
from sys import stdout

from loguru import logger


def setup_logger(channel_id):
    config = {
        "handlers": [
            {"sink": stdout, "format": "<g>{time}</> [<lvl>{level}</>] | {message}",
             "colorize": True, "level": "DEBUG"},
            {"sink": f"logs/{channel_id}.log", "serialize": True, "rotation": "100 MB", "retention": 60},
        ]
    }
    logger.configure(**config)


def os_notify(video_id, channel_id):
    if os.name == 'nt':
        from winotify import Notification
        try:
            toast = Notification(app_id="ytchat-ingest",
                                 title=f"Ingesting live chat",
                                 msg=f"Chat from video: {video_id} | channel: {channel_id}",
                                 icon=r"C:\Misc\Resources\Icons\youtube.png")
            toast.add_actions(label="Open Video",
                              launch=f"https://youtube.com/watch?v={video_id}")
            toast.show()
        except:
            logger.info("could not send OS notification")
