# Execution classes

Execution classes define the characteristics of how instances are executed,
such as:

* cores
* memory
* maximum run time

In a nutshell, an execution class is the type of machine that is used to run
remotely. Here is the _default_ execution class that is widely available:

| Class | Cores | Memory | Maximum run time | Premium |
| --- | --- | --- | --- | --- |
| `6c9500mb870s` | 6 | 9500 MB | 14.5 minutes | ➖ |

If an execution class is not specified, this _default_ (`6c9500mb870s`) one is
used.

!!! tip

    You can read more about [execution classes here][execution-classes](https://docs.nextmv.io/docs/using-nextmv/run/execution-classes).

Use the `configuration` argument when starting a new run. Here is an example.

```python
import json
import os

import nextmv
from nextmv.cloud import Application, Client, Configuration, PollingOptions

with open(os.getenv("INPUT_FILE")) as f:
    input = json.load(f)

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")
result = app.new_run_with_result(
    input=input,
    instance_id="<YOUR_INSTANCE_ID>",
    run_options={
        "solve.duration": "10s",
        "solve.iterations": "20",
    },
    polling_options=PollingOptions(),  # Customize polling options.
    configuration=Configuration(execution_class="8c16gb12h"),
)
nextmv.write(result)
```
