# Batch experiments

!!! tip

    Find more information about batch experiments in this [section of the Nextmv docs](https://docs.nextmv.io/docs/using-nextmv/experiments/batch).

Batch experiments are used to analyze the output from one or more decision
models on a fixed [input set][input-sets]. They are generally used as an
exploratory test to understand the impacts to business metrics (or KPIs) when
updating a model with a new feature, such as an additional constraint. They can
also be used to validate that a model is ready for further testing and likely to
make an intended business impact.

Define the desired batch experiment ID and name. After, create the batch
experiment.

```python
import os

from nextmv.cloud import Application, Client

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")
batch_experiment_id = app.new_batch_experiment(
    id="<YOUR_BATCH_EXPERIMENT_ID>",
    name="<YOUR_BATCH_EXPERIMENT_ID>",
    input_set_id="<YOUR_INPUT_SET_ID>",
    instance_ids=["latest", "latest-2"],
    description="An optional description",
)
print(batch_experiment_id)
```  

```bash
experiment-1
```  

Defining `runs` and `option_sets` is supported as well.

## Delete a batch experiment

Deleting a batch experiment will also delete all of the associated information
such as the udnerlying app runs.

!!! warning

    This action is permanent and cannot be undone.

To delete a batch experiment, you can use the
`Application.delete_batch_experiment` method.

```python
import os

from nextmv.cloud import Application, Client

client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR-APP-ID>")
app.delete_batch_experiment(batch_id="<YOUR-BATCH-EXPERIMENT-ID>")
```

You will _not_ be prompted to confirm the deletion.

[input-sets]: ./input-sets.md
