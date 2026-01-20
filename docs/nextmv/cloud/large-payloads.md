# Large payloads

!!! tip

    When using the [`Application.new_run`](./reference/application.md#nextmv.nextmv.cloud.application._run.ApplicationRunMixin.new_run) or [`Application.new_run_with_result`](./reference/application.md#nextmv.nextmv.cloud.application._run.ApplicationRunMixin.new_run_with_result) methods, input size is automatically handled by the SDK.
    You may skip this tutorial if you are using these methods.

When submitting a new run and retrieving the run's results, there are size
limits to consider for the payload: 5MB for the input and output of a run.

You can use this large payloads workflow to handle bigger sizes. When using
this alternative, note that:

* There is a maximum limit of 500MB when uploading a file.
* There is a maximum limit of 100MB when downloading a file.

The process for handling large payloads is as follows:

![Large payloads][large-payloads-image]

You can use the following methods to handle large payloads:

* [`Application.upload_url`][application-upload-url]: This method returns a
      temporary, pre-signed URL to which you can upload a file.
* [`Application.upload_large_input`][application-upload-large-input]: This
      method takes the actual data and uploads it to the pre-signed URL.

Here is an example of how to use these methods.

```python
import json
import os
import time

import nextmv
from nextmv.cloud import Application, Client, DownloadURL

with open("<YOUR-INPUT-FILE>") as f:
    input = json.load(f)

# Create a client and an application object.
client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR-APP-ID>")

# Get the upload URL.
upload_url = app.upload_url()

# Upload the input.
app.upload_large_input(input=input, upload_url=upload_url)

# Make a run.
run_id = app.new_run(
    instance_id="<YOUR-INSTANCE-ID>",
    upload_id=upload_url.upload_id,  # Use the upload ID from the upload URL.
    options={
        "solve_duration": "2", # Customize options.
    },
)

# You should poll for results, but we'll just sleep for now.
time.sleep(5)

# Get the download URL.
response = client.request(
    method="GET",
    endpoint=f"{app.endpoint}/runs/{run_id}",
    query_params={"format": "url"},
)
download_url = DownloadURL.from_dict(response.json()["output"])

# Download the output.
download_response = client.request(
    method="GET",
    endpoint=download_url.url,
    headers={"Content-Type": "application/json"},
)
nextmv.write(download_response)
```

[large-payloads-image]: ../../../images/large_file_run_overview.png
[application-upload-url]: ./reference/application.md#nextmv.nextmv.cloud.application.Application.upload_url
[application-upload-large-input]: ./reference/application.md#nextmv.nextmv.cloud.application.Application.upload_large_input
