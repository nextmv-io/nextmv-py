# Manage instances for an application

!!! tip "Reference"

    Find the reference for the `Application` class [here](./reference/application.md).

Application instances allow you to deploy and run different versions of your application in various
environments. This is useful for separating development, staging, and production workloads, or running
multiple configurations of the same application.

## Understanding instances

A Nextmv Cloud application instance is a way to configure your runs in a repeatable way.
Each instance can run a specific version of your application with its own configuration.

When you create an instance, you specify which version of your application run.

After creating a [version][version] from the latest push, you can either create a
new instance or update an instance with the latest version.

## Creating instances

If you want to create a new instance after using `app.push()`, your script might include the following.

```python
import os
from nextmv import cloud


client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

latest_version = app.new_version(
    name="v1.2.1",
    id="v1.2.1",
    description="Added new optimization features"
)

# Optional Configuration
config = cloud.InstanceConfiguration(
    options={
        "duration": "60s",
    },
)

instance = app.new_instance(
    name="Staging Instance",
    id="staging",
    version_id=latest_version.id,
    configuration=config
)
```

## Updating instances

Often, you will already have an instance created that you might want to
update with you new version.  In this case, your `push.py` might look like this:

```python
latest_version = app.new_version(
    name="v1.2.0",
    description="Added new optimization features"
)

instance = app.instance("staging")

app.update_instance(
    id=instance.id,
    name=instance.name,
    version_id=latest_version.id,
    description=instance.description,
    configuration=instance.configuration
)
```

[version]: ./reference/version.md
