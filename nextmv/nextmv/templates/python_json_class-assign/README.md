# Python Class Assignment Template

This is a template for a Nextmv application that solves a school class
assignment problem using mixed-integer programming (MIP) with Pyomo. It has the
following characteristics:

* Type: Python
* Content format: `json`, utf-8 encoded. JSON is read from stdin
  and written to stdout.

This is the basic structure:

```text
├── app.yaml
├── main.py
├── README.md
├── requirements.txt
└── visualizations.py
```

* `app.yaml`: App manifest, containing the configuration to run the app with Nextmv.
* `main.py`: Entrypoint for the app. Loads input data, solves the assignment
  problem, and writes the output.
* `README.md`: Description of the app.
* `requirements.txt`: Python dependencies for the app.
* `visualizations.py`: Generates visual assets from the solution.

A sample input file is also provided as `input.json`. It contains students
(with preferences, priority, class level, and optional extended-day requests)
and classes to assign them to.

1. Install packages.

    ```bash
    pip install -r requirements.txt
    ```

2. Run the app. Options can be omitted and will default to the values specified
   in `app.yaml`.

    ```bash
    cat input.json | python main.py \
        --duration 30 \
        --solver highs \
        --extended_day_time 17 \
        --extended_day_bonus 2.0 \
        --extended_day_penalty 0.5
    ```
