# Go multi-file Template

This is a template for a Nextmv application with the following characteristics:

* Type: Binary (Go)
* Content format: `multi-file`. Read/write one or more files from/to disk (a directory).

This is the basic structure:

```text
├── app.yaml
├── main.go
├── go.mod
└── README.md
```

* `app.yaml`: App manifest, containing the configuration to run the app with Nextmv.
* `main.go`: Entrypoint for the app.
* `README.md`: Description of the app.
* `go.mod`: Go module definition for the app.

A sample input file is also provided in `inputs/input.json`.

1. Build the app.

    ```bash
    go build -o main .
    ```

2. Run the app.

    ```bash
    ./main --details true
    ```
