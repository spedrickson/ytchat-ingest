from sys import argv
# from channel import YtChannel
from db_connector import CommentDB
from datetime import datetime
from pathlib import Path

from loguru import logger

import json


def read_comments(file):
    with open(file) as f:
        data = json.load(f)
        return items_to_comments(data["items"])


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
    renamed['updatedAt'] = datetime.fromisoformat(renamed['updatedAt'])
    renamed['publishedAt'] = datetime.fromisoformat(renamed['publishedAt'])
    renamed.pop("channelId") # comments are inserted to a specific channel db, this field is useless
    return renamed

# flattens nested comments into their own
def items_to_comments(items: list):
    for item in items:
        snippet = item["snippet"]
        yield normalize_top_level_snippet(snippet)
        if 'replies' in item:
            for reply in item['replies']['comments']:
                yield normalize_reply(reply)


def rename_keys(dictionary: dict):
    return dict((rename_key(k), v) for k, v in dictionary.items())


def rename_key(key: str):
    return key.replace("topLevelComment_", "", 1).replace("snippet_", "", 1).replace("_value", "", 1)

def main():
    # basic args
    if len(argv) < 3:
        print("must provide channelID as 1st param, and directory full of JSON files as 2nd param")
        return
    channel_id = argv[1]
    path = argv[2]

    db = CommentDB(channel_id, enforce_index=True)
    for file in Path(path).glob('*.json'):
        comments = list(read_comments(file))
        db.insert_comments(comments)

if __name__ == "__main__":
    main()
