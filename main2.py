import json
import os

from nextmv.cloud import Client
from nextmv.cloud.account import Account

client = Client(api_key=os.getenv("NEXTMV_API_KEY_PROD"))
account = Account(client=client)
queue = account.queue()

print(json.dumps(queue.to_dict(), indent=2))  # Pretty print.
