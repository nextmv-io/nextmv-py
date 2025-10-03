# Modeling overview

The `nextmv` package, at its root namespace, provides modeling constructs to
work with decision models in an opinionated way. These constructs allow you to
create executable apps that:

1. read an input,
1. solve a decision model, and
1. produce an output.

These functions are entirely optional when working with the Nextmv Platform.
However, they provide useful features to structure your decision models and
follow Nextmv best practices.

In this section you will find the following tutorials encompassing the main
modeling constructs:

| Feature | Description |
|---------|-------------|
| [Options][options] | Define and parse options to configure how your decision model is run |
| [Input][input] | Structure and validate the input data that your decision model will use |
| [Logging][logging] | Log messages to understand how your decision model is running |
| [Output][output] | Structure the output that your decision model produces |
| [Model][model] | Use the `nextmv.Model` class to create decision models in an opinionated way |

[options]: ./options.md
[input]: ./input.md
[logging]: ./logging.md
[output]: ./output.md
[model]: ./model.md
