# Secrets

!!! tip "Reference"

    Find the reference for the `Application` class [here](./reference/application.md).

Secrets collections are a secure mechanism for storing and using sensitive
information such as API keys and license files in your application (decision
model). Secrets collections can be used at these levels:

* Instance: set secrets at the instance level so that all runs that use the
  instance can access the secrets.
* Run: set secrets at the run level so that only the run can access the
  secrets.

To read more about secrets collections, go [to the general
documentation][secrets-collections].

## Create a secrets collection

Start by creating a secrets collection in your Nextmv Application. You can do
this with the `new_secrets_collection` method.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

secrets_collection_summary = app.new_secrets_collection(
    secrets=[
        cloud.Secret(
            secret_type=cloud.SecretType.ENV,
            location="PROVIDER_API_KEY",
            value="super_secret_value",
        ),
        cloud.Secret(
            secret_type=cloud.SecretType.FILE,
            location="PROVIDER_LICENSE_FILE",
            value="super secret\nlicense information\nhere",
        ),
    ],
    id="my-secrets-collection",
    name="My Secrets Collection",
    description="Sensitive secrets for my application",
)


nextmv.write(secrets_collection_summary)
```

There are several things to note about the code above:

* `secrets` (**required**): list of secrets in the collection. Multiple secrets
  can be added to a collection.
  * `secret_type` is the type of secret. It can be `env` (environment variable)
    or `file` (an actual file).
  * `location` is the name/location of the secret. For `env`, this is the name
    of the environment variable. For `file`, this is the name of the file.
  * `value` is the value of the secret. For `env`, this is the value of the
    environment variable. For `file`, this is the content of the file.
* `id` (**required**): ID of the secrets collection. This is a unique
  identifier for the collection.
* `name` (**required**): name of the secrets collection.
* `description` (_optional_): description of the secrets collection.

The object returned is the summary of the secrets collection that was just
created.

```bash
$ python main.py
{
  "id": "my-secrets-collection",
  "application_id": "...",
  "name": "My Secrets Collection",
  "description": "Sensitive secrets for my application",
  "created_at": "2025-04-17T03:57:03Z",
  "updated_at": "2025-04-17T03:57:03Z"
}
```

## Use a secrets collection

There are two ways to use the secrets collection:

* Instance
  * `new_instance`: Create a new instance with the secrets collection.
  * `update_instance`: Update an existing instance with the secrets
      collection.
* Run
  * `new_run`: Create a new run with the secrets collection.
  * `new_run_with_result`: Create a new run with the secrets collection, and
      poll for the result.

Here are two example of using secrets collection with instances: creating and
updating an instance. The `secrets_collection_id` from the previous example is
used. Please note that in these examples, it is assumed that there is a version
with the ID `version-1` previously created. You may create a version with the
`new_version` method.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

instance = app.new_instance(
    version_id="version-1",
    id="instance-1",
    name="My Instance",
    configuration=cloud.InstanceConfiguration(
        secrets_collection_id="my-secrets-collection",
    ),
)

nextmv.write(instance)
```

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

instance = app.update_instance(
    id="instance-1",
    name="My Instance",
    version_id="version-1",
    configuration=cloud.InstanceConfiguration(
        secrets_collection_id="my-secrets-collection",
    ),
)

nextmv.write(instance)
```

Running the code will create (or update) an instance with the secrets
collection attached.

```bash
$ python main.py
{
  "id": "instance-1",
  "application_id": "...",
  "version_id": "version-1",
  "name": "My Instance",
  "description": "",
  "configuration": {
    "execution_class": "6c9500mb870s",
    "secrets_collection_id": "my-secrets-collection"
  },
  "locked": false,
  "created_at": "2025-04-17T05:02:56.745656Z",
  "updated_at": "2025-04-17T05:02:56.745656Z"
}
```

A new run can be executed, either using the `new_run_with_result` or `new_run`
methods, applying the instance shown above.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

result = app.new_run_with_result(input={"foo": "bar"}, instance_id="instance-1")

nextmv.write(result)
```

The other way to use a secrets collection is to attach it to a run directly, as
opposed to using an instance. This is done by using the `secrets_collection_id`
parameter in the `new_run` or `new_run_with_result` methods.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

result = app.new_run_with_result(
    input={"foo": "bar"},
    configuration=cloud.RunConfiguration(
        secrets_collection_id="my-secrets-collection",
    ),
)

nextmv.write(result)
```

```python
import json
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

run_id = app.new_run(
    input={"foo": "bar"},
    configuration=cloud.RunConfiguration(
        secrets_collection_id="my-secrets-collection",
    ),
)

print(run_id)
```

## Manage secrets collections

There are several methods to manage secrets collections. In the following
examples, the same `secrets_collection_id` as before is used. This ID
corresponds to the secrets collection that was created.

Use the `secrets_collection` method to get the details of a secrets collection.
This method returns the secret collection itselg, including the sensitive
information for each secret.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

secrets_collection = app.secrets_collection(secrets_collection_id="my-secrets-collection")

nextmv.write(secrets_collection)
```

```bash
$ python main.py
{
  "id": "my-secrets-collection",
  "application_id": "...",
  "name": "My Secrets Collection",
  "description": "Sensitive secrets for my application",
  "created_at": "2025-04-17T03:57:03Z",
  "updated_at": "2025-04-17T03:57:03Z",
  "secrets": [
    {
      "type": "env",
      "location": "PROVIDER_API_KEY",
      "value": "super_secret_value"
    },
    {
      "type": "file",
      "location": "PROVIDER_LICENSE_FILE",
      "value": "super secret\nlicense information\nhere"
    }
  ]
}
```

Use the `list_secrets_collections` method to list all secrets collections
summaries in the application. This method returns a list of the summaries, so
sensitive information is not displayed.

```python
import json
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

secrets_collections = app.list_secrets_collections()

print(json.dumps([r.to_dict() for r in secrets_collections], indent=2))
```

```bash
$ python main.py
[
  {
    "id": "my-secrets-collection",
    "application_id": "1504",
    "name": "My Secrets Collection",
    "description": "Sensitive secrets for my application",
    "created_at": "2025-04-17T03:57:03Z",
    "updated_at": "2025-04-17T03:57:03Z"
  }
]
```

Use the `update_secrets_collection` method to update a secrets collection. This
method returns the updated secrets collection summary, so the sensitive
information is not displayed.

Please note that the `secrets` parameter, if defined, will overwrite the
existing secrets in the collection. If you want to keep the existing secrets
and add new ones, you need to first get the existing secrets collection, and
then add the new secrets to the list.

```python
import os

import nextmv
from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

secrets_collection_summary = app.update_secrets_collection(
    secrets_collection_id="my-secrets-collection",
    name="A new name for my secrets collection",
    description="A new description for my secrets collection",
    secrets=[
        cloud.Secret(
            secret_type=cloud.SecretType.ENV,
            location="PROVIDER_API_KEY",
            value="a_new_secret_value",
        ),
        cloud.Secret(
            secret_type=cloud.SecretType.FILE,
            location="PROVIDER_LICENSE_FILE",
            value="new secret\nlicense information\nis updated here",
        ),
    ],
)

nextmv.write(secrets_collection_summary)
```

```bash
$ python main.py
{
  "id": "my-secrets-collection",
  "application_id": "1504",
  "name": "A new name for my secrets collection",
  "description": "A new description for my secrets collection",
  "created_at": "2025-04-17T03:57:03Z",
  "updated_at": "2025-04-17T05:29:38Z"
}
```

Lastly, you can delete a secrets collection with the
`delete_secrets_collection` method. No information is returned. This action is
irreversible, so be careful when using it.

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
app = cloud.Application(client=client, id="<YOUR_APP_ID>")

app.delete_secrets_collection(secrets_collection_id="my-secrets-collection")
```

[secrets-collections]: https://docs.nextmv.io/docs/using-nextmv/reference/secret-collections
