# Managed inputs

Managed inputs are input files stored on the Nextmv platform and managed at an
application level.

Managed inputs can be created in two different ways:

* Via the ID of an existing [run][runs] within the application
* Via the ID of [data uploaded to Nextmv][application-upload-data]
  through the use of a [presigned URL][application-upload-url].

## Creating inputs via a run ID

Example code for generating a managed input via run ID:

```python
import os

import nextmv
from nextmv.cloud import Application, Client

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")
managed_input = app.new_managed_input(
    id="<YOUR_MANAGED_INPUT_ID>",
    name="<YOUR_MANAGED_INPUT_ID>",
    description="An optional description",
    run_id="<YOUR_RUN_ID>",
)
nextmv.write(managed_input)
```

A possible output of such code
(where the format of the existing run `<YOUR_RUN_ID` is the `JSON` type):

```json
{
    "app_id": "<YOUR_APP_ID>",
    "created_at": "2026-03-03T14:02:12.000000Z",
    "description": "An optional description",
    "id": "<YOUR_MANAGED_INPUT_ID>",
    "run_id": "<YOUR_RUN_ID>",
    "format": {
        "input": {
            "type": "json"
        }
    },
    "name": "<YOUR_MANAGED_INPUT_ID>",
    "updated_at": "2026-03-03T14:02:12.000000Z"
}
```

!!! tip

    The `format` information of a run used to create a managed input will be
    inherited by the managed input generated.

## Creating inputs via the ID of uploaded data

Example code for generating a managed input via uploaded data:

```python
import os

import nextmv
from nextmv.cloud import Application, Client

with open("<YOUR-INPUT-FILE>") as f:
    input = json.load(f)

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")

# Get the upload URL.
upload_url = app.upload_url()

# Upload the input.
app.upload_data(data=input, upload_url=upload_url)

managed_input = app.new_managed_input(
    id="<YOUR_MANAGED_INPUT_ID>",
    name="<YOUR_MANAGED_INPUT_ID>",
    description="An optional description",
    upload_id=upload_url.upload_id,
)
nextmv.write(managed_input)
```

A possible output of such code:

```json
{
    "app_id": "<YOUR_APP_ID>",
    "created_at": "2026-03-03T14:02:12.000000Z",
    "description": "An optional description",
    "id": "<YOUR_MANAGED_INPUT_ID>",
    "upload_id": "generated-upload-id",
    "format": {
        "input": {
            "type": "json"
        }
    },
    "name": "<YOUR_MANAGED_INPUT_ID>",
    "updated_at": "2026-03-03T14:02:12.000000Z"
}
```

!!! warning

    When using input that is not `JSON` formatted, the `Format` argument _must_
    be supplied to the `new_managed_input` function

[runs]: ./runs.md
[application-upload-url]: ./reference/application.md#nextmv.nextmv.cloud.application.Application.upload_url
[application-upload-data]: ./reference/application.md#nextmv.nextmv.cloud.application.Application.upload_data
