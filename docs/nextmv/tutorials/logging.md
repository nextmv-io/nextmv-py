# Logging

!!! tip "Reference"

    Find the reference for the `logger` module [here](../reference/logger.md).

The Nextmv platform captures logs via `stderr`. Please note that any messages
printed to `stdout` will not be displayed in Nextmv Cloud. Use the provided
functionality to record logs. The `redirect_stdout` function is particularly
useful when you want to redirect `stdout` to `stderr` for logging purposes.
Many solvers and libraries print messages to `stdout`, which can be redirected
to `stderr` for logging.

```python
import sys

import nextmv

print("0. I do nothing")

nextmv.redirect_stdout()

nextmv.log("1. I log a message to stderr")

print("2. I print a message to stdout")

nextmv.reset_stdout()

print("3. I print another message to stdout")

print("4. I print yet another message to stderr without the logger", file=sys.stderr)

nextmv.log("5. I log a message to stderr using the nextmv module directly")

print("6. I print a message to stdout, again")
```

After executing it, here are the messages printed to the different streams.

* `stdout`:

    ```txt
    1. I do nothing
    2. I print another message to stdout
    3. I print a message to stdout, again
    ```

* `stderr`:

    ```txt
    1. I log a message to stderr
    2. I print a message to stdout
    3. I print yet another message to stderr without the logger
    4. I log a message to stderr using the nextmv module directly
    ```
