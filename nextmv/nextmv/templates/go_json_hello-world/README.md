# Go json Template

This is a template for a Nextmv application with the following characteristics:

* Type: Go
* Content format: `json`, utf-8 encoded. JSON is read from stdin
  and written to stdout.

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

A sample input file is also provided as `input.json`.

1. Build the app.

    ```bash
    go build -o main .
    ```

2. Run the app.

    ```bash
    cat input.json | ./main --details true
    ```
