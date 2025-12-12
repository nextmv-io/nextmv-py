# Manage integrations

!!! tip "Reference"

    Find the reference for the `Integration` class [here](./reference/integration.md).

Integrations allow Nextmv Cloud to communicate with external systems or
services. This enables you to connect your applications to runtime environments
like Databricks or data sources for seamless data exchange and execution.

## Understanding integrations

A Nextmv Cloud integration is a configuration that establishes a connection
between your Nextmv applications and external platforms. Each integration
specifies:

* The **provider** (e.g., Databricks)
* The **integration type** (runtime or data)
* Supported **execution types** (e.g., Python)
* Provider-specific **configuration** details

Integrations can be either **global** (available to all applications in your
account) or **application-specific** (limited to selected applications).

## Creating integrations

To create a new integration, use the `Integration.new` class method:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))

integration = cloud.Integration.new(
    client=client,
    name="My Databricks Runtime",
    integration_id="my-dbx-runtime", # Auto-generated if omitted
    description="Databricks integration for production workloads",
    integration_type=cloud.IntegrationType.RUNTIME,
    exec_types=[cloud.ManifestType.PYTHON],
    provider=cloud.IntegrationProvider.DBX,
    provider_config={
        "job_id": 123456789,
        "client_id": "a-client-id-123",
        "client_secret": "client-secret",
        "workspace_url": "https://identifier.cloud.databricks.com",
    },
    is_global=True,
)

print(f"Created integration: {integration.integration_id}")
```

If you want to create an integration that's only available to specific applications:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))

integration = cloud.Integration.new(
    client=client,
    name="App-Specific Integration",
    integration_id="my-dbx-runtime", # Auto-generated if omitted
    integration_type=cloud.IntegrationType.DATA,
    exec_types=[cloud.ManifestType.PYTHON],
    provider=cloud.IntegrationProvider.DBX,
    provider_config={"config_key": "config_value"},
    is_global=False,
    application_ids=["app-id-1", "app-id-2"],
)

print(f"Created integration: {integration.integration_id}")
```

the `exist_ok` parameter can be set to `True` to instantiate the integration if
it already exists.

## Running with an integration

Once you've created an integration, you can use it to execute your application
runs on external compute resources. There are two ways to configure an
integration for your runs:

1. Directly in the run configuration.
2. At the instance level.

### 1. Direct integration in run configuration

You can specify an integration directly when submitting a run using the
`RunConfiguration` class. This approach is useful for one-off runs or when you
want to use a specific integration regardless of the instance configuration.

```python
import os

from nextmv import RunConfiguration, cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

# Submit a run with a specific integration
run_id = app.new_run(
    input={"key": "value"},
    configuration=RunConfiguration(integration_id="my-dbx-runtime"),
)

print(f"Submitted run: {run_id}")
```

To get the results directly, use `new_run_with_result`:

```python
import os

from nextmv import RunConfiguration, cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

# Submit a run and wait for results
result = app.new_run_with_result(
    input={"key": "value"},
    configuration=RunConfiguration(integration_id="my-dbx-runtime"),
)

print(f"Run completed: {result.metadata.status_v2.value}")
print(f"Output: {result.output}")
```

!!! note

    When you specify an `integration_id`, the `execution_class` is automatically
    set to `"integration"`. You don't need to specify it manually.

!!! note

    Specifying an integration directly in the run configuration overrides any
    integration set at the instance level. This is useful when you need to:

      * Test different integrations without modifying the instance.
      * Route specific runs to different compute environments.
      * Use a fallback integration for certain scenarios.

### 2. Instance-level integration

For more permanent configurations, you can set an integration at the instance
level using `InstanceConfiguration`. When you submit runs using that instance,
the integration will be automatically applied.

First, create an instance with an integration:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

# Create an instance with an integration
instance = app.new_instance(
    id="inst_databricks",
    name="Databricks Instance",
    version_id="ver_1234567890",
    configuration=cloud.InstanceConfiguration(
        integration_id="my-dbx-runtime",
    ),
)

print(f"Created instance: {instance.id}")
```

Then, submit runs using the instance, the integration is automatically applied:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

# The integration from the instance configuration is used
run_id = app.new_run(
    input={"key": "value"},
    instance_id="inst_databricks",
)

print(f"Submitted run using instance integration: {run_id}")

```

Or get results directly with the `new_run_with_result` method.

## Getting integrations

To retrieve an existing integration and ensure all fields are properly
populated, use the `Integration.get` class method:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))

integration = cloud.Integration.get(client=client, integration_id="my-dbx-runtime")

print(f"Integration name: {integration.name}")
print(f"Provider: {integration.provider}")
print(f"Type: {integration.integration_type}")
print(f"Global: {integration.is_global}")
```

To view all integrations available in your Nextmv Cloud account, use the
`list_integrations` function:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))

integrations = cloud.list_integrations(client=client)

for integration in integrations:
    print(f"ID: {integration.integration_id}")
    print(f"Name: {integration.name}")
    print(f"Type: {integration.integration_type}")
    print(f"Provider: {integration.provider}")
    print(f"Global: {integration.is_global}")
    print("---")
```

## Updating integrations

To update an existing integration, call the `update` method with the fields you
want to change:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))

integration = cloud.Integration.get(client=client, integration_id="my-dbx-runtime")

updated_integration = integration.update(
    name="Updated Databricks Runtime",
    description="Updated configuration for production",
    provider_config={
        "workspace_url": "https://new-workspace.databricks.com",
        "cluster_id": "new-cluster-id",
        "token": "new-token",
    },
)

print(f"Updated integration: {updated_integration.name}")
```

You can update any combination of fields.

## Deleting integrations

To delete an integration from Nextmv Cloud, use the `delete` method:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))

integration = cloud.Integration.get(client=client, integration_id="my-dbx-runtime")

integration.delete()
print("Integration deleted successfully")
```

!!! warning

    Deleting an integration is permanent and cannot be undone. Make sure you're
    not actively using the integration in any applications before deleting it.
