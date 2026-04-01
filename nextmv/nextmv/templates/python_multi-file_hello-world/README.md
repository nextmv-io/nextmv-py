# Python multi-file Template

This is a template for a Nextmv application with the following characteristics:

* Type: Python
* Content format: `multi-file`. Read/write one or more files from/to disk (a directory).

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

A sample input file is also provided in `inputs/input.json`.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app.

    ```bash
    python main.py --details true
    ```
