import os

from loguru import logger
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, BulkWriteError

import utils


class ChatDB:
    def __init__(self, channel_id: str, db_name=None):
        utils.setup_logger(channel_id)
        logger.debug(f"chatdb init for channel: {channel_id}")
        if not db_name:
            db_name = channel_id
        self.channel_id = channel_id
        mongo_host = os.environ['YTCHAT_INGEST_MONGO_URL'] if 'YTCHAT_INGEST_MONGO_URL' in os.environ else "localhost"
        mongo_port = os.environ['YTCHAT_INGEST_MONGO_PORT'] if 'YTCHAT_INGEST_MONGO_PORT' in os.environ else 27017
        client = MongoClient(host=mongo_host, port=mongo_port)
        self._db = client.get_database(db_name)

        # enforce unique messageID index
        messages = self._db.get_collection('messages')
        messages.create_index([('id', ASCENDING)], name="unique messageID", unique=True)

    # TODO: remove list type-hinting to accept generators/iterators (need len() solution)
    def insert_comments(self, comments: list):
        count = len(comments)
        if count == 0:
            logger.debug("tried to insert 0 comments, skipping")
            return 0
        try:
            self._db.messages.insert_many(comments, ordered=False)
            return count
        except BulkWriteError as e:
            panic = filter(lambda x: x['code'] != 11000, e.details['writeErrors'])
            if len(list(panic)) > 0:
                # actual error that isn't a duplicate key
                raise e
            else:
                logger.warning(f"duplicate key(s) when inserting comments")
                return count - len(e.details['writeErrors'])

    def insert_by_type(self, comments: dict):
        for key, value in comments.items():
            logger.info(f"inserting {len(value)} items into {key} collection")
            # self._db[key].insert_many(value)

    def insert_comment(self, comment: dict):
        try:
            self._db.messages.insert_one(comment)
        except DuplicateKeyError:
            logger.error(f"tried to insert duplicate message: {comment['id']}")
            return 1
        # except BaseException as e:
        #     print(f"error inserting: {e}")
        #     return -1
        return 0

    # def vod_ingest_started(self, video_id: str):
    #     self._db.vods.update_one({"video_id": video_id}, {"$set": })

    def set_vod_progress(self, video_id: str, continuation: str):
        self._db.vods.update_one({"video_id": video_id}, {"$set": {"last_continuation": continuation}}, upsert=True)

    def vod_progress(self, video_id: str):
        try:
            return self._db.vods.find_one({"video_id": video_id})['last_continuation']
        except:
            return None
