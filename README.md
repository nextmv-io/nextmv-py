# Nextmv Python SDK

This is the Python SDK for the Nextmv Platform. Before starting:

1. [Sign up][signup] for a Nextmv account.
2. Get your API key. Go to [Team > API Key][api-key].

Visit the [docs][docs] for more information.

## Installation

Requires Python `>=3.10`. Install using `pip`:

```bash
pip install nextmv
```

## Usage

Make sure that you have your API key set as an environment variable:

```bash
export NEXTMV_API_KEY="<YOUR-API-KEY>"
```

Additionally, you must have a valid app in Nextmv Cloud.

- Make a run and get the results.

```python
import os

from nextmv.cloud import Application, Client, PollingOptions

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

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR-APP-ID>")
result = app.new_run_with_result(
    input=input,
    instance_id="latest",
    run_options={"solve.duration": "1s"},
    polling_options=PollingOptions(),  # Customize the polling options.
)
print(result.to_dict())

```

[signup]: https://cloud.nextmv.io
[docs]: https://nextmv.io/docs
[api-key]: https://cloud.nextmv.io/team/api-keys
