# standard library
import json
import sys
from time import sleep
from urllib.parse import urlparse
from urllib.parse import parse_qs

# requirements
import pytchat
import requests
from loguru import logger
from lxml import html

# project
import utils
from db_connector import ChatDB


class YtChannel:
    def __init__(self, channel_id: str, db_name=None):
        if not db_name:
            db_name = channel_id
        self.channel_id = channel_id
        self.conn = ChatDB(self.channel_id, db_name=db_name)
        utils.setup_logger(self.channel_id)
        if len(str(channel_id)) == 0:
            raise RuntimeError("cannot create YtChannel instance without channel ID")

    def get_live_id(self):
        """Queries the channel for a live or scheduled broadcast\n
        example: `yCuHrjO_LK8` from the URL: `https://www.youtube.com/watch?v=yCuHrjO_LK8`\n
        :returns: video id for the live/scheduled broadcast, or None if no video found"""
        if self.channel_id.startswith('@'):
            url = f'https://youtube.com/{self.channel_id}/live'
        else:
            url = f'https://youtube.com/channel/{self.channel_id}/live'
        logger.debug(f"testing channel live status: {url}")
        page = requests.get(url)
        tree = html.fromstring(page.content)
        canonical_url = str(tree.xpath('//link[@rel="canonical"]/@href')[0])
        if "/channel/" not in canonical_url:
            logger.info(f"found live url ({canonical_url}) for channel {self.channel_id}")
            parsed_url = urlparse(canonical_url)
            video_id = parse_qs(parsed_url.query)['v'][0]
            return video_id
        return None

    def ingest(self):
        logger.info(f"starting to endlessly ingest chat for channel: {self.channel_id}")
        while True:
            try:
                video_id = self.wait_for_live_id()
                self.ingest_video(video_id)
            except KeyboardInterrupt:
                logger.info("manual user interrupt, closing")
                sys.exit()
            except Exception as e:
                logger.error(f"unhandled error: {e}")
                sleep(5)

    def ingest_video(self, video_id: str):
        count = err_count = 0
        chat = pytchat.create(video_id=video_id)
        while chat.is_alive():
            messages = chat.get().sync_items()
            json_messages = list(map(lambda m: json.loads(m.json()), messages))
            l_count = len(json_messages)
            success_count = self.conn.insert_comments(list(json_messages))
            l_err = l_count - success_count
            count += l_count
            err_count += l_err
            logger.info(f"attempted to add {l_count} items. had: {l_err} errors/duplicates")
        logger.info(f"total had {count} items. {err_count} errors/duplicates")
        chat.terminate()

    def wait_for_live_id(self):
        """Waits forever for a live or scheduled broadcast from the channel, then returns the id.\n
           example: `yCuHrjO_LK8` from the URL: `https://www.youtube.com/watch?v=yCuHrjO_LK8`\n
           :returns: video id for the live/scheduled broadcast"""
        logger.info(f"waiting for video_id on channel: {self.channel_id}")
        video_id = None
        while not video_id:
            video_id = self.get_live_id()
            if not video_id:
                logger.debug(f"sleeping 90 seconds before checking status again")
                sleep(90)
        return video_id

    def test(self, video_id: str):
        count = err_count = 0
        chat = pytchat.create(video_id=video_id)
        while chat.is_alive():
            messages = chat.get().sync_items()
            json_messages = list(map(lambda m: json.loads(m.json()), messages))
            l_count = len(json_messages)
            success_count = self.conn.insert_comments(list(json_messages))
            l_err = l_count - success_count
            count += l_count
            err_count += l_err
            logger.info(f"attempted to add {l_count} items. had: {l_err} errors/duplicates")
        logger.info(f"total had {count} items. {err_count} errors/duplicates")
        chat.terminate()

    # pass these methods on to ChatDB connector
    def insert_comments(self, comments: list):
        return self.conn.insert_comments(comments)

    def insert_comment(self, comment: dict):
        return self.conn.insert_comment(comment)

    def vod_progress(self, video_id: str):
        return self.conn.vod_progress(video_id)

    def set_vod_progress(self, video_id: str, continuation: str):
        return self.conn.set_vod_progress(video_id, continuation)
