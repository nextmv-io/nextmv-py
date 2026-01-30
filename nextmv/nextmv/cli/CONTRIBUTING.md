# Contributing to Nextmv CLI

Hello dear contributor. Thank you for helping out with the CLI 😎. Here are a
few style guidelines to help all of us maintain a high-quality tool, that feels
unified and consistent. You are required to read and understand these
guidelines before submitting a pull request.

The Nextmv CLI is built using [Typer][typer]. If you don't know Typer, we
_strongly encourage_ you to read through the [Typer Learn][typer-learn]
section to understand what is possible with the library. Even if you decide not
to run the example commands, you should spend 1 - 2 hours reading through the
material to get a good understanding of how Typer works.

We are following Typer's recommendations and using [Rich][rich] for formatting.
We also _strongly encourage_ you to read though Rich's documentation, spending
30 minutes to an hour familiarizing yourself with the library. Quoting directly
from the Typer docs:

> If you are wondering what tool should be used for what, Typer is useful for
> structuring the command line application, with options, arguments,
> subcommands, data validation, etc.
>
> In general, Typer tends to be the entry point to your program, taking the
> first input from the user.
>
> Rich is useful for the parts that need to display information. Showing
> beautiful content on the screen.
>
> The best results for your command line application would be achieved
> combining both Typer and Rich.

## Command structure

The logic for command tree organization is based on:

> Domain > Entity > Action

Where:

- Domain separates `cloud` from `local`. If there is no domain, the command
  belongs to the root command tree.
- Entity refers to resources like `run`, `batch-experiment`,
  `secrets-collection`, etc.
- Action details what can be done on the entity: `create`, `get`, `delete`,
  `list`, etc.
- Sometimes, it is not practical to follow this logic. Consider the `nextmv
  cloud run` command tree. The available subcommands are:

  - cancel: Cancel a queued/running Nextmv Cloud application run.
  - create: Create a new Nextmv Cloud application run.
  - get: Get the result (output) of a Nextmv Cloud application run.
  - input: Get the input of a Nextmv Cloud application run.
  - list: Get the list of runs for a Nextmv Cloud application.
  - logs: Get the logs of a Nextmv Cloud application run.
  - metadata: Get the metadata of a Nextmv Cloud application run.
  - track: Track an external run as a Nextmv Cloud application run.
  
  Strictly speaking, `input`, `logs`, and `metadata` are not actions. To avoid
  defining a `nextmv cloud run input get` command, which starts getting
  convoluted, we decided to keep these commands as-is. On the other hand, if
  you have the need to define commands like `nextmv cloud run input-update`, or
  `nextmv cloud run input-delete`, then it is better to define a `nextmv cloud run
  input` command tree, with `get`, `update`, and `delete` subcommands.

- If possible, use single words for command trees and commands.
- Use the best judgement when deciding how to structure commands. If you
  believe a different structure makes more sense, feel free to propose it in
  your pull request, explaining the reasoning behind it.

## File organization

Follow these guidelines when organizing files and directories for commands:

- Directories and files should be named following the command names. For
  example, the `cloud` directory has the `cloud` command tree, and the
  `cloud/app/create.py` file contains the `nextmv cloud app create` command.
- Place commands in their own Python files. Take the `community` dir, for
  example. The `clone.py` file hosts the `nextmv community clone` command and
  the `list.py` file has the `nextmv community list` command.
- Place command trees in their own directories. The main command of the command
  tree should live in the `__init__.py` file in the directory. Consider the
  `cloud/app` directory. The `__init__.py` file has the following code, which
  sets up the `nextmv cloud app` command tree and adds seven subcommands to
  it.

  ```python
  import typer

  from nextmv.cli.cloud.app.create import app as create_app
  from nextmv.cli.cloud.app.delete import app as delete_app
  from nextmv.cli.cloud.app.exists import app as exists_app
  from nextmv.cli.cloud.app.get import app as get_app
  from nextmv.cli.cloud.app.list import app as list_app
  from nextmv.cli.cloud.app.push import app as push_app
  from nextmv.cli.cloud.app.update import app as update_app

  # Set up subcommand application.
  app = typer.Typer()
  app.add_typer(create_app)
  app.add_typer(delete_app)
  app.add_typer(exists_app)
  app.add_typer(get_app)
  app.add_typer(list_app)
  app.add_typer(push_app)
  app.add_typer(update_app)


  @app.callback()
  def callback() -> None:
      """
      Create, manage, and push Nextmv Cloud applications.
      """
      pass
  ```

  Each of the commands should be in their own file in the same directory, e.g.
  `create.py`, `delete.py`, etc.

- Use the same principle of placing command tree definitions in an
  `__init__.py` file for subcommand trees as well. Consider the `cloud`
  directory. It has an `__init__.py` file and subdirectories. The `__init__.py`
  file has the following code, which sets up the `nextmv cloud` command tree
  and adds several subcommand trees to it.

  ```python
  import typer

  from nextmv.cli.cloud.app import app as app_app
  from nextmv.cli.cloud.run import app as run_app

  # Set up subcommand application.
  app = typer.Typer()
  app.add_typer(app_app, name="app")
  app.add_typer(run_app, name="run")


  @app.callback()
  def callback() -> None:
      """
      Interact with Nextmv Cloud, a platform for deploying and managing models.
      """
      pass
  ```

## Printing

When information to the user, i.e., printing to the console, follow these
guidelines:

- Unless otherwise necessary, always print and log to `stderr`. This ensures
  that the CLI's output can be piped and redirected without issues.
- We embrace the use of emojis. They make the CLI friendlier and more
  approachable.
- The `message.py` file contains helper functions for printing messages, like:
  - `message`: prints a message. You can give it an emoji for the message. The
    other commands have fixed emojis.
  - `info`: prints an informational message. Use for neutral messages.
  - `in_progress`: prints an in-progress message. Use before executing an action.
  - `success`: prints a success message. Use after successfully completing an action.
  - `warning`: prints a warning message. Use for non-critical issues.
  - `error`: prints an error and raises an exception. Use for critical issues
    and to return early from commands.
- For printing `JSON` information, use the `print_json` function in the
  `message.py` file to print JSON output. This ensures consistent formatting
  across the CLI.
- Emojis should be formatted according to [Rich's emoji guide][rich-emoji].
  They are strings enclosed in colons, e.g. `:rocket:`, `:boom:`,
  `:hourglass_flowing_sand:`, etc.
- When using the `success` function, include the variable or entity that was
  affected, formatted with `[magenta]`:

  ```python
  success(f"Application [magenta]{app_id}[/magenta] deleted successfully.")
  ```

- When showing the values of an `Enum`, use the `enum_values` function in the
  `message.py` file which will give a nicely colored, comma-separated list of
  the enum values. Consider the following example, where we get the allowed
  values for the `InputFormat` class.

  ```python
      content_format: Annotated[
        InputFormat | None,
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format for the instance. Allowed values are: {enum_values(InputFormat)}.",
            metavar="CONTENT_FORMAT",
            rich_help_panel="Instance configuration",
        ),
    ] = None,
  ```

## Confirmation prompts

For destructive actions (like deletions), use the `get_confirmation()` method
to ask for user confirmation before proceeding. The method is available from
the `cli/confirm.py` file. This method already handles sensible values used for
getting a confirmation from a user. Additionally, it handles non-interactive
sessions by defaulting to `False` if no input can be provided.

When using confirmation prompts, follow these guidelines:

- The confirmation message should use `[magenta]` for the variable/s being
  affected.
- Provide a `--yes` / `-y` flag to skip the confirmation prompt where possible,
  useful for non-interactive sessions.
- If the user declines, call `info()` and return early.

Consider the `nextmv cloud app delete` command:

```python
if not yes:
    confirm = get_confirmation(
        f"Are you sure you want to delete application [magenta]{app_id}[/magenta]? This action cannot be undone.",
    )

    if not confirm:
        info(f"Application [magenta]{app_id}[/magenta] will not be deleted.")
        return
```

## Formatting, colors, and styles

Use these Rich markup colors/styles when formatting help text and messages.
These are the main colors/styles that can be used for highlighting/contrast (we
limit colors to keep coloring consistent):

- `[code]`: commands. CLI related variables. - technical things that are CLI
  commands.
- `[magenta]`: variable names, values, literals, etc. - mainly short technical things.
- `[dim]`: examples. - longer technical things.
- `[yellow]`: emphasis, highlight of special items, type contrast to
  `[magenta]`. Use sparingly only.

In any case, the best advice is to follow existing examples in the codebase to
maintain consistency.

Here are some guidelines for when to use each formatting style.

- When talking about a command use the `[code]` `[/code]` tags. Consider the
  help message of the `cloud/shadow/stop.py` file. We tell the user they can
  delete an experiment with the `nextmv cloud shadow delete` command. The
  formatting of that command is done using the `[code]` `[/code]` tags:

  ```python
  @app.command()
  def stop(
      app_id: AppIDOption,
      shadow_test_id: ShadowTestIDOption,
      profile: ProfileOption = None,
  ) -> None:
      """
      Stops a Nextmv Cloud shadow test.

      Before stopping a shadow test, it must be in a started state. Experiments
      in a [magenta]draft[/magenta] state, that haven't started, can be deleted
      with the [code]nextmv cloud shadow delete[/code] command.

      [bold][underline]Examples[/underline][/bold]

      - Stop the shadow test with the ID [magenta]hop-analysis[/magenta] from application
        [magenta]hare-app[/magenta].
          $ [dim]nextmv cloud shadow stop --app-id hare-app --shadow-test-id hop-analysis[/dim]
      """

      in_progress(msg="Stopping shadow test...")
      cloud_app = build_app(app_id=app_id, profile=profile)
      cloud_app.stop_shadow_test(shadow_test_id=shadow_test_id)
      success(
          f"Shadow test [magenta]{shadow_test_id}[/magenta] stopped successfully "
          f"in application [magenta]{app_id}[/magenta]."
      )
  ```

- When talking about a command option, there is no formatting needed. Typer
  automatically adds coloring to options in the help menu. Take this example
  from the help menu of the `cloud/app/delete.py` file. In the command help,
  when referring to the `--yes` option:

  ```python
  @app.command()
  def delete(
      app_id: AppIDOption,
      yes: Annotated[
          bool,
          typer.Option(
              "--yes",
              "-y",
              help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
          ),
      ] = False,
      profile: ProfileOption = None,
  ) -> None:
      """
      Deletes a Nextmv Cloud application.

      This action is permanent and cannot be undone. Use the --yes
      flag to skip the confirmation prompt.

      [bold][underline]Examples[/underline][/bold]

      - Delete the application with the ID [magenta]hare-app[/magenta].
          $ [dim]nextmv cloud app delete --app-id hare-app[/dim]

      - Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.
          $ [dim]nextmv cloud app delete --app-id hare-app --yes[/dim]
      """
  ```

- When talking about a variable (like a filepath, value of an option, a string,
  etc.), use the `[magenta]` `[/magenta]` tags. Using the same example as
  above, when referring to the application ID `hare-app`, we use
  `[magenta]hare-app[/magenta]` to format it as a variable. Another example is
  when providing error messages that include values:

  ```python
  error(f"Input path [magenta]{input}[/magenta] does not exist.")
  ```

- When talking about longer technical things, like examples for a command
  usage, or examples of a JSON object, use the `[dim]` `[/dim]` tags. Consider
  the examples section of the `cloud/app/delete.py` file above. The example
  commands are formatted using the `[dim]` `[/dim]` tags. The `[dim]` tag is
  discussed in more detail in the command documentation section below.

- Links to URLs should be formatted using the `[link=URL_LINK][bold]
  [/bold][/link]` tags. Consider the main help message of the `nextmv
  community` command, in the `community/__init__.py` file:

  ```python
  @app.callback()
  def callback() -> None:
      """
      Interact with community apps, which are pre-built decision models.

      Community apps are maintained in the following GitHub repository:
      [link=https://github.com/nextmv-io/community-apps][bold]nextmv-io/community-apps[/bold][/link].
      """
      pass
  ```

  The link provided is <https://github.com/nextmv-io/community-apps>, and it will
  be applied to the text `nextmv-io/community-apps`.

## Command documentation

Every command should have good-enough documentation that guides the user on how
to use it.

- Document every command using Python docstrings.
- Document every option and argument using the `help` parameter of the
  `typer.Option` functions.
- Option documentation should be short and to the point. Avoid long
  explanations. If necessary, you can add more detailed information in the
  command's help.
- The help of the command should be structured as follows:
  - A short, one-line description of what the command does.
  - A blank line.
  - A more detailed description of what the command does. This can be multiple
    paragraphs. Only add this section if necessary.
  - A blank line.
  - An Examples section, with one or more examples of how to use the command.
    Each example should have a short description of what it does, followed by
    the command itself. More on example formatting below.
- Consider the `nextmv cloud app get` command, under the `cloud/app/get.py` file:
  
  ```python
  @app.command()
  def get(
      app_id: AppIDOption,
      output: Annotated[
          str | None,
          typer.Option(
              "--output",
              "-o",
              help="Saves the app information to this location.",
              metavar="OUTPUT_PATH",
          ),
      ] = None,
      profile: ProfileOption = None,
  ) -> None:
      """
      Get a Nextmv Cloud application.

      This command is useful to get the attributes of an existing Nextmv Cloud
      application by its ID.

      [bold][underline]Examples[/underline][/bold]

      - Get the application with the ID [magenta]hare-app[/magenta].
          $ [dim]nextmv cloud app get --app-id hare-app[/dim]

      - Get the application with the ID [magenta]hare-app[/magenta] and save the information to an
        [magenta]app.json[/magenta] file.
          $ [dim]nextmv cloud app get --app-id hare-app --output app.json[/dim]
      """

      client = build_client(profile)
      in_progress("Getting application...")

      cloud_app = Application.get(
          client=client,
          id=app_id,
      )
      cloud_app_dict = cloud_app.to_dict()

      if output is not None and output != "":
          with open(output, "w") as f:
              json.dump(cloud_app_dict, f, indent=2)

          success(f"Application information saved to [magenta]{output}[/magenta].")

          return

      print_json(cloud_app_dict)
  ```

  - The short description is: `Get a Nextmv Cloud application.`
  - The detailed description is:

    ```text
    This command is useful to get the attributes of an existing Nextmv Cloud
    application by its ID.
    ```

  - The examples section is fenced with the `[bold][underline]
    [/underline][/bold]` tags.
  - Each example is listed as a bullet, using a hyphen (`-`).
  - Each example has a short description, followed by the command itself in a
    new line, with 4 spaces of indentation in comparison to where the hyphen is.
  - The command itself should be formatted using the `[dim]` `[/dim]` tags.
  - The command should start with a dollar sign (`$`), followed by a space, and
    then the actual command.
  - When an example command is too long, use a double backslash (`\\`) for line
    continuation. It gets rendered as a single backslash. The next line should
    have 4 additional spaces of indentation (8 spaces total from the hyphen):

    ```text
    - Create an application with an ID and description.
        $ [dim]nextmv cloud app create --name "Hare App" --app-id hare-app \\
            --description "An application for routing hares"[/dim]
    ```

## Command options

Consider the following guideline when declaring command options:

- We _only_ use command options, we _do not_ use command arguments.
- Use the `Annotated` type hint from the `typing_extensions` module to declare
  options. Consider the `name` option from the `nextmv cloud app create`
  command hosted in the `cloud/app/create.py` file:

  ```python
  name: Annotated[
    str,
    typer.Option(
        "--name",
        "-n",
        help="A name for the application.",
        metavar="NAME",
    ),
  ],
  ```

  The type of the option is `str`, and we use `typer.Option` to declare the
  option's properties.

- If possible, provide both a long and short version of the option. In the example
  above, the long version is `--name` and the short version is `-n`.
- Always provide a `help` parameter that describes what the option does. Avoid
  long-winded explanations here, keep it short and to the point. If you need to
  provide more context about using the option, add that information to the
  command's help docstring.
- For `str` options, always provide a `metavar` parameter for describing the
  expected value. In the example above, the `metavar` is `NAME`, indicating
  that the option expects a name string.
- _Optional_ options are declared using the `| None` type hint and normally
  have a default value of `None`. Consider the `default_instance_id` option of
  the same command:

  ```python
  default_instance_id: Annotated[
      str | None,
      typer.Option(
          "--default-instance-id",
          "-i",
          help="An optional default instance ID for the application.",
          metavar="DEFAULT_INSTANCE_ID",
      ),
  ] = None,
  ```
  
  The type hint is `str | None`, and the default value is `None`.

- For `bool` options, always provide at least the long name, to avoid the
  auto-populated `--no-...` version of the option, given by Typer.
- `bool` options should have a default value of either `True` or `False`.
- Use the `rich_help_panel` to organize commands that have a large number of
  options. Consider the `input` option of the `nextmv cloud run create`
  command, hosted in the `cloud/run/create.py` file:

  ```python
  input: Annotated[
      str | None,
      typer.Option(
          "--input",
          "-i",
          help="The input path to use. File or directory depending on content format. "
          "Uses [magenta]stdin[/magenta] if not defined.",
          metavar="INPUT_PATH",
          rich_help_panel="Input control",
      ),
  ] = None,
  ```

  The `rich_help_panel` parameter is set to `Input control`, which groups
  this option under the `Input control` panel in the command's help message.

- When an option can be set via an environment variable, use the `envvar`
  parameter. Environment variable names should follow the `NEXTMV_<OPTION_NAME>`
  convention, e.g. `NEXTMV_PROFILE`, `NEXTMV_API_KEY`, `NEXTMV_APP_ID`,
  `NEXTMV_RUN_ID`.
- Place widely-used options in the `options.py` file, and import them into commands
  that need them. Consider the `profile` option, which is used
  in many `nextmv cloud` commands. It is defined in the `options.py` file:

  ```python
  # profile option - can be used in any command to specify which profile to use.
  # Define it as follows in commands or callbacks, as necessary:
  # profile: ProfileOption = None
  ProfileOption = Annotated[
      str | None,
      typer.Option(
          "--profile",
          "-p",
          help="Profile to use for this action. Use [code]nextmv configuration[/code] to manage profiles.",
          envvar="NEXTMV_PROFILE",
          metavar="PROFILE_NAME",
      ),
  ]
  ```

  Then, in commands that need these options, simply import them and use them
  as needed. Consider the `nextmv cloud app list` command, in the `cloud/app/list.py`
  file:

  ```python
  @app.command()
  def list(
      output: Annotated[
          str | None,
          typer.Option(
              "--output",
              "-o",
              help="Saves the app list information to this location.",
              metavar="OUTPUT_PATH",
          ),
      ] = None,
      profile: ProfileOption = None,
  ) -> None:
  ```

  The `profile` option's type is `ProfileOption`, which is imported from the
  `options.py` file.

- If a command outputs `JSON` content, try to always provide an `output` option
  to allow the user to save the output to a file. Consider the `nextmv cloud
  app list` command again. It has an `output` option that allows the user to
  save the list of applications to a file.
- Always order command options alphabetically. Required options (without
  default values) should be listed first, in alphabetical order. Optional
  options (with default values) should follow, also in alphabetical order. When
  using `rich_help_panel` to group options, maintain alphabetical order within
  each panel. This ensures consistency across the CLI and makes it easier to
  locate options in the code. An exception for this is the `profile` option, which
  should always be the last option in the command's signature, for consistency
  across the CLI.

[typer]: https://typer.tiangolo.com
[typer-learn]: https://typer.tiangolo.com/tutorial/
[rich]: https://rich.readthedocs.io/en/stable/
[rich-emoji]: https://rich.readthedocs.io/en/latest/markup.html#emoji
