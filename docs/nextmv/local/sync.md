# Sync to Cloud

!!! tip "Reference"

    Find the reference for the `local.Application` class [here](./reference/application.md).

The [local Application][local-application] gives you the ability to ease the
transition to [Cloud][cloud-index] by syncing it to a [Cloud
Application][cloud-application].

All your local runs are structured under the `.nextmv` directory of your local
app. The sync process will track all your local runs and push them to your
Cloud application.

To unleash the full potential of Nextmv, let's create a
[`cloud.Application`][cloud-application], and sync our
[`local.Application`][local-application] to that target. With the Cloud app,
you can take full advantage of the Nextmv Platform with features such as:

1. Testing and experimentation
2. Versioning
3. Configuration for operators

---

Let's start by creating a [Cloud application][cloud-application].

```python
import os

from nextmv import cloud

client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
cloud_app = cloud.Application.new(client=client, name="sample-cloud-app", id="sample-cloud-app", exist_ok=True)
```

Now, let's sync our local Application to our cloud Application using the
[`local.Application.sync`][app-sync] method.

```python
from nextmv import local

local_app = local.Application(src="<YOUR_APP_SRC>") # Path to your local app, where the app.yaml manifest is located.
local_app.sync(target=cloud_app, verbose=True) # Set verbose to True to visualize what happens.
```

You should see an output similar to the following:

```bash
☁️ Starting sync of local application `/Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17` to Nextmv Cloud application `sample-cloud-app`.
ℹ️  Found 3 local runs to sync from /Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17/.nextmv/runs.
🔄 Syncing local run `local-75l23gzf`... 
✅ Synced local run `local-75l23gzf` as remote run `devint-CIZjpy3Ng`.
🔄 Syncing local run `local-9881aggf`... 
✅ Synced local run `local-9881aggf` as remote run `devint-OVSjtyqHR`.
🔄 Syncing local run `local-au9xnvbj`... 
✅ Synced local run `local-au9xnvbj` as remote run `devint-D6OCps3Ng`.
🚀 Process completed, synced local application `/Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17` to Nextmv Cloud application `sample-cloud-app`: 3/3 runs.
```

* You can specify the `run_ids` parameter to sync specific runs, as opposed to all
  the runs in your local app.
* You can specify the `instance_id` parameter to sync the runs to a specific
  [instance][instance] of your Cloud application.

What happens when you run the command again?

```bash
☁️ Starting sync of local application `/Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17` to Nextmv Cloud application `sample-cloud-app`.
ℹ️  Found 3 local runs to sync from /Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17/.nextmv/runs.
🔄 Syncing local run `local-75l23gzf`... 
   ⏭️  Skipping local run `local-75l23gzf`, already synced at 2025-10-03T09:14:58.879628+00:00.
🔄 Syncing local run `local-9881aggf`... 
   ⏭️  Skipping local run `local-9881aggf`, already synced at 2025-10-03T09:15:02.777086+00:00.
🔄 Syncing local run `local-au9xnvbj`... 
   ⏭️  Skipping local run `local-au9xnvbj`, already synced at 2025-10-03T09:15:06.868320+00:00.
🚀 Process completed, synced local application `/Users/sebastian-quintero/nextmv/github/nextmv-py/nextmv/app-voo59k17` to Nextmv Cloud application `sample-cloud-app`: 0/3 runs.
```

The SDK recognizes that the runs were already synced, and skips them. The local
Application keeps track of the synced runs, so they are not replicated in
Cloud.

[cloud-index]: ../cloud/index.md
[cloud-application]: ../cloud/reference/application.md
[local-application]: ./reference/application.md
[instance]: ../cloud/instances.md
[app-sync]: ./reference/application.md#nextmv.nextmv.local.application.Application.sync
