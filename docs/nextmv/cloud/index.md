# Cloud overview

The `nextmv.cloud` package provides functionality to interact with Nextmv Cloud
directly.

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

In this section you will find tutorials encompassing the main features for
interacting with Nextmv Cloud.

## Application & run management

Tutorials to manage your Cloud applications and their runs.

| Feature | Description |
|---------|-------------|
| [Managing an application][manage] | Create, delete, and list applications |
| [Pushing an application][push] | Upload your executable decision model to a Cloud application |
| [Running an application][runs] | Create and manage runs for your Cloud application |
| [Versions][versions] | Manage versions of your Cloud application |
| [Instances][instances] | Manage instances of your Cloud application |
| [Track Runs][external-runs] | Associate external runs executed outside of Cloud with your Cloud application |
| [Secrets][secrets] | Manage secrets to use in your Cloud application |
| [Large Payloads][large-payloads] | Manage large payloads for your Cloud application |
| [Queuing & prioritization][queuing] | Manage queuing and prioritization for your Cloud application |
| [Execution classes][execution-classes] | Manage execution classes for your Cloud application |

## Application testing and experimentation

Tutorials to manage testing and experimentation for your Cloud applications.

| Feature | Description |
|---------|-------------|
| [Scenario tests][scenario-tests] | Manage scenario tests for your Cloud application |
| [Batch experiments][batch-experiments] | Manage batch experiments for your Cloud application |
| [Acceptance tests][acceptance-tests] | Manage acceptance tests for your Cloud application |
| [Input sets][input-sets] | Manage input sets for your Cloud application |

## Account management

| Feature | Description |
|---------|-------------|
| [Queuing & prioritization][queuing] | Get the queue for your Cloud account |
| [Integrations][integrations] | Manage integrations for your Cloud account |

[signup]: https://cloud.nextmv.io
[api-key]: https://cloud.nextmv.io/team/api-keys
[reference-client]: ./reference/client.md
[manage]: ./manage.md
[push]: ./push.md
[runs]: ./runs.md
[versions]: ./versions.md
[instances]: ./instances.md
[external-runs]: ./external-runs.md
[secrets]: ./secrets.md
[large-payloads]: ./large-payloads.md
[queuing]: ./queuing.md
[execution-classes]: ./execution-classes.md
[integrations]: ./integrations.md
[scenario-tests]: ./scenario-tests.md
[batch-experiments]: ./batch-experiments.md
[acceptance-tests]: ./acceptance-tests.md
[input-sets]: ./input-sets.md
