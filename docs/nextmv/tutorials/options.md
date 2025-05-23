# Options

!!! tip "Reference"

    Find the reference for the `options` module [here](../reference/options.md).

Use options to capture parameters (i.e.: configurations) for the run.

Consider the following script:

```python
import nextmv

options = nextmv.Options(
    nextmv.Option("str_option", str, "default value", "A string option", required=True),
    nextmv.Option("int_option", int, 1, "An int option", required=False),
    nextmv.Option("float_option", float, 1.0, "A float option", required=False),
    nextmv.Option("bool_option", bool, True, "A bool option", required=True),
)

# Options can be accessed as attributes.
print(options.str_option)
print(options.int_option)
print(options.float_option)
print(options.bool_option)
print(options.to_dict())
```

By using options, you are able to pass in the values with CLI arguments or
environment variables. Run the script, providing the required arguments.

```bash
$ python main.py --str_option foo --bool_option false
foo
1
1.0
False
{'str_option': 'foo', 'int_option': 1, 'float_option': 1.0, 'bool_option': False}
```

At any moment, you may summon the help message to see the available options.

```bash
$ python main.py --help
usage: main.py [options]

Options for main2.py. Use command-line arguments (highest precedence) or
environment variables.

options:
  -h, --help            show this help message and exit
  -str_option STR_OPTION, --str_option STR_OPTION
                        [env var: STR_OPTION] (required) (default: default
                        value) (type: str): A string option
  -int_option INT_OPTION, --int_option INT_OPTION
                        [env var: INT_OPTION] (default: 1) (type: int): An int
                        option
  -float_option FLOAT_OPTION, --float_option FLOAT_OPTION
                        [env var: FLOAT_OPTION] (default: 1.0) (type: float):
                        A float option
  -bool_option BOOL_OPTION, --bool_option BOOL_OPTION
                        [env var: BOOL_OPTION] (required) (default: True)
                        (type: bool): A bool option

```

You can merge options together to create a new set of options.

```python
import nextmv

options1 = nextmv.Options(
    nextmv.Option("str_option1", str, "default value", "A string option", required=True),
    nextmv.Option("int_option1", int, 1, "An int option", required=False),
    nextmv.Option("float_option1", float, 1.0, "A float option", required=False),
    nextmv.Option("bool_option1", bool, True, "A bool option", required=True),
)

options2 = nextmv.Options(
    nextmv.Option("str_option2", str, "default value", "A string option", required=True),
    nextmv.Option("int_option2", int, 1, "An int option", required=False),
    nextmv.Option("float_option2", float, 1.0, "A float option", required=False),
    nextmv.Option("bool_option2", bool, True, "A bool option", required=True),
)

options = options1.merge(options2)

print(options.str_option1)
print(options.int_option1)
print(options.float_option1)
print(options.bool_option1)
print(options.str_option2)
print(options.int_option2)
print(options.float_option2)
print(options.bool_option2)
print(options.to_dict())

```

```bash
$ python main.py --str_option1 foo --bool_option1 false --str_option2 bar --bool_option2 true
foo
1
1.0
False
bar
1
1.0
True
{'str_option1': 'foo', 'int_option1': 1, 'float_option1': 1.0, 'bool_option1': False, 'str_option2': 'bar', 'int_option2': 1, 'float_option2': 1.0, 'bool_option2': True}
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main2.py. Use command-line arguments (highest precedence) or environment variables.

options:
  -h, --help            show this help message and exit
  -str_option1 STR_OPTION1, --str_option1 STR_OPTION1
                        [env var: STR_OPTION1] (required) (default: default value) (type: str): A string option
  -int_option1 INT_OPTION1, --int_option1 INT_OPTION1
                        [env var: INT_OPTION1] (default: 1) (type: int): An int option
  -float_option1 FLOAT_OPTION1, --float_option1 FLOAT_OPTION1
                        [env var: FLOAT_OPTION1] (default: 1.0) (type: float): A float option
  -bool_option1 BOOL_OPTION1, --bool_option1 BOOL_OPTION1
                        [env var: BOOL_OPTION1] (required) (default: True) (type: bool): A bool option
  -str_option2 STR_OPTION2, --str_option2 STR_OPTION2
                        [env var: STR_OPTION2] (required) (default: default value) (type: str): A string option
  -int_option2 INT_OPTION2, --int_option2 INT_OPTION2
                        [env var: INT_OPTION2] (default: 1) (type: int): An int option
  -float_option2 FLOAT_OPTION2, --float_option2 FLOAT_OPTION2
                        [env var: FLOAT_OPTION2] (default: 1.0) (type: float): A float option
  -bool_option2 BOOL_OPTION2, --bool_option2 BOOL_OPTION2
                        [env var: BOOL_OPTION2] (required) (default: True) (type: bool): A bool option
```

Please note that merging the options will also `parse` them. Once options have
been parsed, they cannot be merged with other options. You may also parse the
options manually using the `.parse()` method.
