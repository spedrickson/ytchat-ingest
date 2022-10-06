# ytchat-ingest

Ingest messages from YouTube live chat to MongoDB.

This is related to the projects ytchat-backend and ytchat-frontend.

## Limitations

Currently, this program is designed to ingest from only one chat at a time.

Additionally, there is no good way to find *pending* YouTube live streams, so it checks for a redirect
from `https://youtube.com/CHANNEL_ID/live`. This means that it only supports one live stream per channel at a time,
depending on which the URL redirects to.

## Setup

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Configuration

Before launching, set any necessary environment variables.

```bash
# bash
YTCHAT_CHANNELID=...
```

```bash
# powershell
$env:YTCHAT_CHANNELID = "..."
```

#### Supported variables

| Variable                 | Purpose                                                    | Default                             |
|--------------------------|------------------------------------------------------------|-------------------------------------|
| YTCHAT_CHANNELID         | Which MongoDB collection messages should be inserted into. | `UCrPseYLGpNygVi34QpGNqpA` (Ludwig) |
| YTCHAT_INGEST_MONGO_URL  | Host URL for MongoDB instance that should store messages.  | `localhost`                         |
| YTCHAT_INGEST_MONGO_PORT | Port for the MongoDB instance that should store messages.  | `27017`                             |

#### MongoDB Setup

Note: you will need to set an index that enforces uniqueness of messages based on the `id` field (not `_id`). Otherwise,
you will occasionally get duplicate messages inserted into the DB.

## Running

```bash
python3 main.py CHANNEL_ID
```

## License

This program is released under the [MIT License](LICENSE)
