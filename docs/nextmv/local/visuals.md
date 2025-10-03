# Run visuals

If your local app produces visual assets as part of its output, you can view
them using the [`Application.run_visuals`][app-run-visuals] method.

```python
from nextmv import local

app = local.Application(src="<YOUR_APP_SRC>") # Path to your local app, where the app.yaml manifest is located.
app.run_visuals(run_id="<YOUR_RUN_ID>") # The ID of the run you want to visualize.
```

This will open a web browser tab with the visual assets produced by the run. If
your app does not produce any visual assets, this method will do nothing.

The visual assets are typically `.html` files stored under the
`.nextmv/runs/<RUN_ID>/visuals` directory of your local app. One browser tab
will be opened for each visual asset produced in that run.

These run visuals are similar to the ones produced by the Nextmv Console, so
you can use this method to preview the visuals locally before pushing your app
to Nextmv Cloud.

[app-run-visuals]: ./reference/application.md#nextmv.nextmv.local.application.Application.run_visuals
