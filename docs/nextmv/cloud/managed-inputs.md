# Managed inputs

Managed inputs are input files stored on the Nextmv platform and managed at an
application level.

## Creating managed inputs

Managed inputs can be created in two different ways:

* Via the ID of an existing [run][runs] within the application
* Via the ID of [data uploaded to Nextmv][application-upload-data]
  through the use of a [presigned URL][application-upload-url].

### __Via a run ID__

Example code for generating a managed input via run ID:

```python
import os

import nextmv
from nextmv.cloud import Application, Client

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id=os.getenv("APP_ID"))
managed_input = app.new_managed_input(
    id=os.getenv("MANAGED_INPUT_ID"),
    name=os.getenv("MANAGED_INPUT_ID"),
    description="An optional description",
    run_id="latest-RNBs7AKSg",
)
nextmv.write(managed_input)
```

A possible output of such code
(where environment variables `NEXTMV_API_KEY=routing` and `MANAGED_INPUT_ID=managed-input-3`,
and the format of the existing run `latest-RNBs7AKSg` is the `JSON` type):

```json
{
    "app_id": "routing",
    "created_at": "2026-03-03T14:02:12.000000Z",
    "description": "An optional description",
    "id": "managed-input-3",
    "run_id": "latest-RNBs7AKSg",
    "format": {
        "input": {
            "type": "json"
        }
    },
    "name": "managed-input-3",
    "updated_at": "2026-03-03T14:02:12.000000Z"
}
```

!!! tip

    The `format` information of a run used to create a managed input will be
    inherited by the managed input generated.

### __Via the ID of uploaded data__

Example code for generating a managed input via uploaded data:

```python
import os

import nextmv
from nextmv.cloud import Application, Client

with open("<YOUR-INPUT-FILE>") as f:
    input = json.load(f)

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id=os.getenv("APP_ID"))

# Get the upload URL.
upload_url = app.upload_url()

# Upload the input.
app.upload_data(data=input, upload_url=upload_url)

managed_input = app.new_managed_input(
    id=os.getenv("MANAGED_INPUT_ID"),
    name=os.getenv("MANAGED_INPUT_ID"),
    description="An optional description",
    upload_id=upload_url.upload_id,
)
nextmv.write(managed_input)
```

A possible output of such code
(where environment variables `NEXTMV_API_KEY=routing` and `MANAGED_INPUT_ID=managed-input-3`):

```json
{
    "app_id": "routing",
    "created_at": "2026-03-03T14:02:12.000000Z",
    "description": "An optional description",
    "id": "managed-input-3",
    "upload_id": "generated-upload-id",
    "format": {
        "input": {
            "type": "json"
        }
    },
    "name": "managed-input-3",
    "updated_at": "2026-03-03T14:02:12.000000Z"
}
```

!!! warning

    When using input that is not `JSON` formatted, the `Format` argument _must_
    be supplied to the `new_managed_input` function

[runs]: ./runs.md
[application-upload-url]: ./reference/application.md#nextmv.nextmv.cloud.application.Application.upload_url
[application-upload-data]: ./reference/application.md#nextmv.nextmv.cloud.application.Application.upload_data
