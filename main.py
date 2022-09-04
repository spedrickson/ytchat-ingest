import os

from sys import argv
from channel import YtChannel

channel_id = "UCrPseYLGpNygVi34QpGNqpA" if len(argv) == 1 else argv[1]
channel_id = os.environ['YTCHAT_CHANNELID'] if 'YTCHAT_CHANNELID' in os.environ else channel_id

channel = YtChannel(channel_id)
if len(argv) > 2:
    channel.ingest_video(argv[2])
else:
    channel.ingest()
