# Java json Template

This is a template for a Nextmv application with the following characteristics:

* Type: Java
* Content format: `json`, utf-8 encoded. JSON is read from stdin
  and written to stdout.

This is the basic structure:

```text
├── app.yaml
├── pom.xml
├── Main.java
└── README.md
```

* `app.yaml`: App manifest, containing the configuration to run the app with Nextmv.
* `pom.xml`: Maven project definition for the app.
* `Main.java`: Entrypoint for the app.
* `README.md`: Description of the app.

A sample input file is also provided as `input.json`.

1. Build the app.

    ```bash
    mvn package
    ```

2. Run the app.

    ```bash
    cat input.json | java -jar main.jar --details true
    ```
