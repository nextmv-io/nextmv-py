# Java multi-file Template

This is a template for a Nextmv application with the following characteristics:

* Type: Java
* Content format: `multi-file`. Read/write one or more files from/to disk (a directory).

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

A sample input file is also provided in `inputs/input.json`.

1. Build the app.

    ```bash
    mvn package
    ```

2. Run the app.

    ```bash
    java -jar main.jar --details true
    ```
