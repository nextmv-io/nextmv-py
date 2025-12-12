# Nextmv application

This is the basic structure of a Nextmv application.

```text
├── app.yaml
├── main.py
├── README.md
├── requirements.txt
└── src
```

* `app.yaml`: App manifest, containing the configuration to run the app
  remotely on Nextmv Cloud.
* `main.py`: Entry point for the app.
* `README.md`: Description of the app.
* `requirements.txt`: Python dependencies for the app.
* `src/`: Source code for the app.

A sample input file is also provided as `input.json`.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app.

    ```bash
    cat input.json | python main.py
    ```
