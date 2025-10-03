# Manage Versions for an Application

!!! tip "Reference"

    Find the reference for the `Application` class [here](./reference/application.md).

Application versions allow you to preserve and manage different iterations of your application.
This is useful for rollbacks, testing different versions, or maintaining stable releases while
developing new features.

## Understanding Versions

A Nextmv Cloud Application Version refers to a specific executable created from
a pushed application. The underlying executable is immutable and can be
configured to run in an [instance][instance].

When you [push][push] an application, the executable is stored in a development
instance. Subsequent pushes overwrite this executable. Creating a version
preserves a copy of the current executable, allowing you to maintain multiple
stable versions.

## Creating Versions

You can automatically create a version after pushing:

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

# Push the application
app.push()

# Create a new version with an auto-generated ID
app.new_version(
    name="My new version"
)

# Or with additional metadata
app.new_version(
    name="Production Release v1.2.0",
    description="Added new optimization features"
)
```

[instance]: ./instances.md
[push]: ./push.md
