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
    integration_id="my-dbx-runtime",
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
