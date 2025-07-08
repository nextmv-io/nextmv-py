# Input sets

Input sets are defined sets of input files to use for tests, such as [batch
experiments][batch-experiments] and [acceptance tests][acceptance-tests].

Define the desired input set ID and name. After, create the input set by:

* Referencing the run IDs.

    ```python
    import json
    import os

    from nextmv.cloud import Application, Client

    client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = Application(client=client, id=os.getenv("APP_ID"))
    input_set = app.new_input_set(
        id=os.getenv("INPUT_SET_ID"),
        name=os.getenv("INPUT_SET_ID"),
        description="An optional description",
        run_ids=["latest-RNBs7AKSg", "latest-UlulZAKSR", "latest-fK_wZ0FSg"],
    )
    print(json.dumps(input_set.to_dict(), indent=2))  # Pretty print.
    ```  

    ```json
    {
        "app_id": "routing",
        "created_at": "2024-01-11T17:00:08.190412Z",
        "description": "An optional description",
        "id": "input-set-3",
        "input_ids": [
        "latest-RNBs7AKSg",
        "latest-UlulZAKSR",
        "latest-fK_wZ0FSg"
        ],
        "name": "input-set-3",
        "updated_at": "2024-01-11T17:00:08.190412Z"
    }
    ```  

* Referencing a date range and an instance ID.

    ```python
    import json
    import os
    from datetime import datetime, timezone  

    from nextmv.cloud import Application, Client

    client = Client(api_key=os.getenv("NEXTMV_API_KEY"))
    app = Application(client=client, id=os.getenv("APP_ID"))
    input_set = app.new_input_set(
        id=os.getenv("INPUT_SET_ID"),
        name=os.getenv("INPUT_SET_ID"),
        description="An optional description",
        instance_id=os.getenv("INSTANCE_ID"),
        start_time=datetime(2024, 1, 5, 0, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2024, 1, 5, 23, 59, 59, tzinfo=timezone.utc),
    )
    print(json.dumps(input_set.to_dict(), indent=2))  # Pretty print.
    ```  

    ```json
    {
        "app_id": "routing",
        "created_at": "2024-01-11T17:00:08.190412Z",
        "description": "An optional description",
        "id": "input-set-3",
        "input_ids": [
        "latest-RNBs7AKSg",
        "latest-UlulZAKSR",
        "latest-fK_wZ0FSg"
        ],
        "name": "input-set-3",
        "updated_at": "2024-01-11T17:00:08.190412Z"
    }
    ```  

[batch-experiments]: ./batch-experiments.md
[acceptance-tests]: ./acceptance-tests.md
