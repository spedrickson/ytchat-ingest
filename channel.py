import datetime
import json
from time import sleep
from urllib import parse

import pytchat
from loguru import logger
from playwright.sync_api import sync_playwright

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
        url = f"https://www.youtube.com/channel/{self.channel_id}/live"
        logger.info(f"testing channel live status: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            logger.debug(f"page url after load: {page.url}")
            split = parse.urlsplit(page.url)
            browser.close()
            logger.debug(f"url query: {split.query}")
            query = dict(parse.parse_qs(split.query))
            video_id = query.get("v", None)
            return video_id[0] if video_id else None

    def ingest(self):
        logger.info(f"starting to endlessly ingest chat for channel: {self.channel_id}")
        while True:
            video_id = self.wait_for_live_id()
            self.ingest_video(video_id)

    def ingest_video(self, video_id: str):
        count = err_count = 0
        chat = pytchat.create(video_id=video_id)
        last_ingest = datetime.datetime.now()
        while chat.is_alive():
            utils.minimum_wait(last_ingest)
            last_ingest = datetime.datetime.now()
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
        # count = err_count = 0
        chat = pytchat.create(video_id=video_id, processor=utils.RawChatProcessor())
        last_ingest = datetime.datetime.now()
        while chat.is_alive():
            utils.minimum_wait(last_ingest)
            last_ingest = datetime.datetime.now()
            messages = chat.get()
            items = messages.get('items', None)
            if not items:
                continue
            # json_messages = list(map(lambda m: json.loads(m.json()), messages))
            # l_count = len(json_messages)
            success_count = self.conn.insert_comments(list(items))
            # l_err = l_count - success_count
            # count += l_count
            # err_count += l_err
            # logger.info(f"attempted to add {l_count} items. had: {l_err} errors/duplicates")
        # logger.info(f"total had {count} items. {err_count} errors/duplicates")
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
