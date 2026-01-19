# Managing applications

One of the main features of `nextmv`, the general Nextmv Python SDK, is the
ability to interact with the Nextmv Platform. This allows you to run, and
experiment with your decision applications in Cloud.

Before starting:

1. [Sign up][signup] for a Nextmv account.
2. Get your API key. Go to [Team > API Key][api-key].

Make sure that you have your API key set as an environment variable:

```bash
export NEXTMV_API_KEY="<YOUR-API-KEY>"
```

Once you have your API key set up, you can create a cloud
[`Client`][reference-client]:

```python
import os
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
```

## Application

An application represents a decision model that you can run in the Nextmv
Cloud. The [`Application`][reference-application] class defines the methods to
interact with an app. You can create an app in multiple ways:

* Through the Python SDK (see next header).
* Through the [Nextmv CLI][cli].
* Through the Nextmv Cloud Console.

Once you have an app, and can identify its ID, you can interact with it.

### Create an app

You can create an app by providing the [`Client`][reference-client] instance
and the app ID:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
application = cloud.Application.new(
    client=client,
    name="My Application",
    id="<YOUR_APP_ID>",
    description="My first application",
)
```

### Delete an app

You can delete an application by using its ID.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
application = cloud.Application(client=client, id="<YOUR_APP_ID>")
application.delete()
```

### Do more

!!! tip "Reference"

    Find the reference for the `Application` class [here](./reference/application.md).

Make sure to check out the latest version of `nextmv` to see all the available
features of the [`Application`][reference-application]. Here are some of the
methods you can use that were not covered in this guide:

* `acceptance_test`: gets an acceptance test.
* `batch_experiment`: gets a batch experiment.
* `cancel_run`: cancels a run.
* `delete_batch_experiment`: deletes a batch experiment.
* `delete_acceptance_test`: deletes an acceptance test.
* `input_set`: gets an input set.
* `instance`: gets an instance.
* `list_acceptance_tests`: lists acceptance tests.
* `list_batch_experiments`: lists batch experiments.
* `list_input_sets`: lists input sets.
* `list_instances`: lists instances.
* `list_versions`: lists versions.
* `new_acceptance_test`: creates a new acceptance test.
* `new_acceptance_test_with_result`: creates a new acceptance test and gets the result.
* `new_batch_experiment`: creates a new batch experiment.
* `new_input_set`: creates a new input set.
* `new_version`: creates a new version.
* `new_instance`: creates a new instance.
* `run_input`: gets the input of a run.
* `run_logs`: gets the logs of a run.
* `run_metadata`: gets the metadata of a run.
* `run_result`: gets the result of a run.
* `run_result_with_polling`: gets the result of a run with polling.
* `update_instance`: updates an instance.
* `upload_data`: uploads data that is large or multiple files.
* `upload_url`: gets the URL for uploading.
* `version`: gets a version.

[signup]: https://cloud.nextmv.io
[api-key]: https://cloud.nextmv.io/team/api-keys
[cli]: https://docs.nextmv.io/docs/using-nextmv/reference/cli
[reference-client]: ./reference/client.md
[reference-application]: ./reference/application.md
