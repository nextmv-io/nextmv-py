# Python json Template

This is a template for a Nextmv application with the following characteristics:

* Type: Python
* Content format: `json`, utf-8 encoded. JSON is read from stdin
  and written to stdout.

This is the basic structure:

```text
├── app.yaml
├── main.py
├── README.md
└── requirements.txt
```

* `app.yaml`: App manifest, containing the configuration to run the app with Nextmv.
* `main.py`: Entrypoint for the app.
* `README.md`: Description of the app.
* `requirements.txt`: Python dependencies for the app.

A sample input file is also provided as `input.json`.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app.

    ```bash
    cat input.json | python main.py --details true
    ```
