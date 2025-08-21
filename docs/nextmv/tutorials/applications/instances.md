# Manage Instances for an Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](../../reference/cloud/application.md).

Application instances allow you to deploy and run different versions of your application in various
environments. This is useful for separating development, staging, and production workloads, or running
multiple configurations of the same application.

## Understanding Instances

A Nextmv Cloud Application Instance is a way to configure your runs in a repeatable way.
Each instance can run a specific version of your application with its own configuration.

When you create an instance, you specify which version of your application run.

In your `push.py`, after creating a [version][version] from the latest push, you can either create a
new instance or update an instance with the latest version.

## Creating Instances

If you want to create a new instance after using `app.push()`, your script might include the following.

```python
latest_version = app.new_version(
    name="v1.2.0",
    id="v1.2.0"
    description="Added new optimization features"
)

# Create a new instance from the latest version
instance = app.new_instance(
    name="Staging Instance",
    version_id=latest_version.id
)

# Or create with custom configuration
config = cloud.InstanceConfiguration(
    secrets_collection_id="staging_secrets",
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

## Updating Instances

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

[version]: ../../reference/cloud/version.md
