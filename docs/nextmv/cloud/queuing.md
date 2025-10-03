# Queuing and prioritization

Queuing lets you submit runs beyond your allowed maximum concurrency limits. Queues
are maintained for each execution class and ordered by priority then age.
The next run started upon a completion will be the highest priority, oldest
request for the execution class of the completed run.

A priority is between  1 (highest) and 9, with a priority 6 by default. Since
queuing is specific to execution classes, run requests in execution classes that
are not at limit will start without delay.

In some cases you may not want a run request to queue. An example could be
a real time workload that must complete in a short time.  In that case when you
submit you specify no queuing behavior in the request, and you'll receive a busy
failure if you are at capacity that and you can then manage immediately.

!!! tip

    By default runs are queued if capacity does not exist. Queued runs have a
    default priority of 6. Disable queuing if you prefer to receive a busy error
    (429) if no capacity remains for the execution class.

You can use the `configuration` argument when starting a new run. Here is an
example:

```python
import json
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

result = app.new_run_with_result(
    input=input,
    instance_id="<YOUR_INSTANCE_ID>",
    run_options={
        "solve.duration": "10s",
        "solve.iterations": "20",
    },
    configuration=cloud.RunConfiguration(
        queuing=cloud.RunQueuing(
            priority=3,
        ),
    ),
)

nextmv.write(result)
```

## Queued runs

When you submit a run, it is placed in a queue. The run will be executed when
resources are available. The queue is set at the account level, so you can
visualize runs from all applications in the same queue. A run is queued when
the `status_v2` in the metadata is `queued`.

To get the account queue you can use the  [`Account.queue`][account-queue]
method.

```python
import os

import nextmv
from nextmv.cloud import Client
from nextmv.cloud.account import Account

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
account = Account(client=client)
queue = account.queue()
nextmv.write(queue)
```

```bash
$ python main.py
{
  "runs": [
      {
        "id": "latest-VdOraGaIR",
        "user_email": "sebastian@nextmv.io",
        "name": "",
        "description": "",
        "created_at": "2024-04-09T16:38:51.974643483Z",
        "application_id": "routing",
        "application_instance_id": "latest",
        "application_version_id": "v1.0.4",
        "execution_class": "8c16gb12h",
        "status": "running",
        "status_v2": "queued"
      },
      {
        "id": "latest-JRIr-MaIg",
        "user_email": "sebastian@nextmv.io",
        "name": "",
        "description": "",
        "created_at": "2024-04-09T16:38:48.593808223Z",
        "application_id": "routing",
        "application_instance_id": "latest",
        "application_version_id": "v1.0.4",
        "execution_class": "8c16gb12h",
        "status": "running",
        "status_v2": "queued"
      }
  ]
}
```

[account-queue]: ./reference/account.md#nextmv.nextmv.cloud.account.Account.queue
