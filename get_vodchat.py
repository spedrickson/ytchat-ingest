import json
import sys

import pytchat

from channel import YtChannel


def main(args):
    print(str(args))

    chatdb = YtChannel("UCrPseYLGpNygVi34QpGNqpA")  # TODO: add channel id param
    video_id = args[1]

    # check for existing vod progress and resume TODO: add force param to start from beginning
    cont = chatdb.vod_progress(video_id)
    if cont:
        print(f"resuming from: {cont}")
        chat = pytchat.create(
            video_id=video_id, force_replay=True, replay_continuation=cont
        )
    else:
        print("no continuation data, starting from beginning")
        chat = pytchat.create(video_id=video_id, force_replay=True)

    if not chat.is_replay():
        print(f"video {video_id} did not have chat replay or was not accessible")

    count = err_count = dup_count = 0
    # TODO: fix signal handling
    last_cont = ""
    while chat.continuation:
        l_count = l_err = l_dup = 0
        for message in chat.get().items:
            l_count += 1
            message_dict = json.loads(message.json())
            match chatdb.insert_message(message_dict):
                case -1:
                    l_err += 1
                case 1:
                    l_dup += 1
        count += l_count
        err_count += l_err
        dup_count += l_dup

        chatdb.set_vod_progress(video_id, chat.continuation)
        chat = pytchat.create(
            video_id=video_id, force_replay=True, replay_continuation=chat.continuation
        )
        print(
            f"attempted to add {l_count} items. had: {l_count - (l_dup + l_err)} successes, {l_dup} duplicates, {l_err} errors. continuing from: {chat.continuation}"
        )
        if last_cont == chat.continuation:
            print(
                "encountered same continuation token twice, assuming chat archive has ended"
            )
            break
        last_cont = chat.continuation

    print(
        f"total had {count} items. had: {count - (err_count + dup_count)} successes, {dup_count} duplicates, {err_count} errors"
    )
    chat.terminate()


if __name__ == "__main__":
    main(sys.argv)
