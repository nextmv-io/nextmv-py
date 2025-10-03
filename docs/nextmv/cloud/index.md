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

Tutorials to manage your Cloud Applications and their runs.

| Feature | Description |
|---------|-------------|
| [Managing an Application][manage] | Create, delete, and list applications |
| [Pushing an Application][push] | Upload your executable decision model to a Cloud Application |
| [Running an Application][runs] | Create and manage runs for your Cloud Application |
| [Versions][versions] | Manage versions of your Cloud Application |
| [Instances][instances] | Manage instances of your Cloud Application |
| [Track Runs][external-runs] | Associate external runs executed outside of Cloud with your Cloud Application |
| [Secrets][secrets] | Manage secrets to use in your Cloud Application |
| [Large Payloads][large-payloads] | Manage large payloads for your Cloud Application |
| [Queuing & prioritization][queuing] | Manage queuing and prioritization for your Cloud Application |
| [Execution classes][execution-classes] | Manage execution classes for your Cloud Application |

## Application testing and experimentation

Tutorials to manage testing and experimentation for your Cloud Applications.

| Feature | Description |
|---------|-------------|
| [Scenario tests][scenario-tests] | Manage scenario tests for your Cloud Application |
| [Batch experiments][batch-experiments] | Manage batch experiments for your Cloud Application |
| [Acceptance tests][acceptance-tests] | Manage acceptance tests for your Cloud Application |
| [Input sets][input-sets] | Manage input sets for your Cloud Application |

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
[scenario-tests]: ./scenario-tests.md
[batch-experiments]: ./batch-experiments.md
[acceptance-tests]: ./acceptance-tests.md
[input-sets]: ./input-sets.md
