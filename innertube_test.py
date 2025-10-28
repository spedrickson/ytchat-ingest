import base64
import json
import time

import comment_continuation_pb2

from innertube import InnerTube

# YouTube Web CLient
CLIENT = InnerTube("WEB", "2.20240105.01.00")


def parse_text(text):
    return "".join(run["text"] for run in text["runs"])


def flatten(items):
    flat_items = {}

    for item in items:
        key = next(iter(item))
        val = item[key]

        flat_items.setdefault(key, []).append(val)

    return flat_items


def flatten_item_sections(item_sections):
    return {
        item_section["sectionIdentifier"]: item_section
        for item_section in item_sections
    }


def extract_comments(next_continuation_data):
    return [
        continuation_item["commentThreadRenderer"]
        for continuation_item in next_continuation_data["onResponseReceivedEndpoints"][
            1
        ]["reloadContinuationItemsCommand"]["continuationItems"][:-1]
    ]


# for some reason the continuation token is in hidden here:
#   [ ] onResponseReceivedEndpoints > { } 0 > { } appendContinuationItemsAction > [ ] continuationItems > { } 10 > { } continuationItemRenderer > { } button > { } buttonRenderer > { } command > { ) continuationCommand > "" token
def extract_comments_continuation_token(response):
    for endpoint in response["onResponseReceivedEndpoints"]:
        # print("onResponseReceivedEndpoints")
        if "appendContinuationItemsAction" not in endpoint:
            continue
        for continuation_item in endpoint["appendContinuationItemsAction"][
            "continuationItems"
        ]:
            # print("\tappendContinuationItemsAction")
            if "continuationItemRenderer" not in continuation_item:
                continue
            # print(continuation_item)
            return continuation_item["continuationItemRenderer"]["button"][
                "buttonRenderer"
            ]["command"]["continuationCommand"]["token"]
    print("couldn't find continuation token :(")


# video_id = "BV1O7RR-VoA"

# Get comments for a given video
# comments = get_comments(video_id)

# Select a comment to highlight (in this case the 3rd one)
# comment = comments[2]

# Print the comment we're going to highlight
# print("### Highlighting Comment: ###")
# print()
# print_comment(comment)
# print("---------------------")
# print()

# Get comments, but highlighting the selected comment
# highlighted_comments = get_comments(video_id, params=params)

# print("### Comments: ###")
# print()

# for comment in highlighted_comments:
# print_comment(comment)


# construct the first continuation protobuf message from the required params
# further continuations should be pulled from the response
def construct_continuation_from_thread_parent(
    video_id,
    thread_id,
    uploader_id,
    max_replies=10,
    unknown_value_1=0,
    sort=-1,
    unknown_value_2=1,
    unknown_value_3=3,
):
    continuation = comment_continuation_pb2.Continuation()
    continuation.video_id.value = video_id
    continuation.int_3 = unknown_value_3  # no idea what this one does
    continuation.continuation.context.thread_id = thread_id
    continuation.continuation.context.something.idk = (
        unknown_value_1  # no idea what this is
    )
    continuation.continuation.context.max_replies_maybe = max_replies
    continuation.continuation.context.sort_maybe = (
        sort  # i think this might be sorting?
    )
    continuation.continuation.context.uploader_id = uploader_id
    continuation.continuation.context.video_id = (
        video_id  # don't know why they need it twice
    )
    continuation.continuation.context.sub_message_16.int_1 = unknown_value_2
    continuation.continuation.type_string = f"comment-replies-item-{thread_id}"
    return str(base64.b64encode(continuation.SerializeToString()))

# for some reason the author data is in hidden here:
# { } frameworkUpdates > { } entityBatchUpdate > [ ] mutations > { } 40 > { ) payload > { } commentEntityPayload > { } author
def extract_comments(response):
    if "frameworkUpdates" not in response:
        print("no frameworkUpdate in response")
        return
    if "entityBatchUpdate" not in response["frameworkUpdates"]:
        print("no entityBatchUpdate in frameworkUpdate")
        return
    for mutation in response["frameworkUpdates"]["entityBatchUpdate"]["mutation"]:
        if "payload" not in mutation:
            continue
        if "commentEntityPayload" not in mutation["payload"]:
            continue
        yield mutation["payload"]["commentEntityPayload"]
    # print("couldn't find comments :(")

def get_thread(video_id, thread_id, uploader_id):
    continuation = construct_continuation_from_thread_parent(video_id, thread_id, uploader_id)
    count = 0
    comments = [None]
    while continuation and len(comments) > 0:
        print(f"{continuation=}")
        response = CLIENT.next(continuation=continuation)
        continuation = extract_comments_continuation_token(response)
        comments = list(extract_comments(response))
        with open(f"thread_response_{count}.json", 'w') as f:
            json.dump(comments, f)
        print(f"[{count:05}] received {len(comments)} comments!")
        time.sleep(1)
        count += 1

def main():
    get_thread("1gUP_43J7wY", "Ugz9_k-qycnhFWbZ3ON4AaABAg", "UC3XTzVzaHQEd30rQbuvCtTQ")


    # result = CLIENT.next(continuation="Eg0SCzFnVVBfNDNKN3dZGAYygwEaUBIaVWd6OV9rLXF5Y25oRldiWjNPTjRBYUFCQWciAggAKhhVQzNYVHpWemFIUUVkMzByUWJ1dkN0VFEyCzFnVVBfNDNKN3dZQAFICoIBAggBQi9jb21tZW50LXJlcGxpZXMtaXRlbS1VZ3o5X2stcXljbmhGV2JaM09ONEFhQUJBZw==")
    # result = CLIENT.next(continuation=encoded)
    # print(json.dumps(result, indent=2 ))

    # with open(filename, 'w') as f:
    # json.dump(result, f)

    # print(f"./{filename}")
    # continuation = extract_comments_continuation_token(result)
    # print(continuation)


if __name__ == "__main__":
    main()
