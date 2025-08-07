# Batch experiments

!!! tip

    Find more information about batch experiments in this [section of the Nextmv docs](https://docs.nextmv.io/docs/using-nextmv/experiments/batch).

!!! tip

    [Scenario tests](./scenario-tests.md) are a more flexible form of batch experiments. Consider using
    them instead.

Batch experiments are used to analyze the output from one or more decision
models on a fixed [input set][input-sets]. They are generally used as an
exploratory test to understand the impacts to business metrics (or KPIs) when
updating a model with a new feature, such as an additional constraint. They can
also be used to validate that a model is ready for further testing and likely to
make an intended business impact.

To create a batch experiment, you need to build the underlying runs, using an
input set and instances. After, define the desired batch experiment ID and name.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = Application(client=client, id="<YOUR_APP_ID>")

# Define the input set to use for the batch experiment.
input_set = app.input_set(input_set_id="<YOUR_INPUT_SET_ID>")

# Define the instances to run the batch experiment on.
instances = ["<SAMPLE_INSTANCE_ID_1>", "<SAMPLE_INSTANCE_ID_2>"]

# Build the batch experiment runs.
input_ids = input_set.input_ids
if len(input_set.input_ids) == 0:
    input_ids = [input.id for input in input_set.inputs]

runs = []
for instance in instances:
    for input_id in input_ids:
        run = cloud.BatchExperimentRun(
            input_id=input_id,
            instance_id=instance,
            input_set_id=input_set.id,
        )
        runs.append(run)


# Create the batch experiment with the defined runs.
batch_exp_id = app.new_batch_experiment(
    id="<YOUR_BATCH_EXPERIMENT_ID>",
    name="<YOUR_BATCH_EXPERIMENT_ID>",
    runs=runs,
    description="An optional description",
)
print(batch_exp_id)
```  

```bash
experiment-1
```  

Defining `option_sets` is supported as well.

Alternatively, you may use the `instance_ids` argument to specify which
instances to use for the batch experiment.

```python
batch_exp_id = app.new_batch_experiment(
    id="<YOUR_BATCH_EXPERIMENT_ID>",
    name="<YOUR_BATCH_EXPERIMENT_ID>",
    input_set_id="<YOUR_INPUT_SET_ID>",
    instance_ids=["<SAMPLE_INSTANCE_ID_1>", "<SAMPLE_INSTANCE_ID_2>"],
    description="An optional description",
)
print(batch_exp_id)
```

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
