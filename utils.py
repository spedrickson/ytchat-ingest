import datetime
from sys import stdout
from time import sleep

from loguru import logger
# from pytchat import ChatProcessor

from processor.chat_processor import ChatProcessor


# from processor


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

# class RawChatProcessor(ChatProcessor):
#
#     def process(self, chat_components: list):
#         chatlist = []
#         timeout = 0
#         ret = {"kind": "youtube#liveChatMessageListResponse", "etag": "", "nextPageToken": ""}
#         if chat_components:
#             for chat_component in chat_components:
#                 timeout += chat_component.get('timeout', 0)
#                 chatdata = chat_component.get('chatdata')
#
#                 if chatdata is None:
#                     break
#                 for action in chatdata:
#                     match action:
#                         case "markChatItemAsDeletedAction":
#                             print(f"markChatItemAsDeletedAction")
#
#                         case _:
#                             print(f"unrecognized action type: {action}")
#                             # logger.warning("")
#
#                     # chatlist.append(action)
#
#                     # if action is None:
#                     #     continue
#
#                     # if action.get('addChatItemAction'):
#                     #     continue
#                     # if action['addChatItemAction'].get('item') is None:
#                     #     continue
#                     #
#                     # chat = self.parse(action)
#                     # if chat:
#         ret["pollingIntervalMillis"] = int(timeout * 1000)
#         ret["pageInfo"] = {
#             "totalResults": len(chatlist),
#             "resultsPerPage": len(chatlist),
#         }
#         ret["items"] = chatlist
#         return ret
#
#     # def parse(self, sitem):
#     #
#     #     action = sitem.get("addChatItemAction")
#     #     if action:
#     #         item = action.get("item")
#     #     if item is None:
#     #         return None
#     #     rd = {}
#     #     try:
#     #         renderer = self.get_renderer(item)
#     #         if renderer is None:
#     #             return None
#     #
#     #         rd["kind"] = "youtube#liveChatMessage"
#     #         rd["etag"] = ""
#     #         rd["id"] = 'LCC.' + renderer.get_id()
#     #         rd["snippet"] = renderer.get_snippet()
#     #         rd["authorDetails"] = renderer.get_authordetails()
#     #     except (KeyError, TypeError, AttributeError) as e:
#     #         logger.error(f"Error: {str(type(e))}-{str(e)}")
#     #         logger.error(f"item: {sitem}")
#     #         return None
#     #
#     #     return rd
#     #
#     # def get_renderer(self, item):
#     #     if item.get("liveChatTextMessageRenderer"):
#     #         renderer = LiveChatTextMessageRenderer(item)
#     #     elif item.get("liveChatPaidMessageRenderer"):
#     #         renderer = LiveChatPaidMessageRenderer(item)
#     #     elif item.get("liveChatPaidStickerRenderer"):
#     #         renderer = LiveChatPaidStickerRenderer(item)
#     #     elif item.get("liveChatLegacyPaidMessageRenderer"):
#     #         renderer = LiveChatLegacyPaidMessageRenderer(item)
#     #     elif item.get("liveChatMembershipItemRenderer"):
#     #         renderer = LiveChatMembershipItemRenderer(item)
#     #     else:
#     #         renderer = None
#     #     return renderer
