import json
import os
import time

from nextmv.cloud import Application, Client
from nextmv.cloud.account import Account
from nextmv.cloud.application import Configuration

input = {
    "defaults": {"vehicles": {"speed": 20}},
    "stops": [
        {
            "id": "Nijō Castle",
            "location": {"lon": 135.748134, "lat": 35.014239},
            "quantity": -1,
        },
        {
            "id": "Kyoto Imperial Palace",
            "location": {"lon": 135.762057, "lat": 35.025431},
            "quantity": -1,
        },
    ],
    "vehicles": [
        {
            "id": "v2",
            "capacity": 2,
            "start_location": {"lon": 135.728898, "lat": 35.039705},
        },
    ],
}

client = Client(api_key=os.getenv("NEXTMV_API_KEY_PROD"))
app = Application(client=client, id="routing")
acc = Account(client=client)

for _ in range(10):
    result = app.new_run(
        input=input,
        instance_id="latest",
        # run_options={"solve.duration": "1s"},
        options={"solve.duration": "1s"},
        # polling_options=PollingOptions(max_tries=2, delay=3),  # Customize the polling options.
        configuration=Configuration(execution_class="8c16gb120m"),
    )
    print(result)

    time.sleep(2)

    result2 = acc.queue()

    print(json.dumps(result2.to_dict(), indent=2))

    # app.cancel_run(result)
