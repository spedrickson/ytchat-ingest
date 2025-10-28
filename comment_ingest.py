import os

from sys import argv

# from channel import YtChannel
from db_connector import CommentDB
from datetime import datetime
from pathlib import Path

import time

from loguru import logger

import json

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

channel_id = "UCrPseYLGpNygVi34QpGNqpA"
db = CommentDB(channel_id, enforce_index=True)

class CommentWatcher:
    def __init__(self, path, filename, channel_id):
        self.observer = Observer()
        self.path = path
        self.filename = filename

    def run(self):
        event_handler = Handler(self.filename)
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(PatternMatchingEventHandler):
    def __init__(self, filename):
        super(Handler, self).__init__(
            patterns=[filename],
            ignore_patterns=["*.tmp"],
            ignore_directories=True,
            case_sensitive=False,
        )

    def on_modified(self, event):
        print(
            f"[{datetime.now().isoformat()}] new comment page: {event.src_path}"
        )
        comments = list(items_to_comments(read_comments(event.src_path)))
        db.insert_comments(comments)


channel_id = "UCrPseYLGpNygVi34QpGNqpA" if len(argv) == 1 else argv[1]
channel_id = (
    os.environ["YTCHAT_CHANNELID"] if "YTCHAT_CHANNELID" in os.environ else channel_id
)
db_name = os.environ["YTCHAT_DB_NAME"] if "YTCHAT_DB_NAME" in os.environ else channel_id


def read_comments(file=R"C:\Misc\allcomments\allcomments_test_0.json"):
    with open(file) as f:
        data = json.load(f)
        return data["items"]


# from stackoverflow: https://stackoverflow.com/a/51379007
def flatten_data(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def normalize_top_level_snippet(comment: dict):
    normalized = normalize_common(comment)
    return normalized


def normalize_reply(comment: dict):
    normalized = normalize_common(comment)
    return normalized


def normalize_common(comment):
    flattened = flatten_data(comment)
    renamed = rename_keys(flattened)
    renamed["updatedAt"] = datetime.fromisoformat(renamed["updatedAt"])
    renamed["publishedAt"] = datetime.fromisoformat(renamed["publishedAt"])
    renamed.pop(
        "channelId"
    )  # comments are inserted to a specific channel db, this field is useless
    return renamed


# flattens nested comments into their own
def items_to_comments(items: list):
    for item in items:
        if "snippet" in item:
            snippet = item["snippet"]
            yield normalize_top_level_snippet(snippet)
        if "replies" in item:
            for reply in item["replies"]["comments"]:
                yield normalize_reply(reply)


def rename_keys(dictionary: dict):
    return dict((rename_key(k), v) for k, v in dictionary.items())


def rename_key(key: str):
    return (
        key.replace("topLevelComment_", "", 1)
        .replace("snippet_", "", 1)
        .replace("_value", "", 1)
    )


def main():
    # basic args
    path = R'.\allcomments'
    filename = "*.json"

    w = CommentWatcher(path, filename, channel_id)
    w.run()
    # if len(argv) < 3:
    #     print(
    #         "must provide channelID as 1st param, and directory full of JSON files as 2nd param"
    #     )
    #     return
    # channel_id = argv[1]
    # path = argv[2]

    # db = CommentDB(channel_id, enforce_index=True)
    # for file in Path(path).glob("*.json"):
    #     comments = list(items_to_comments(read_comments(file)))
    #     db.insert_comments(comments)


if __name__ == "__main__":
    main()
