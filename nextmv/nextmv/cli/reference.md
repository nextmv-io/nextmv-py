# CLI

The Nextmv Command Line Interface (CLI).

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show the current version of the Nextmv CLI.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

[dim]
---

[italic]:rabbit: Made by Nextmv with :heart:[/italic][/dim]

**Commands**:

* `auth`: Authenticate and manage login sessions.
* `cache`: Manage the cache used for Nextmv operations.
* `cloud`: Interact with Nextmv Cloud, a platform for...
* `community`: Interact with community apps, which are...
* `configuration`: Configure the CLI and manage profiles.
* `init`: Get started with the Nextmv CLI.
* `local`: Interact with local Nextmv apps and make...
* `manifest`: Manage <span style="color: #800080; text-decoration-color: #800080">app.yaml</span> (app...
* `version`: Show the current version of the Nextmv CLI.
* `mcp`: Model Context Protocol (MCP) server for...

## `auth`

Authenticate and manage login sessions.

**Usage**:

```console
$ auth [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `login`: Log in to Nextmv using the browser-based...
* `logout`: Log out of Nextmv and delete stored access...

### `auth login`

Log in to Nextmv using the browser-based PKCE auth flow.

Opens your browser, completes the OAuth2 PKCE flow, and stores the
resulting tokens under <span style="color: #800080; text-decoration-color: #800080">~/.nextmv/auth/</span>.

If --profile is given, only that profile is logged in (it must be configured
with <span style="font-weight: bold">--auth-type pkce</span> via <span style="font-weight: bold">nextmv configuration create</span>).
If no profile is given, all <span style="color: #800080; text-decoration-color: #800080">pkce</span> profiles found in
<span style="color: #800080; text-decoration-color: #800080">~/.nextmv/config.yaml</span> are logged in sequentially.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Log in with the default auth profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv auth login</span>

- Log in with a specific named profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv auth login --profile my-auth-profile</span>

- Force re-authentication, bypassing any active browser session.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv auth login --force</span>

**Usage**:

```console
$ auth login [OPTIONS]
```

**Options**:

* `-f, --force`: Force re-authentication even if an active browser session exists. Opens the identity provider&#x27;s logout endpoint first to clear any existing session before starting the login flow.
* `-p, --profile PROFILE_NAME`: Profile to log in to. If omitted, all pkce profiles are logged in.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `auth logout`

Log out of Nextmv and delete stored access tokens.

Deletes the token file for the auth session associated with each
<span style="color: #800080; text-decoration-color: #800080">pkce</span> profile.  Multiple profiles sharing the same
auth session are logged out together (tokens are stored per session,
not per profile).

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Log out of all pkce profiles.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv auth logout</span>

- Log out of a specific named profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv auth logout --profile my-auth-profile</span>

**Usage**:

```console
$ auth logout [OPTIONS]
```

**Options**:

* `-p, --profile PROFILE_NAME`: Profile to log out of. If omitted, all pkce profiles are logged out.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

## `cache`

Manage the cache used for Nextmv operations.

**Usage**:

```console
$ cache [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Deletes the Nextmv cache and resets it to...
* `get`: Gets general information about the Nextmv...

### `cache delete`

Deletes the Nextmv cache and resets it to an empty state.

This action is permanent and cannot be undone. Use the --yes flag to skip
the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the Nextmv cache.
    
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cache delete</span>

- Delete the Nextmv cache without confirmation prompt.
    
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cache delete --yes</span>

**Usage**:

```console
$ cache delete [OPTIONS]
```

**Options**:

* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

### `cache get`

Gets general information about the Nextmv cache.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get cache information.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cache get</span>

**Usage**:

```console
$ cache get [OPTIONS]
```

**Options**:

* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

## `cloud`

Interact with Nextmv Cloud, a platform for deploying and managing decision models.

**Usage**:

```console
$ cloud [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `acceptance`: Create and manage Nextmv Cloud acceptance...
* `account`: Manage your Nextmv Cloud account...
* `app`: Create, manage, and push Nextmv Cloud...
* `batch`: Create and manage Nextmv Cloud batch...
* `data`: Upload data for Nextmv Cloud application...
* `ensemble`: Create and manage Nextmv Cloud ensemble...
* `input-set`: Create and manage Nextmv Cloud input sets.
* `instance`: Create and manage Nextmv Cloud application...
* `managed-input`: Create and handle managed inputs for...
* `marketplace`: Interact with the Nextmv Marketplace.
* `run`: Create and manage Nextmv Cloud application...
* `scenario`: Create and manage Nextmv Cloud scenario...
* `secrets`: Create and manage Nextmv Cloud secrets...
* `shadow`: Create and manage Nextmv Cloud shadow tests.
* `sso`: Manage SSO for your Nextmv Cloud...
* `switchback`: Create and manage Nextmv Cloud switchback...
* `upload`: Create temporary upload URLs for Nextmv...
* `version`: Create and manage Nextmv Cloud application...

### `cloud acceptance`

Create and manage Nextmv Cloud acceptance tests.

**Usage**:

```console
$ cloud acceptance [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud acceptance test.
* `delete`: Deletes a Nextmv Cloud acceptance test.
* `get`: Get a Nextmv Cloud acceptance test.
* `list`: List all Nextmv Cloud acceptance tests for...
* `update`: Update a Nextmv Cloud acceptance test.

#### `cloud acceptance create`

Create a new Nextmv Cloud acceptance test.

The acceptance test is based on a batch experiment. If the batch experiment
with the same ID already exists, it will be reused. Otherwise, you must
provide the --input-set-id option to create a new batch experiment.

Use the --wait flag to wait for the acceptance test to complete, polling
for results. Using the --output flag will also activate waiting, and allows
you to specify a destination file for the results.

<span style="font-weight: bold; text-decoration: underline">Metrics</span>

Metrics are provided as <span style="color: #800080; text-decoration-color: #800080">json</span> objects using the
--metrics flag. Each metric defines how to compare the
candidate and baseline instances.

You can provide metrics in three ways:
- A single metric as a <span style="color: #800080; text-decoration-color: #800080">json</span> object.
- Multiple metrics by repeating the --metrics flag.
- Multiple metrics as a <span style="color: #800080; text-decoration-color: #800080">json</span> array in a single --metrics flag.

Each metric must have the following fields:
- <span style="color: #800080; text-decoration-color: #800080">field</span>: Field of the metric to measure (e.g., &quot;result.custom.unassigned&quot;).
- <span style="color: #800080; text-decoration-color: #800080">metric_type</span>: Type of metric comparison. Allowed values: <span style="color: #800080; text-decoration-color: #800080">direct-comparison</span>.
- <span style="color: #800080; text-decoration-color: #800080">params</span>: Parameters of the metric comparison.
    - <span style="color: #800080; text-decoration-color: #800080">operator</span>: Comparison operator. Allowed values: <span style="color: #800080; text-decoration-color: #800080">eq</span>, <span style="color: #800080; text-decoration-color: #800080">gt</span>, <span style="color: #800080; text-decoration-color: #800080">ge</span>, <span style="color: #800080; text-decoration-color: #800080">lt</span>, <span style="color: #800080; text-decoration-color: #800080">le</span>, and <span style="color: #800080; text-decoration-color: #800080">ne</span>.
    - <span style="color: #800080; text-decoration-color: #800080">tolerance</span>: Tolerance for the comparison.
        - <span style="color: #800080; text-decoration-color: #800080">type</span>: Type of tolerance. Allowed values: , <span style="color: #800080; text-decoration-color: #800080">absolute</span>, and <span style="color: #800080; text-decoration-color: #800080">relative</span>.
        - <span style="color: #800080; text-decoration-color: #800080">value</span>: Tolerance value (numeric).
- <span style="color: #800080; text-decoration-color: #800080">statistic</span>: Statistical method. Allowed values: <span style="color: #800080; text-decoration-color: #800080">min</span>, <span style="color: #800080; text-decoration-color: #800080">max</span>, <span style="color: #800080; text-decoration-color: #800080">mean</span>, <span style="color: #800080; text-decoration-color: #800080">std</span>, <span style="color: #800080; text-decoration-color: #800080">shifted_geometric_mean</span>, <span style="color: #800080; text-decoration-color: #800080">p01</span>, <span style="color: #800080; text-decoration-color: #800080">p05</span>, <span style="color: #800080; text-decoration-color: #800080">p10</span>, <span style="color: #800080; text-decoration-color: #800080">p25</span>, <span style="color: #800080; text-decoration-color: #800080">p50</span>, <span style="color: #800080; text-decoration-color: #800080">p75</span>, <span style="color: #800080; text-decoration-color: #800080">p90</span>, <span style="color: #800080; text-decoration-color: #800080">p95</span>, and <span style="color: #800080; text-decoration-color: #800080">p99</span>.

Object format:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;field&quot;: &quot;field&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;metric_type&quot;: &quot;type&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;operator&quot;: &quot;op&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;tolerance&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;type&quot;: &quot;tol_type&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;value&quot;: tol_value</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;statistic&quot;: &quot;statistic&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an acceptance test with a single metric.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">METRIC=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;field&quot;: &quot;result.custom.unassigned&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;operator&quot;: &quot;lt&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;tolerance&quot;: {&quot;type&quot;: &quot;relative&quot;, &quot;value&quot;: 0.05}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistic&quot;: &quot;mean&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud acceptance create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --metrics &quot;$METRIC&quot; --input-set-id input-set-123</span>

- Create with multiple metrics by repeating the flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">METRIC1=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;field&quot;: &quot;result.custom.unassigned&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;operator&quot;: &quot;lt&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;tolerance&quot;: {&quot;type&quot;: &quot;relative&quot;, &quot;value&quot;: 0.05}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistic&quot;: &quot;mean&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    METRIC2=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;field&quot;: &quot;run.duration&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;operator&quot;: &quot;le&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;tolerance&quot;: {&quot;type&quot;: &quot;absolute&quot;, &quot;value&quot;: 1.0}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistic&quot;: &quot;p95&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud acceptance create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --metrics &quot;$METRIC1&quot; --metrics &quot;$METRIC2&quot; --input-set-id input-set-123</span>

- Create with multiple metrics in a single <span style="color: #800080; text-decoration-color: #800080">json</span> array.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">METRICS=&#x27;[</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;field&quot;: &quot;result.custom.unassigned&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;operator&quot;: &quot;lt&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;tolerance&quot;: {&quot;type&quot;: &quot;relative&quot;, &quot;value&quot;: 0.05}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;statistic&quot;: &quot;mean&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;field&quot;: &quot;run.duration&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;operator&quot;: &quot;le&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;tolerance&quot;: {&quot;type&quot;: &quot;absolute&quot;, &quot;value&quot;: 1.0}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;statistic&quot;: &quot;p95&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    ]&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud acceptance create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --metrics &quot;$METRICS&quot; --input-set-id input-set-123</span>

- Create an acceptance test and wait for it to complete.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">METRIC=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;field&quot;: &quot;result.custom.unassigned&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;operator&quot;: &quot;lt&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;tolerance&quot;: {&quot;type&quot;: &quot;relative&quot;, &quot;value&quot;: 0.05}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistic&quot;: &quot;mean&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud acceptance create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --metrics &quot;$METRIC&quot; --input-set-id input-set-123 --wait</span>

- Create an acceptance test and save the results to a file, waiting for completion.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">METRIC=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;field&quot;: &quot;result.custom.unassigned&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;metric_type&quot;: &quot;direct-comparison&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;params&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;operator&quot;: &quot;lt&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;tolerance&quot;: {&quot;type&quot;: &quot;relative&quot;, &quot;value&quot;: 0.05}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistic&quot;: &quot;mean&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud acceptance create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id candidate-123 --baseline-instance-id baseline-456 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --metrics &quot;$METRIC&quot; --input-set-id input-set-123 --output results.json</span>

**Usage**:

```console
$ cloud acceptance create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --baseline-instance-id BASELINE_INSTANCE_ID`: ID of the baseline instance to compare against.  [required]
* `-c, --candidate-instance-id CANDIDATE_INSTANCE_ID`: ID of the candidate instance to test.  [required]
* `-m, --metrics METRICS`: Metrics to use for the acceptance test. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple metrics by repeating the flag, or providing a list of objects. See command help for details on metric formatting.  [required]
* `-t, --acceptance-test-id ACCEPTANCE_TEST_ID`: An optional ID for the acceptance test. If not provided, a random ID will be generated.  [env var: NEXTMV_ACCEPTANCE_TEST_ID]
* `-d, --description DESCRIPTION`: Description of the acceptance test.
* `-i, --input-set-id INPUT_SET_ID`: ID of the input set to use for the underlying batch experiment. Required if the batch experiment does not exist yet.
* `-n, --name NAME`: Optional name of the acceptance test. If not provided, the ID will be used as the name.
* `-o, --output OUTPUT_PATH`: Waits for the test to complete and saves the results to this location.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the acceptance test to complete. Results are printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud acceptance delete`

Deletes a Nextmv Cloud acceptance test.

This action is permanent and cannot be undone. The underlying batch
experiment and associated data will also be deleted. Use the --yes flag to
skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the acceptance test with the ID <span style="color: #800080; text-decoration-color: #800080">test-cotton-tail</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance delete --app-id hare-app --acceptance-test-id test-cotton-tail</span>

- Delete the acceptance test without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance delete --app-id hare-app --acceptance-test-id test-cotton-tail --yes</span>

**Usage**:

```console
$ cloud acceptance delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-t, --acceptance-test-id ACCEPTANCE_TEST_ID`: The Nextmv Cloud acceptance test ID to use for this action.  [env var: NEXTMV_ACCEPTANCE_TEST_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud acceptance get`

Get a Nextmv Cloud acceptance test.

Use the --wait flag to wait for the acceptance test to complete, polling
for results. Using the --output flag will also activate waiting, and allows
you to specify a destination file for the results.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the acceptance test with ID <span style="color: #800080; text-decoration-color: #800080">test-123</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance get --app-id hare-app --acceptance-test-id test-123</span>

- Get the acceptance test and wait for it to complete if necessary.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance get --app-id hare-app --acceptance-test-id test-123 --wait</span>

- Get the acceptance test and save the results to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance get --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --acceptance-test-id test-123 --output results.json</span>

- Get the acceptance test using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance get --app-id hare-app --acceptance-test-id test-123 --profile prod</span>

**Usage**:

```console
$ cloud acceptance get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-t, --acceptance-test-id ACCEPTANCE_TEST_ID`: The Nextmv Cloud acceptance test ID to use for this action.  [env var: NEXTMV_ACCEPTANCE_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Waits for the acceptance test to complete and saves the results to this location.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the acceptance test to complete. Results are printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud acceptance list`

List all Nextmv Cloud acceptance tests for an application.

This command retrieves all acceptance tests associated with the specified
application. By default this command paginates the list of tests, which
means multiple API calls may be made to retrieve all tests. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all acceptance tests for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance list --app-id hare-app</span>

- List all acceptance tests and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance list --app-id hare-app --output tests.json</span>

- List all acceptance tests using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance list --app-id hare-app --profile prod</span>

- List all acceptance tests without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud acceptance list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of acceptance tests to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud acceptance update`

Update a Nextmv Cloud acceptance test.

Update the name and/or description of an acceptance test. Any fields not
specified will remain unchanged.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of an acceptance test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --acceptance-test-id test-123 --name &quot;Updated Test Name&quot;</span>

- Update the description of an acceptance test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --acceptance-test-id test-123 --description &quot;Updated description&quot;</span>

- Update both name and description and save the result.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud acceptance update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --acceptance-test-id test-123 --name &quot;New Name&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;New description&quot; --output updated-test.json</span>

**Usage**:

```console
$ cloud acceptance update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-t, --acceptance-test-id ACCEPTANCE_TEST_ID`: The Nextmv Cloud acceptance test ID to use for this action.  [env var: NEXTMV_ACCEPTANCE_TEST_ID; required]
* `-d, --description DESCRIPTION`: Updated description of the acceptance test.
* `-n, --name NAME`: Updated name of the acceptance test.
* `-o, --output OUTPUT_PATH`: Saves the updated acceptance test information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud account`

Manage your Nextmv Cloud account (organization).

Please contact <span style="font-weight: bold"><a href="https://www.nextmv.io/contact">Nextmv</a></span>
<span style="font-weight: bold"><a href="https://www.nextmv.io/contact">support</a></span> for assistance configuring SSO for your organization.
You may use the <span style="font-weight: bold">nextmv cloud sso</span> command tree to manage the
SSO configuration for your organization.

**Usage**:

```console
$ cloud account [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud account in your...
* `delete`: Deletes an account within your SSO-enabled...
* `get`: Get the information of a Nextmv Cloud...
* `update`: Updates information of a Nextmv Cloud...

#### `cloud account create`

Create a new Nextmv Cloud account in your organization.

To create managed accounts, SSO must be configured for your organization.
Please contact <span style="font-weight: bold"><a href="https://www.nextmv.io/contact">Nextmv</a></span>
<span style="font-weight: bold"><a href="https://www.nextmv.io/contact">support</a></span> for assistance. You may use the <span style="font-weight: bold">nextmv cloud</span>
<span style="font-weight: bold">sso</span> command tree to manage the SSO configuration for your
organization.

At least one administrator email address must be provided. Multiple
administrators can be specified by repeating the --admins flag or by
separating email addresses with commas.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an account named <span style="color: #800080; text-decoration-color: #800080">Bunny Logistics</span> with a single administrator.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account create --name &quot;Bunny Logistics&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --admins peter.rabbit@carrotexpress.com</span>

- Create an account named <span style="color: #800080; text-decoration-color: #800080">Hare Delivery Co</span> with multiple administrators.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account create --name &quot;Hare Delivery Co&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --admins bugs@acme.com --admins roger@toontown.com</span>

- Create an account using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account create --name &quot;Cottontail Couriers&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --admins fluffy@hopmail.com --profile hare</span>

- Create an account with comma-separated administrators.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account create --name &quot;Whiskers Warehouse&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --admins &quot;thumper@forestmail.com,flopsy@warren.io&quot;</span>

**Usage**:

```console
$ cloud account create [OPTIONS]
```

**Options**:

* `-a, --admins ADMINS`: Email addresses of the administrators for the account. Pass multiple emails by repeating the flag, or separating with commas.  [required]
* `-n, --name NAME`: A name for the account.  [required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud account delete`

Deletes an account within your SSO-enabled organization.

You must have the <span style="color: #800080; text-decoration-color: #800080">administrator</span> role on that account in order to delete it.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the account with the ID <span style="color: #800080; text-decoration-color: #800080">bunnies-account</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account delete --account-id bunnies-account</span>

- Delete the account without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account delete --account-id bunnies-account --yes</span>

**Usage**:

```console
$ cloud account delete [OPTIONS]
```

**Options**:

* `-a, --account-id ACCOUNT_ID`: The Nextmv Cloud account ID to use for this action.  [env var: NEXTMV_ACCOUNT_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud account get`

Get the information of a Nextmv Cloud account.

This command is useful to get the attributes of an existing Nextmv Cloud
account by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the account with the ID <span style="color: #800080; text-decoration-color: #800080">bunny-logistics</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account get --account-id bunny-logistics</span>

- Get the account with the ID <span style="color: #800080; text-decoration-color: #800080">cottontail-couriers</span> and save the information to an
  <span style="color: #800080; text-decoration-color: #800080">account.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account get --account-id cottontail-couriers --output account.json</span>

**Usage**:

```console
$ cloud account get [OPTIONS]
```

**Options**:

* `-a, --account-id ACCOUNT_ID`: The Nextmv Cloud account ID to use for this action.  [env var: NEXTMV_ACCOUNT_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the account information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud account update`

Updates information of a Nextmv Cloud account.

This command allows you to update the name of an existing account.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the account named <span style="color: #800080; text-decoration-color: #800080">hare-delivery</span> to <span style="color: #800080; text-decoration-color: #800080">Hare Delivery Co</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account update --account-id hare-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Hare Delivery Co&quot;</span>

- Update an account and save the updated information to an <span style="color: #800080; text-decoration-color: #800080">updated_account.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud account update --account-id cottontail-couriers \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Cottontail Express&quot; --output updated_account.json</span>

**Usage**:

```console
$ cloud account update [OPTIONS]
```

**Options**:

* `-a, --account-id ACCOUNT_ID`: The Nextmv Cloud account ID to use for this action.  [env var: NEXTMV_ACCOUNT_ID; required]
* `-n, --name NAME`: A new name for the account.  [required]
* `-o, --output OUTPUT_PATH`: Saves the updated account information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud app`

Create, manage, and push Nextmv Cloud applications.

A Nextmv application is an entity that contains a decision model as
executable code. An application can make a run by taking an input,
executing the decision model, and producing an output.

**Usage**:

```console
$ cloud app [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud application.
* `delete`: Deletes a Nextmv Cloud application.
* `exists`: Check if a Nextmv Cloud application exists.
* `get`: Get a Nextmv Cloud application.
* `list`: List all Nextmv Cloud applications.
* `push`: Push (deploy) a Nextmv application to...
* `update`: Updates a Nextmv Cloud application.

#### `cloud app create`

Create a new Nextmv Cloud application.

Use the --exist-ok flag to avoid errors when creating an application with
an ID that already exists. This is useful for scripts that need to ensure
an application exists without worrying about whether it was created
previously.

An application can be marked as a workflow using the --is-workflow flag.
Workflows allow for more complex decision-making processes by leveraging
<span style="font-weight: bold"><a href="https://github.com/nextmv-io/nextpipe">Nextpipe</a></span> to
orchestrate multiple decision models.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an application with the name <span style="color: #800080; text-decoration-color: #800080">Hare App</span>. A random ID will be generated.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare App&quot;</span>

- Create an application with the specific ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare App&quot; --app-id hare-app</span>

- Create an application with an ID and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare App&quot; --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;An application for routing hares&quot;</span>

- Create an application, or get it if it already exists.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare App&quot; --app-id hare-app --exist-ok</span>

- Create a workflow application.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare Workflow&quot; --app-id hare-workflow --is-workflow</span>

- Create an application with a default instance ID.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare App&quot; --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --default-instance-id burrow</span>

- Create an application with a default experiment instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app create --name &quot;Hare App&quot; --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --default-experiment-instance experiment-v1</span>

**Usage**:

```console
$ cloud app create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: An optional ID for the Nextmv Cloud application. If not provided, a random ID will be generated.  [env var: NEXTMV_APP_ID]
* `-x, --default-experiment-instance DEFAULT_EXPERIMENT_INSTANCE`: An optional default experiment instance ID for the application.
* `-i, --default-instance-id DEFAULT_INSTANCE_ID`: An optional default instance ID for the application.
* `-d, --description DESCRIPTION`: An optional description for the application.
* `-e, --exist-ok`: If an application with the given ID already exists, do not raise an error, and simply return it.
* `-w, --is-workflow`: Whether the application is a workflow.
* `-n, --name NAME`: An optional name for the application. If not provided, the application ID will be used as the name.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud app delete`

Deletes a Nextmv Cloud application.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app delete --app-id hare-app</span>

- Delete the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app delete --app-id hare-app --yes</span>

**Usage**:

```console
$ cloud app delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud app exists`

Check if a Nextmv Cloud application exists.

This command is useful in scripting applications to verify the existence of
a Nextmv Cloud application by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Check if the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> exists.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app exists --app-id hare-app</span>

- Check if the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> exists.
  Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app exists --app-id hare-app --profile hare</span>

**Usage**:

```console
$ cloud app exists [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud app get`

Get a Nextmv Cloud application.

This command is useful to get the attributes of an existing Nextmv Cloud
application by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app get --app-id hare-app</span>

- Get the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> and save the information to an
  <span style="color: #800080; text-decoration-color: #800080">app.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app get --app-id hare-app --output app.json</span>

**Usage**:

```console
$ cloud app get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the app information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud app list`

List all Nextmv Cloud applications.

By default this command paginates the list of applications, which means
multiple API calls may be made to retrieve all applications. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all applications.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app list</span>

- List all applications using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app list --profile hare</span>

- List all applications and save the information to an <span style="color: #800080; text-decoration-color: #800080">apps.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app list --output apps.json</span>

- List all applications without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app list --no-pagination</span>

**Usage**:

```console
$ cloud app list [OPTIONS]
```

**Options**:

* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the app list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud app push`

Push (deploy) a Nextmv application to Nextmv Cloud.

Use the --app-dir option to specify the path to your application&#x27;s root
directory. By default, the current working directory is used.

You can also provide a custom manifest file using the --manifest option. If
not provided, the CLI will look for a file named
<span style="color: #800080; text-decoration-color: #800080">app.yaml</span> in the application&#x27;s root.

By default, this command only pushes the app. After the push, you will be
prompted to create a new version. If a new version is created, you will be
prompted to link it to an instance. If the instance exists, you will be
asked if you want to update it. If it doesn&#x27;t, you will be asked to create
it. You can use the following options to skip the prompts, useful in
non-interactive sessions like in a CI/CD pipeline: --version-yes,
--version-no, --version-id, --create-instance-id, and --update-instance-id.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Push an application, with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, from the current directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app</span>

- Push an application, with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, from the <span style="color: #800080; text-decoration-color: #800080">./my-app</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app --app-dir ./my-app</span>

- Push an application, with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using a custom manifest file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app --manifest ./custom-manifest.yaml</span>

- Push and automatically create a new version (no prompt).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app --version-yes</span>

- Push and create a new version with a custom version ID (no prompt).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app --version-id v1.0.0</span>

- Push and create a new version, then link it to a new instance with a specific ID (no prompt).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app --create-instance-id inst-1</span>

- Push and create a new version, then link it to an existing instance (no prompt).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app push --app-id hare-app --update-instance-id inst-1</span>

**Usage**:

```console
$ cloud app push [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-d, --app-dir APP_DIR`: The path to the application&#x27;s root directory.  [default: .]
* `-m, --manifest MANIFEST_PATH`: Path to the application manifest file (<span style="color: #800080; text-decoration-color: #800080">app.yaml</span>).
* `--no-cache`: Do not read from or write to the Nextmv dependency cache for <span style="color: #800080; text-decoration-color: #800080">Python</span> applications.
* `-v, --version-id VERSION_ID`: Custom ID for version creation after app push. Automatically generated if not provided. Activates --version-yes.
* `-y, --version-yes`: Create a new version after push. Skips confirmation prompt. Useful for non-interactive sessions.
* `-n, --version-no`: Skip version creation after push. Skips confirmation prompt. Useful for non-interactive sessions.
* `-c, --create-instance-id CREATE_INSTANCE_ID`: Link the newly created version to a <span style="color: #808000; text-decoration-color: #808000">new</span> instance with this ID. Skips prompt to provide an instance ID. Useful for non-interactive sessions. Activates --version-yes.
* `-u, --update-instance-id UPDATE_INSTANCE_ID`: Link the newly created version to an <span style="color: #808000; text-decoration-color: #808000">existing</span> instance with this ID. Skips prompt to provide an instance ID. Useful for non-interactive sessions. Activates --version-yes.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud app update`

Updates a Nextmv Cloud application.

Please note that you cannot change the type of an application, you must
create a new one.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update an application&#x27;s name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app update --app-id hare-app --name &quot;New Hare App&quot;</span>

- Update an application&#x27;s description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app update --app-id hare-app --name &quot;Hare App&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;An updated description for routing hares&quot;</span>

- Update an application&#x27;s default instance ID.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app update --app-id hare-app --name &quot;Hare App&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --default-instance-id burrow</span>

- Update an application&#x27;s default experiment instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app update --app-id hare-app --name &quot;Hare App&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --default-experiment-instance experiment-v1</span>

- Update multiple application properties at once.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app update --app-id hare-app --name &quot;Hare App&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Updated description&quot; --default-instance-id burrow \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --default-experiment-instance experiment-v1</span>

- Update an application and save the updated information to an <span style="color: #800080; text-decoration-color: #800080">updated_app.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud app update --app-id hare-app --name &quot;New Hare App&quot; --output updated_app.json</span>

**Usage**:

```console
$ cloud app update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-x, --default-experiment-instance DEFAULT_EXPERIMENT_INSTANCE`: A new default experiment instance ID for the application.
* `-i, --default-instance-id DEFAULT_INSTANCE_ID`: A new default instance ID for the application.
* `-d, --description DESCRIPTION`: A new description for the application.
* `-n, --name NAME`: A new name for the application.
* `-o, --output OUTPUT_PATH`: Saves the updated app information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud batch`

Create and manage Nextmv Cloud batch experiments.

**Usage**:

```console
$ cloud batch [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud batch experiment.
* `delete`: Deletes a Nextmv Cloud batch experiment.
* `get`: Get a Nextmv Cloud batch experiment,...
* `list`: List all Nextmv Cloud batch experiments...
* `metadata`: Get metadata for a Nextmv Cloud batch...
* `update`: Update a Nextmv Cloud batch experiment.

#### `cloud batch create`

Create a new Nextmv Cloud batch experiment.

A batch experiment executes multiple runs across different inputs and/or
configurations. Each run is defined by a combination of input, instance or
version, and optional configuration options.

Use the --wait flag to wait for the batch experiment to complete, polling
for results. Using the --output flag will also activate waiting, and allows
you to specify a destination file for the results.

<span style="font-weight: bold; text-decoration: underline">Runs</span>

Runs are provided as <span style="color: #800080; text-decoration-color: #800080">json</span> objects using the --runs flag.
Each run defines what input, instance/version, and configuration to use.

You can provide runs in three ways:
- A single run as a <span style="color: #800080; text-decoration-color: #800080">json</span> object.
- Multiple runs by repeating the --runs flag.
- Multiple runs as a <span style="color: #800080; text-decoration-color: #800080">json</span> array in a single --runs flag.

Each run must have the following fields:
- <span style="color: #800080; text-decoration-color: #800080">input_id</span>: ID of the input to use for this run
  (required). If a managed input is used, this should be the ID of the
  managed input. If <span style="color: #800080; text-decoration-color: #800080">input_set_id</span> is provided for the run,
  this should be the ID of an input within that input set.
- <span style="color: #800080; text-decoration-color: #800080">instance_id</span> OR <span style="color: #800080; text-decoration-color: #800080">version_id</span>: Either an instance ID or
  version ID must be provided (at least one required).
- <span style="color: #800080; text-decoration-color: #800080">option_set</span>: ID of the option set to use (optional).
  Make sure to define the option sets using the --option-sets flag.
- <span style="color: #800080; text-decoration-color: #800080">input_set_id</span>: ID of the input set (optional).
- <span style="color: #800080; text-decoration-color: #800080">scenario_id</span>: Scenario ID if part of a scenario test (optional).
- <span style="color: #800080; text-decoration-color: #800080">repetition</span>: Repetition number (optional).

Object format:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;input_id&quot;: &quot;meadow-input-a1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;instance_id&quot;: &quot;bunny-hopper-v2&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;option_set&quot;: &quot;speed-optimized&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;input_set_id&quot;: &quot;spring-gardens&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

<span style="font-weight: bold; text-decoration: underline">Option Sets</span>

Option sets are provided as a <span style="color: #800080; text-decoration-color: #800080">json</span> object using the
--option-sets flag. Option sets define named collections of
runtime options that can be referenced by runs.

The option sets object is a dictionary where keys are option set IDs and
values are dictionaries of string key-value pairs representing the options.

Object format:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;speed-optimized&quot;: {&quot;timeout&quot;: &quot;30&quot;, &quot;algorithm&quot;: &quot;fast&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;quality-focused&quot;: {&quot;timeout&quot;: &quot;300&quot;, &quot;algorithm&quot;: &quot;thorough&quot;}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a batch experiment with a single run.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;carrot-patch-a&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;warren-planner-v1&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud batch create --app-id hare-app --batch-experiment-id bunny-hop-test \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --input-set-id spring-gardens --runs &quot;$RUN&quot;</span>

- Create with multiple runs by repeating the flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN1=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;lettuce-field-1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RUN2=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;lettuce-field-2&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud batch create --app-id hare-app --input-set-id veggie-gardens \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --runs &quot;$RUN1&quot; --runs &quot;$RUN2&quot;</span>

- Create with multiple runs in a single <span style="color: #800080; text-decoration-color: #800080">json</span> array.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUNS=&#x27;[</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;input_id&quot;: &quot;warren-zone-a&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;instance_id&quot;: &quot;burrow-builder&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;input_id&quot;: &quot;warren-zone-b&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;version_id&quot;: &quot;tunnel-planner-v3&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    ]&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud batch create --app-id hare-app --input-set-id burrow-sites --runs &quot;$RUNS&quot;</span>

- Create a batch experiment and wait for it to complete.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;carrot-harvest&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;foraging-route&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud batch create --app-id hare-app --input-set-id harvest-season \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --runs &quot;$RUN&quot; --wait</span>

- Create a batch experiment and save the results to a file, waiting for completion.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;predator-zones&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;safe-hopper&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud batch create --app-id hare-app --input-set-id danger-zones \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --runs &quot;$RUN&quot; --output bunny-safety-results.json</span>

- Create a batch experiment with option sets.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN1=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;garden-route-1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;option_set&quot;: &quot;fast-hops&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RUN2=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;input_id&quot;: &quot;garden-route-1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;option_set&quot;: &quot;careful-hops&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    OPTION_SETS=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;fast-hops&quot;: {&quot;max_speed&quot;: &quot;10&quot;, &quot;caution_level&quot;: &quot;low&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;careful-hops&quot;: {&quot;max_speed&quot;: &quot;5&quot;, &quot;caution_level&quot;: &quot;high&quot;}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud batch create --app-id hare-app --input-set-id garden-paths \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --runs &quot;$RUN1&quot; --runs &quot;$RUN2&quot; --option-sets &quot;$OPTION_SETS&quot;</span>

**Usage**:

```console
$ cloud batch create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --batch-experiment-id BATCH_EXPERIMENT_ID`: Optional ID for the batch experiment. Will be generated if not provided.  [env var: NEXTMV_BATCH_EXPERIMENT_ID]
* `-d, --description DESCRIPTION`: Description of the batch experiment.
* `-i, --input-set-id INPUT_SET_ID`: ID of the input set to use for the batch experiment.
* `-n, --name NAME`: Optional name of the batch experiment. If not provided, the ID will be used as the name.
* `--option-sets OPTION_SETS`: Option sets to use for the batch experiment. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. See command help for details on option sets formatting.
* `-r, --runs RUNS`: Runs to execute for the batch experiment. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple runs by repeating the flag, or providing a list of objects. See command help for details on run formatting.
* `-o, --output OUTPUT_PATH`: Waits for the experiment to complete and saves the results to this location.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the batch experiment to complete. Results are printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud batch delete`

Deletes a Nextmv Cloud batch experiment.

This action is permanent and cannot be undone. The batch experiment and all
associated data, including runs, will be deleted. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the batch experiment with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch delete --app-id hare-app --batch-experiment-id hop-analysis</span>

- Delete the batch experiment without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch delete --app-id hare-app --batch-experiment-id carrot-routes --yes</span>

**Usage**:

```console
$ cloud batch delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --batch-experiment-id BATCH_EXPERIMENT_ID`: The Nextmv Cloud batch experiment ID to use for this action.  [env var: NEXTMV_BATCH_EXPERIMENT_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud batch get`

Get a Nextmv Cloud batch experiment, including its runs.

Use the --wait flag to wait for the batch experiment to
complete, polling for results. Using the --output flag will
also activate waiting, and allows you to specify a destination file for the
results.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the batch experiment with ID <span style="color: #800080; text-decoration-color: #800080">carrot-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch get --app-id hare-app --batch-experiment-id carrot-optimization</span>

- Get the batch experiment and wait for it to complete if necessary.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch get --app-id hare-app --batch-experiment-id bunny-hop-test --wait</span>

- Get the batch experiment and save the results to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch get --app-id hare-app --batch-experiment-id warren-planning \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output results.json</span>

- Get the batch experiment using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch get --app-id hare-app --batch-experiment-id lettuce-routes --profile prod</span>

**Usage**:

```console
$ cloud batch get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --batch-experiment-id BATCH_EXPERIMENT_ID`: The Nextmv Cloud batch experiment ID to use for this action.  [env var: NEXTMV_BATCH_EXPERIMENT_ID; required]
* `-o, --output OUTPUT_PATH`: Waits for the batch experiment to complete and saves the results to this location.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the batch experiment to complete. Results are printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud batch list`

List all Nextmv Cloud batch experiments for an application.

This command retrieves all batch experiments associated with the specified
application. By default this command paginates the list of experiments,
which means multiple API calls may be made to retrieve all experiments. You
may use the --no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all batch experiments for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch list --app-id hare-app</span>

- List all batch experiments and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch list --app-id hare-app --output experiments.json</span>

- List all batch experiments using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch list --app-id hare-app --profile prod</span>

- List all experiments without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud batch list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of batch experiments to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud batch metadata`

Get metadata for a Nextmv Cloud batch experiment.

This command retrieves metadata for a specific batch experiment, including
status, creation date, and other high-level information without the full
run details.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get metadata for batch experiment <span style="color: #800080; text-decoration-color: #800080">bunny-warren-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch metadata --app-id hare-app --batch-experiment-id bunny-warren-optimization</span>

- Get metadata and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch metadata --app-id hare-app --batch-experiment-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output metadata.json</span>

- Get metadata using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch metadata --app-id hare-app --batch-experiment-id hop-schedule --profile prod</span>

**Usage**:

```console
$ cloud batch metadata [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --batch-experiment-id BATCH_EXPERIMENT_ID`: The Nextmv Cloud batch experiment ID to use for this action.  [env var: NEXTMV_BATCH_EXPERIMENT_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the batch experiment metadata to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud batch update`

Update a Nextmv Cloud batch experiment.

Update the name and/or description of a batch experiment. Any fields not
specified will remain unchanged.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of a batch experiment.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch update --app-id hare-app --batch-experiment-id carrot-feast \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Spring Carrot Harvest&quot;</span>

- Update the description of a batch experiment.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch update --app-id hare-app --batch-experiment-id bunny-hop-routes \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Optimizing hop paths through the meadow&quot;</span>

- Update both name and description and save the result.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud batch update --app-id hare-app --batch-experiment-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Warren Lettuce Express&quot; --description &quot;Fast lettuce delivery to all burrows&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output updated-batch.json</span>

**Usage**:

```console
$ cloud batch update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --batch-experiment-id BATCH_EXPERIMENT_ID`: The Nextmv Cloud batch experiment ID to use for this action.  [env var: NEXTMV_BATCH_EXPERIMENT_ID; required]
* `-d, --description DESCRIPTION`: Updated description of the batch experiment.
* `-n, --name NAME`: Updated name of the batch experiment.
* `-o, --output OUTPUT_PATH`: Saves the updated batch experiment information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud data`

Upload data for Nextmv Cloud application components.

When data is too large (exceeds <span style="color: #800080; text-decoration-color: #800080">5 MiB</span>), or you are
working with the <span style="color: #800080; text-decoration-color: #800080">multi-file</span> content format, you can use
this command to upload information to Nextmv Cloud. Requires a pre-signed
upload URL, which can be obtained using the <span style="font-weight: bold">nextmv cloud upload</span>
<span style="font-weight: bold">create</span> command. Use the <span style="color: #800080; text-decoration-color: #800080">.upload_url</span> field from the
command output.

**Usage**:

```console
$ cloud data [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `upload`: Upload data for Nextmv Cloud application...

#### `cloud data upload`

Upload data for Nextmv Cloud application components.

When data is too large, or is not in a text-based content format, you can
use this command to upload information for a Nextmv Cloud application. Data
is used for starting new runs, tracking runs, performing experiments, and
more.

The --upload-url flag is required to specify the pre-signed
upload URL. It can be obtained using the <span style="font-weight: bold">nextmv cloud upload</span>
<span style="font-weight: bold">create</span> command. Use the <span style="color: #800080; text-decoration-color: #800080">.upload_url</span> field from
the command output.

The data input should be given through <span style="color: #800080; text-decoration-color: #800080">stdin</span> or the
--input flag. When using the --input flag, the value can be one of the
following:

- <span style="color: #808000; text-decoration-color: #808000">&lt;FILE_PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">file</span> containing
  the data. Use with the <span style="color: #800080; text-decoration-color: #800080">json</span>, and
  <span style="color: #800080; text-decoration-color: #800080">text</span> content formats.
- <span style="color: #808000; text-decoration-color: #808000">&lt;DIR_PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">directory</span>
  containing data files. Use with the <span style="color: #800080; text-decoration-color: #800080">multi-file</span>
  content format.
- <span style="color: #808000; text-decoration-color: #808000">&lt;.tar.gz PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file
  containing tarred data files. Use with the <span style="color: #800080; text-decoration-color: #800080">multi-file</span>
  content format.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Upload data from <span style="color: #800080; text-decoration-color: #800080">stdin</span> for application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">echo &#x27;{&quot;key&quot;: &quot;value&quot;}&#x27; | nextmv cloud data upload --app-id hare-app --upload-url &lt;URL&gt;</span>

- Upload data from a <span style="color: #800080; text-decoration-color: #800080">JSON</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud data upload --app-id hare-app --upload-url &lt;URL&gt; --input data.json</span>

- Upload data from a <span style="color: #800080; text-decoration-color: #800080">text</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud data upload --app-id hare-app --upload-url &lt;URL&gt; --input data.txt</span>

- Upload <span style="color: #800080; text-decoration-color: #800080">multi-file</span> data from a directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud data upload --app-id hare-app --upload-url &lt;URL&gt; --input ./data_directory</span>

- Upload <span style="color: #800080; text-decoration-color: #800080">multi-file</span> data from a
  <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud data upload --app-id hare-app --upload-url &lt;URL&gt; --input data.tar.gz</span>

- Upload data using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud data upload --app-id hare-app --upload-url &lt;URL&gt; --input data.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --profile production</span>

**Usage**:

```console
$ cloud data upload [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-u, --upload-url UPLOAD_URL`: Pre-signed URL for uploading the data.  [required]
* `-i, --input INPUT_PATH`: The input path to use. File or directory depending on content format. Uses <span style="color: #800080; text-decoration-color: #800080">stdin</span> if not defined. Can be a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file for multi-file content format.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud ensemble`

Create and manage Nextmv Cloud ensemble definitions.

An ensemble definition defines how to coordinate and execute multiple child
runs for an application, and how to determine the optimal result from those
runs. You can configure run groups to specify which instances to run on and
with what options, as well as evaluation rules to determine the best result
based on specified metrics.

**Usage**:

```console
$ cloud ensemble [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud ensemble...
* `delete`: Deletes a Nextmv Cloud ensemble definition.
* `get`: Get a Nextmv Cloud ensemble definition.
* `list`: List all Nextmv Cloud ensemble definitions...
* `update`: Update a Nextmv Cloud ensemble definition.

#### `cloud ensemble create`

Create a new Nextmv Cloud ensemble definition.

An ensemble definition coordinates the execution of multiple child runs for
an application and determines the optimal result from those runs. Each
ensemble definition contains run groups and evaluation rules.

<span style="font-weight: bold; text-decoration: underline">Run Groups</span>

Run groups are provided as <span style="color: #800080; text-decoration-color: #800080">json</span> objects using the
--run-groups flag. Each run group specifies how child runs are executed.

You can provide run groups in three ways:
- A single run group as a <span style="color: #800080; text-decoration-color: #800080">json</span> object.
- Multiple run groups by repeating the --run-groups flag.
- Multiple run groups as a <span style="color: #800080; text-decoration-color: #800080">json</span> array in a single --run-groups flag.

Each run group must have the following fields:
- <span style="color: #800080; text-decoration-color: #800080">id</span>: Unique identifier for the run group (required).
- <span style="color: #800080; text-decoration-color: #800080">instance_id</span>: The instance to execute runs on (required).
- <span style="color: #800080; text-decoration-color: #800080">options</span>: Runtime options/parameters (optional). Options should be provided as a
  <span style="color: #800080; text-decoration-color: #800080">json</span> object with <span style="color: #800080; text-decoration-color: #800080">string</span> key-value pairs.
- <span style="color: #800080; text-decoration-color: #800080">repetitions</span>: Number of times to repeat the run (optional).

Object format:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;id&quot;: &quot;rg1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;instance_id&quot;: &quot;inst-123&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;options&quot;: {&quot;param&quot;: &quot;value&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;repetitions&quot;: 5</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

<span style="font-weight: bold; text-decoration: underline">Evaluation Rules</span>

Evaluation rules are provided as <span style="color: #800080; text-decoration-color: #800080">json</span> objects using the
--rules flag. Each rule determines how to evaluate and select the best
result from the child runs.

You can provide rules in three ways:
- A single rule as a <span style="color: #800080; text-decoration-color: #800080">json</span> object.
- Multiple rules by repeating the --rules flag.
- Multiple rules as a <span style="color: #800080; text-decoration-color: #800080">json</span> array in a single --rules flag.

Each rule must have the following fields:
- <span style="color: #800080; text-decoration-color: #800080">id</span>: Unique identifier for the rule (required).
- <span style="color: #800080; text-decoration-color: #800080">statistics_path</span>: JSONPath to the metric (e.g., <span style="color: #800080; text-decoration-color: #800080">$.result.value</span>) (required).
- <span style="color: #800080; text-decoration-color: #800080">objective</span>: Objective for the evaluation (required).
  Allowed values: <span style="color: #800080; text-decoration-color: #800080">maximize</span> and <span style="color: #800080; text-decoration-color: #800080">minimize</span>.
- <span style="color: #800080; text-decoration-color: #800080">tolerance</span>: Object with the following fields (required):
    - <span style="color: #800080; text-decoration-color: #800080">value</span>: Tolerance value (float).
    - <span style="color: #800080; text-decoration-color: #800080">type</span>: Tolerance type. Allowed values: <span style="color: #800080; text-decoration-color: #800080">absolute</span> and <span style="color: #800080; text-decoration-color: #800080">relative</span>.
- <span style="color: #800080; text-decoration-color: #800080">index</span>: Evaluation order - lower indices evaluated first (required).

Object format:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;id&quot;: &quot;rule1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;statistics_path&quot;: &quot;$.result.value&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;objective&quot;: &quot;minimize&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;tolerance&quot;: {&quot;value&quot;: 0.1, &quot;type&quot;: &quot;relative&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;index&quot;: 0</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an ensemble definition with a single run group and rule.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN_GROUP=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rg1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;inst-123&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RULE=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rule1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistics_path&quot;: &quot;$.result.value&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;objective&quot;: &quot;minimize&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;tolerance&quot;: {&quot;value&quot;: 0.1, &quot;type&quot;: &quot;relative&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;index&quot;: 0</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud ensemble create --app-id hare-app --run-groups &quot;$RUN_GROUP&quot; --rules &quot;$RULE&quot;</span>

- Create with multiple run groups by repeating the flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN_GROUP_1=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rg1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;inst-123&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RUN_GROUP_2=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rg2&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;inst-456&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;options&quot;: {&quot;param&quot;: &quot;value&quot;}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RULE=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rule1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistics_path&quot;: &quot;$.result.value&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;objective&quot;: &quot;minimize&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;tolerance&quot;: {&quot;value&quot;: 0.1, &quot;type&quot;: &quot;relative&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;index&quot;: 0</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud ensemble create --app-id hare-app --run-groups &quot;$RUN_GROUP_1&quot; --run-groups &quot;$RUN_GROUP_2&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --rules &quot;$RULE&quot;</span>

- Create with multiple items in a single JSON array.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN_GROUPS=&#x27;[</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {&quot;id&quot;: &quot;rg1&quot;, &quot;instance_id&quot;: &quot;inst-123&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {&quot;id&quot;: &quot;rg2&quot;, &quot;instance_id&quot;: &quot;inst-456&quot;}</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    ]&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RULES=&#x27;[{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rule1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistics_path&quot;: &quot;$.result.value&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;objective&quot;: &quot;minimize&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;tolerance&quot;: {&quot;value&quot;: 0.1, &quot;type&quot;: &quot;relative&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;index&quot;: 0</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }]&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud ensemble create --app-id hare-app --run-groups &quot;$RUN_GROUPS&quot; --rules &quot;$RULES&quot;</span>

- Create with custom ID, name, and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN_GROUP=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rg1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;inst-123&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RULE=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rule1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistics_path&quot;: &quot;$.result.value&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;objective&quot;: &quot;minimize&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;tolerance&quot;: {&quot;value&quot;: 0.1, &quot;type&quot;: &quot;relative&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;index&quot;: 0</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud ensemble create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --ensemble-definition-id prod-ensemble --name &quot;Production Ensemble&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Production ensemble with multiple solvers&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --run-groups &quot;$RUN_GROUP&quot; --rules &quot;$RULE&quot;</span>

- Create with run group repetitions.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">RUN_GROUP=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rg1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;inst-123&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;repetitions&quot;: 5</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    RULE=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;id&quot;: &quot;rule1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;statistics_path&quot;: &quot;$.result.value&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;objective&quot;: &quot;minimize&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;tolerance&quot;: {&quot;value&quot;: 0.1, &quot;type&quot;: &quot;relative&quot;},</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;index&quot;: 0</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud ensemble create --app-id hare-app --run-groups &quot;$RUN_GROUP&quot; --rules &quot;$RULE&quot;</span>

**Usage**:

```console
$ cloud ensemble create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-groups RUN_GROUPS`: Run groups to configure for the ensemble. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple run groups by repeating the flag, or providing a list of objects. See command help for details on run group formatting.  [required]
* `-u, --rules RULES`: Evaluation rules to configure for the ensemble. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple rules by repeating the flag, or providing a list of objects. See command help for details on rule formatting.  [required]
* `-d, --description DESCRIPTION`: An optional description for the ensemble definition.
* `-n, --name NAME`: Optional name for the ensemble definition. If not provided, the ID will be used as the name.
* `-e, --ensemble-definition-id ENSEMBLE_DEFINITION_ID`: The ID to assign to the new ensemble definition. If not provided, a random ID will be generated.  [env var: NEXTMV_ENSEMBLE_DEFINITION_ID]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud ensemble delete`

Deletes a Nextmv Cloud ensemble definition.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the ensemble definition with the ID <span style="color: #800080; text-decoration-color: #800080">prod-ensemble</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble delete --app-id hare-app --ensemble-definition-id prod-ensemble</span>

- Delete the ensemble definition without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble delete --app-id hare-app --ensemble-definition-id prod-ensemble --yes</span>

**Usage**:

```console
$ cloud ensemble delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-e, --ensemble-definition-id ENSEMBLE_DEFINITION_ID`: The Nextmv Cloud ensemble definition ID to use for this action.  [env var: NEXTMV_ENSEMBLE_DEFINITION_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud ensemble get`

Get a Nextmv Cloud ensemble definition.

This command is useful to get the attributes of an existing Nextmv Cloud
ensemble definition by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the ensemble definition with the ID <span style="color: #800080; text-decoration-color: #800080">prod-ensemble</span> from
  application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble get --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    --ensemble-definition-id prod-ensemble</span>

- Get the ensemble definition with the ID <span style="color: #800080; text-decoration-color: #800080">prod-ensemble</span> and
  save the information to an <span style="color: #800080; text-decoration-color: #800080">ensemble.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble get --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --ensemble-definition-id prod-ensemble --output ensemble.json</span>

**Usage**:

```console
$ cloud ensemble get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-e, --ensemble-definition-id ENSEMBLE_DEFINITION_ID`: The Nextmv Cloud ensemble definition ID to use for this action.  [env var: NEXTMV_ENSEMBLE_DEFINITION_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the ensemble definition information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud ensemble list`

List all Nextmv Cloud ensemble definitions for an application.

This command retrieves all ensemble definitions associated with the
specified application. By default this command paginates the list of
definitions, which means multiple API calls may be made to retrieve all
definitions. You may use the --no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all ensemble definitions for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble list --app-id hare-app</span>

- List all ensemble definitions and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble list --app-id hare-app --output ensembles.json</span>

- List all ensemble definitions using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble list --app-id hare-app --profile prod</span>

- List all ensemble definitions without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud ensemble list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of ensemble definitions to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud ensemble update`

Update a Nextmv Cloud ensemble definition.

You can update the name and/or description of an existing ensemble
definition. To modify run groups or evaluation rules, you need to delete
and recreate the ensemble definition.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of an ensemble definition.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --ensemble-definition-id prod-ensemble --name &quot;Updated Production Ensemble&quot;</span>

- Update the description of an ensemble definition.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --ensemble-definition-id prod-ensemble \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Updated ensemble for production workloads&quot;</span>

- Update both name and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --ensemble-definition-id prod-ensemble --name &quot;Production Ensemble v2&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Enhanced ensemble configuration for production&quot;</span>

- Update and save the result to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud ensemble update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --ensemble-definition-id prod-ensemble --name &quot;New Name&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;New Description&quot; --output updated.json</span>

**Usage**:

```console
$ cloud ensemble update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-e, --ensemble-definition-id ENSEMBLE_DEFINITION_ID`: The Nextmv Cloud ensemble definition ID to use for this action.  [env var: NEXTMV_ENSEMBLE_DEFINITION_ID; required]
* `-d, --description DESCRIPTION`: A new description for the ensemble definition.
* `-n, --name NAME`: A new name for the ensemble definition.
* `-o, --output OUTPUT_PATH`: Saves the updated ensemble definition information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud input-set`

Create and manage Nextmv Cloud input sets.

An input set is a collection of inputs from associated runs that can be
reused across multiple experiments. Input sets allow you to test different
configurations of your decision model using the same set of inputs for
consistent comparison.

**Usage**:

```console
$ cloud input-set [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud input set for...
* `delete`: Deletes a Nextmv Cloud input set.
* `get`: Get an Nextmv Cloud input set.
* `list`: List all input sets of a Nextmv Cloud...
* `update`: Updates a Nextmv Cloud input set.

#### `cloud input-set create`

Create a new Nextmv Cloud input set for experiments.

An input set is a collection of inputs that can be reused across multiple
experiments.

1. --run-ids: Create from a list of existing run IDs.
2. --managed-inputs: Create from existing managed inputs in the application.
3. --instance-id with --start-time and --end-time:
   Create from instance runs matching the time range criteria.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an input set for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span> from runs.
  A random input set ID will be generated if one is not provided.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --run-ids run-1 --run-ids run-2 --run-ids run-3</span>

- Create an input set with a specific ID and name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set create --app-id hare-app --input-set-id hare-input-set \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Hare Input Set&quot; --run-ids run-1 --run-ids run-2 --run-ids run-3</span>

- Create an input set using existing managed inputs.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --managed-inputs &#x27;[{&quot;id&quot;: &quot;hare-input-1&quot;, &quot;name&quot;: &quot;hare input&quot;, &quot;description&quot;: &quot;hare description&quot;}]&#x27;</span>

- Create an input set from runs using a specific instance and time range.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id hare-instance --start-time &quot;2024-01-01T00:00:00Z&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --end-time &quot;2024-01-31T23:59:59Z&quot;</span>

**Usage**:

```console
$ cloud input-set create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-d, --description DESCRIPTION`: An optional description for the input set.
* `--end-time END_TIME`: End time for filtering runs in <span style="color: #800080; text-decoration-color: #800080">RFC 3339</span> format. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&#x27;2024-01-01T00:00:00Z&#x27;</span>
* `-s, --input-set-id INPUT_SET_ID`: An optional ID for the input set. If not provided, a random ID will be generated.  [env var: NEXTMV_INPUT_SET_ID]
* `-i, --instance-id INSTANCE_ID`: Instance ID to filter runs from.
* `--managed-inputs MANAGED_INPUTS`: Managed inputs for the input set. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">[{&#x27;id&#x27;: &#x27;id&#x27;, &#x27;name&#x27;: &#x27;name&#x27;, &#x27;description&#x27;: &#x27;description&#x27;}]</span>.
* `-m, --maximum-runs MAXIMUM_RUNS`: Maximum number of runs to include (max <span style="color: #800080; text-decoration-color: #800080">20</span>).  [default: 20]
* `-n, --name NAME`: An optional name for the input set. If not provided, the ID will be used as the name.
* `-r, --run-ids RUN_IDS`: List of run IDs to include in the input set (max 20). Pass multiple run IDs by repeating the flag.
* `--start-time START_TIME`: Start time for filtering runs in <span style="color: #800080; text-decoration-color: #800080">RFC 3339</span> format. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&#x27;2024-01-01T00:00:00Z&#x27;</span>
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud input-set delete`

Deletes a Nextmv Cloud input set.

This action is permanent and cannot be undone. The input set and all
associated data will be deleted. Use the --yes flag to skip the
confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the input set with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set delete --app-id hare-app --input-set-id hop-analysis</span>

- Delete the input set without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set delete --app-id hare-app --input-set-id carrot-routes --yes</span>

**Usage**:

```console
$ cloud input-set delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --input-set-id INPUT_SET_ID`: The Nextmv Cloud input set ID to use for this action.  [env var: NEXTMV_INPUT_SET_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud input-set get`

Get an Nextmv Cloud input set.

This command retrieves the details of an existing input set, including
its name, description, and the list of inputs it contains.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get an input set with the ID <span style="color: #800080; text-decoration-color: #800080">hare-input-set</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set get --app-id hare-app --input-set-id hare-input-set</span>

- Get an input set with the ID <span style="color: #800080; text-decoration-color: #800080">hare-input-set</span> and save
  the information to a <span style="color: #800080; text-decoration-color: #800080">input-set.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set get --app-id hare-app --input-set-id hare-input-set \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output input-set.json</span>

**Usage**:

```console
$ cloud input-set get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --input-set-id INPUT_SET_ID`: The Nextmv Cloud input set ID to use for this action.  [env var: NEXTMV_INPUT_SET_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the input set information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud input-set list`

List all input sets of a Nextmv Cloud application.

This command retrieves all input sets that exist for a given Nextmv Cloud
application. By default this command paginates the list of input sets,
which means multiple API calls may be made to retrieve all input sets. You
may use the --no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all input sets of application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set list --app-id hare-app</span>

- List all input sets using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set list --app-id hare-app --profile hare</span>

- List all input sets and save the information to a <span style="color: #800080; text-decoration-color: #800080">input-sets.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set list --app-id hare-app --output input-sets.json</span>

- List all input sets without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud input-set list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the input set list to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud input-set update`

Updates a Nextmv Cloud input set.

This command updates the metadata of an existing input set. You can update
the name, description, or managed inputs of the input set.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update an input set&#x27;s name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --input-set-id hare-input-set --name &quot;New Name&quot;</span>

- Update an input set&#x27;s description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --input-set-id hare-input-set --description &quot;Updated description&quot;</span>

- Update an input set&#x27;s managed inputs.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --managed-inputs &#x27;[{&quot;id&quot;: &quot;hare-input-1&quot;, &quot;name&quot;: &quot;hare input&quot;, &quot;description&quot;: &quot;hare description&quot;}]&#x27;</span>

- Update both name and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;New Name&quot; --description &quot;Updated description&quot;</span>

- Update and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud input-set update --app-id hare-app --input-set-id hare-input-set \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;New Name&quot; --output updated_input_set.json</span>

**Usage**:

```console
$ cloud input-set update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --input-set-id INPUT_SET_ID`: The Nextmv Cloud input set ID to use for this action.  [env var: NEXTMV_INPUT_SET_ID; required]
* `-n, --name NAME`: A new name for the input set.
* `-d, --description DESCRIPTION`: A new description for the input set.
* `--managed-inputs MANAGED_INPUTS`: Managed inputs for the input set. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">[{&#x27;id&#x27;: &#x27;id&#x27;, &#x27;name&#x27;: &#x27;name&#x27;, &#x27;description&#x27;: &#x27;description&#x27;}]</span>.
* `-o, --output OUTPUT_PATH`: Saves the updated input set information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud instance`

Create and manage Nextmv Cloud application instances.

An application instance is a representation of a version and optional
configuration (options/parameters). Instances are the mechanism by which a
run is made. When you make a new run, the app determines which instance to
use and then uses the executable code associated to the version for the
run.

**Usage**:

```console
$ cloud instance [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud application...
* `delete`: Deletes a Nextmv Cloud application instance.
* `exists`: Check if a Nextmv Cloud application...
* `get`: Get a Nextmv Cloud application instance.
* `list`: List all instances of a Nextmv Cloud...
* `update`: Updates a Nextmv Cloud application instance.

#### `cloud instance create`

Create a new Nextmv Cloud application instance.

Use the --exist-ok flag to avoid errors when creating an instance with an
ID that already exists. This is useful for scripts that need to ensure an
instance exists without worrying about whether it was created previously.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an instance for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span> version <span style="color: #800080; text-decoration-color: #800080">v1</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance create --app-id hare-app --version-id v1 --instance-id prod</span>

- Create an instance with a specific name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance create --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id prod --name &quot;Production Instance&quot;</span>

- Create an instance with a name and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance create --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id prod --name &quot;Production Instance&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Instance for production routing jobs&quot;</span>

- Create an instance, or get it if it already exists.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance create --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id prod --exist-ok</span>

- Create an instance with configuration options.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance create --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id prod --execution-class 6c9500mb870s --priority 1</span>

- Create an instance with runtime options.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance create --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id prod --options max_duration=30 --options timeout=60</span>

**Usage**:

```console
$ cloud instance create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Cloud version ID to use for this action.  [env var: NEXTMV_VERSION_ID; required]
* `-d, --description DESCRIPTION`: An optional description for the instance.
* `-e, --exist-ok`: If an instance with the given ID already exists, do not raise an error, and simply return it.
* `-i, --instance-id INSTANCE_ID`: The ID to assign to the new instance. If not provided, a random ID will be generated.  [env var: NEXTMV_INSTANCE_ID]
* `-n, --name NAME`: Optional name for the instance. If a name is not provided, the instance ID will be used as the name.
* `-c, --content-format CONTENT_FORMAT`: The content format of the instance to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.
* `-x, --execution-class EXECUTION_CLASS`: The execution class to use for the instance.
* `--integration-id INTEGRATION_ID`: The integration ID to use for the runs of the instance, if applicable.
* `--no-queuing`: Do not queue when running the instance. Default is <span style="color: #800080; text-decoration-color: #800080">False</span>, meaning the instance&#x27;s run <span style="font-style: italic">will</span> be queued.
* `-o, --options KEY=VALUE`: Options to always use when running the instance. Format: <span style="color: #800080; text-decoration-color: #800080">key=value</span>. Pass multiple options by repeating the flag, or separating with commas.
* `--priority PRIORITY`: The priority of the runs in the instance. Priority is between 1 and 9, with 1 being the highest priority.  [default: 6]
* `-s, --secret-collection-id SECRET_COLLECTION_ID`: The secret collection ID to use for the instance, if applicable.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud instance delete`

Deletes a Nextmv Cloud application instance.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the instance with the ID <span style="color: #800080; text-decoration-color: #800080">prod</span> from application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance delete --app-id hare-app --instance-id prod</span>

- Delete the instance without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance delete --app-id hare-app --instance-id prod --yes</span>

**Usage**:

```console
$ cloud instance delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --instance-id INSTANCE_ID`: The Nextmv Cloud instance ID to use for this action.  [env var: NEXTMV_INSTANCE_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud instance exists`

Check if a Nextmv Cloud application instance exists.

This command is useful in scripting applications to verify the existence of
a Nextmv Cloud application instance by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Check if the instance with the ID <span style="color: #800080; text-decoration-color: #800080">prod</span> exists in application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance exists --app-id hare-app --instance-id prod</span>

- Check if the instance exists using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance exists --app-id hare-app --instance-id prod --profile hare</span>

**Usage**:

```console
$ cloud instance exists [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --instance-id INSTANCE_ID`: The Nextmv Cloud instance ID to use for this action.  [env var: NEXTMV_INSTANCE_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud instance get`

Get a Nextmv Cloud application instance.

This command is useful to get the attributes of an existing Nextmv Cloud
application instance by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the instance with the ID <span style="color: #800080; text-decoration-color: #800080">prod</span> from application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance get --app-id hare-app --instance-id prod</span>

- Get the instance with the ID <span style="color: #800080; text-decoration-color: #800080">prod</span> and save the information to a
  <span style="color: #800080; text-decoration-color: #800080">instance.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance get --app-id hare-app --instance-id prod --output instance.json</span>

**Usage**:

```console
$ cloud instance get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --instance-id INSTANCE_ID`: The Nextmv Cloud instance ID to use for this action.  [env var: NEXTMV_INSTANCE_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the instance information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud instance list`

List all instances of a Nextmv Cloud application.

By default this command paginates the list of instances, which means multiple
API calls may be made to retrieve all instances. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all instances of application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance list --app-id hare-app</span>

- List all instances using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance list --app-id hare-app --profile hare</span>

- List all instances and save the information to a <span style="color: #800080; text-decoration-color: #800080">instances.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance list --app-id hare-app --output instances.json</span>

- List all instances without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud instance list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the instance list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud instance update`

Updates a Nextmv Cloud application instance.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update an instance&#x27;s name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod --name &quot;Production Instance&quot;</span>

- Update an instance&#x27;s description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Instance for production routing jobs&quot;</span>

- Update an instance to use a different version.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod --version-id v2</span>

- Update an instance&#x27;s name and description at once.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Production Instance&quot; --description &quot;Instance for production routing jobs&quot;</span>

- Update an instance and save the updated information to a <span style="color: #800080; text-decoration-color: #800080">updated_instance.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Production Instance&quot; --output updated_instance.json</span>

- Update an instance&#x27;s execution class and priority.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --execution-class 6c9500mb870s --priority 1</span>

- Update an instance&#x27;s runtime options.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud instance update --app-id hare-app --instance-id prod \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --options max_duration=30 --options timeout=60</span>

**Usage**:

```console
$ cloud instance update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --instance-id INSTANCE_ID`: The Nextmv Cloud instance ID to use for this action.  [env var: NEXTMV_INSTANCE_ID; required]
* `-d, --description DESCRIPTION`: A new description for the instance.
* `--locked / --unlocked`: Whether to lock or unlock the instance. If not provided, the locked status will not be updated.
* `-n, --name NAME`: A new name for the instance.
* `-u, --output OUTPUT_PATH`: Saves the updated instance information to this location.
* `-v, --version-id VERSION_ID`: Update the instance to use a different version.
* `-c, --content-format CONTENT_FORMAT`: The content format for the instance. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.
* `-x, --execution-class EXECUTION_CLASS`: The execution class to use for the instance.
* `--integration-id INTEGRATION_ID`: The integration ID to use for the runs of the instance, if applicable.
* `--no-queuing`: Do not queue when running the instance.
* `-o, --options KEY=VALUE`: Options to always use when running the instance. Format: <span style="color: #800080; text-decoration-color: #800080">key=value</span>. Pass multiple options by repeating the flag, or separating with commas.
* `--priority PRIORITY`: The priority of the runs in the instance. Priority is between 1 and 9, with 1 being the highest priority.
* `-s, --secret-collection-id SECRET_COLLECTION_ID`: The secret collection ID to use for the instance, if applicable.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud managed-input`

Create and handle managed inputs for Nextmv Cloud applications.

A managed input is a stored input that can be referenced and used across
runs and experiments. Managed inputs help organize and reuse test cases
and datasets within your application.

**Usage**:

```console
$ cloud managed-input [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud application...
* `delete`: Deletes a Nextmv Cloud application managed...
* `get`: Get a Nextmv Cloud application managed input.
* `list`: List all managed inputs of a Nextmv Cloud...
* `update`: Updates a Nextmv Cloud application managed...

#### `cloud managed-input create`

Create a new Nextmv Cloud application managed input.

A managed input can be created from either an upload or a run. Use the
--upload-id flag to create from an upload, or the --run-id flag to create
from a run output.

You can get an upload ID by using the <span style="font-weight: bold">nextmv cloud upload</span>
<span style="font-weight: bold">create</span> command. The <span style="color: #800080; text-decoration-color: #800080">.upload_id</span> field in the
command output contains the upload ID, and the
<span style="color: #800080; text-decoration-color: #800080">.upload_url</span> field contains a pre-signed URL to upload
the data to. You may use the <span style="font-weight: bold">nextmv cloud data upload</span> command
to upload the data to the upload URL.

If no ID is provided, a unique ID will be automatically generated. If no
name is provided, the ID will be used as the name.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a managed input from an upload.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input create --app-id hare-app --upload-id upl_123456789</span>

- Create a managed input from a run.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input create --app-id hare-app --run-id run_123456789</span>

- Create a managed input with a specific ID, name, and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input create --app-id hare-app --name &quot;Test Input&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --managed-input-id inp_custom --description &quot;Test case for validation&quot; --upload-id upl_123456789</span>

- Create a managed input with custom format.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input create --app-id hare-app --name &quot;CSV Input&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --upload-id upl_123456789 --content-format csv</span>

**Usage**:

```console
$ cloud managed-input create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-c, --content-format CONTENT_FORMAT`: The content format for the managed input. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Default is <span style="color: #800080; text-decoration-color: #800080">json</span>.
* `-d, --description DESCRIPTION`: An optional description for the managed input.
* `-m, --managed-input-id MANAGED_INPUT_ID`: The ID to assign to the new managed input. If not provided, a random ID will be generated.  [env var: NEXTMV_MANAGED_INPUT_ID]
* `-n, --name NAME`: Optional name for the managed input. If not provided, the ID will be used as the name.
* `-r, --run-id RUN_ID`: ID of the run to use for the managed input. Either --upload-id or --run-id must be specified.  [env var: NEXTMV_RUN_ID]
* `-u, --upload-id UPLOAD_ID`: ID of the upload to use for the managed input. Either --upload-id or --run-id must be specified.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud managed-input delete`

Deletes a Nextmv Cloud application managed input.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the managed input with the ID <span style="color: #800080; text-decoration-color: #800080">inp_123456789</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input delete --app-id hare-app             --managed-input-id inp_123456789</span>

- Delete the managed input without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input delete --app-id hare-app --managed-input-id inp_123456789 --yes</span>

**Usage**:

```console
$ cloud managed-input delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-m, --managed-input-id MANAGED_INPUT_ID`: The Nextmv Cloud managed input ID to use for this action.  [env var: NEXTMV_MANAGED_INPUT_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud managed-input get`

Get a Nextmv Cloud application managed input.

This command is useful to get the attributes of an existing Nextmv Cloud
application managed input by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the managed input with the ID <span style="color: #800080; text-decoration-color: #800080">inp_123456789</span> from application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input get --app-id hare-app --managed-input-id inp_123456789</span>

- Get the managed input with the ID <span style="color: #800080; text-decoration-color: #800080">inp_123456789</span> and save the information to a
  <span style="color: #800080; text-decoration-color: #800080">managed_input.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input get --app-id hare-app --managed-input-id inp_123456789             --output managed_input.json</span>

**Usage**:

```console
$ cloud managed-input get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-m, --managed-input-id MANAGED_INPUT_ID`: The Nextmv Cloud managed input ID to use for this action.  [env var: NEXTMV_MANAGED_INPUT_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the managed input information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud managed-input list`

List all managed inputs of a Nextmv Cloud application.

By default this command paginates the list of inputs, which means multiple
API calls may be made to retrieve all inputs. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all managed inputs of application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input list --app-id hare-app</span>

- List all managed inputs using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input list --app-id hare-app --profile hare</span>

- List all managed inputs and save the information to a <span style="color: #800080; text-decoration-color: #800080">managed_inputs.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input list --app-id hare-app --output managed_inputs.json</span>

- List all managed inputs without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud managed-input list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the managed input list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud managed-input update`

Updates a Nextmv Cloud application managed input.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update a managed input&#x27;s name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input update --app-id hare-app             --managed-input-id inp_123456789 --name &quot;Updated Test Input&quot;</span>

- Update a managed input&#x27;s description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123456789 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Updated test case for validation&quot;</span>

- Update a managed input&#x27;s name and description at once.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123456789 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Updated Test Input&quot; --description &quot;Updated test case for validation&quot;</span>

- Update a managed input and save the updated information to a <span style="color: #800080; text-decoration-color: #800080">updated_managed_input.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud managed-input update --app-id hare-app --managed-input-id inp_123456789 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Updated Test Input&quot; --output updated_managed_input.json</span>

**Usage**:

```console
$ cloud managed-input update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-m, --managed-input-id MANAGED_INPUT_ID`: The Nextmv Cloud managed input ID to use for this action.  [env var: NEXTMV_MANAGED_INPUT_ID; required]
* `-d, --description DESCRIPTION`: A new description for the managed input.
* `-n, --name NAME`: A new name for the managed input.
* `-o, --output OUTPUT_PATH`: Saves the updated managed input information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud marketplace`

Interact with the Nextmv Marketplace.

The Nextmv Marketplace is a platform where users can discover,
subscribe to, and run decision applications for various use cases.

**Usage**:

```console
$ cloud marketplace [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `app`: Create and manage Nextmv Marketplace...
* `subscription`: Manage Nextmv Marketplace subscriptions.
* `version`: Create and manage Nextmv Marketplace...

#### `cloud marketplace app`

Create and manage Nextmv Marketplace applications.

Unlike the <span style="font-weight: bold">nextmv cloud app</span> command set, this one can be used
to manage Marketplace applications instances explicitly.

**Usage**:

```console
$ cloud marketplace app [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Marketplace application.
* `get`: Get a Nextmv Marketplace application.
* `list`: List all Nextmv Marketplace applications.
* `update`: Update a Nextmv Marketplace application.

##### `cloud marketplace app create`

Create a new Nextmv Marketplace application.

Marketplace applications are created under a partner ID and are based on a
reference application. The reference application serves as a template,
providing the structure and configuration for the new marketplace listing.

Applications can be enriched with categories and features to improve
discoverability in the Nextmv Marketplace. If no app ID is provided, a
random ID will be generated.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a marketplace application with the title <span style="color: #800080; text-decoration-color: #800080">Hare Routing</span>. A random ID will be generated.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app create --partner-id fluffy-comrade \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --reference-app-id hare-app --title &quot;Hare Routing&quot;</span>

- Create a marketplace application with a specific ID <span style="color: #800080; text-decoration-color: #800080">marketplace-hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app create --partner-id fluffy-comrade \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --reference-app-id hare-app --title &quot;Hare Routing&quot; --app-id marketplace-hare</span>

- Create a marketplace application with a description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app create --partner-id fluffy-comrade \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --reference-app-id hare-app --title &quot;Hare Routing&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Advanced routing solution for hare logistics&quot;</span>

- Create a marketplace application with categories.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app create --partner-id fluffy-comrade \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --reference-app-id hare-app --title &quot;Hare Routing&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --categories routing --categories logistics</span>

- Create a marketplace application with features.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app create --partner-id fluffy-comrade \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --reference-app-id hare-app --title &quot;Hare Routing&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --features &quot;real-time optimization&quot; --features &quot;multi-vehicle support&quot;</span>

- Create a marketplace application with all options.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app create --partner-id fluffy-comrade \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --reference-app-id hare-app --title &quot;Hare Routing&quot; --app-id marketplace-hare \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Advanced routing solution&quot; --categories routing \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --features &quot;real-time optimization&quot;</span>

**Usage**:

```console
$ cloud marketplace app create [OPTIONS]
```

**Options**:

* `-n, --partner-id PARTNER_ID`: The partner ID to create the application under.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-r, --reference-app-id REFERENCE_APP_ID`: The ID of an existing application to use as a reference for the new application.  [required]
* `-t, --title TITLE`: The title of the application to create.  [required]
* `-a, --app-id APP_ID`: An optional ID for the Nextmv Marketplace application. If not provided, a random ID will be generated.  [env var: NEXTMV_MARKETPLACE_APP_ID]
* `-c, --categories CATEGORIES`: Optional categories for the application. Pass multiple categories by repeating the flag.
* `-d, --description DESCRIPTION`: An optional description for the application.
* `-f, --features FEATURES`: Optional features for the application. Pass multiple features by repeating the flag.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace app get`

Get a Nextmv Marketplace application.


<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the marketplace application with the ID <span style="color: #800080; text-decoration-color: #800080">marketplace-hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app get --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare</span>

- Get the marketplace application and save the information to an <span style="color: #800080; text-decoration-color: #800080">app.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app get --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --output app.json</span>

**Usage**:

```console
$ cloud marketplace app get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Marketplace application ID to use for this action.  [env var: NEXTMV_MARKETPLACE_APP_ID; required]
* `-n, --partner-id PARTNER_ID`: The partner ID to use for this action.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the app information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace app list`

List all Nextmv Marketplace applications.

By default, this command lists all marketplace applications. Use the
--partner-id flag to filter applications belonging to a specific partner.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all marketplace applications.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app list</span>

- List all applications for a specific partner.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app list --partner-id my-partner</span>

- List all applications using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app list --profile hare</span>

- List all applications and save the information to an <span style="color: #800080; text-decoration-color: #800080">apps.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app list --output apps.json</span>

**Usage**:

```console
$ cloud marketplace app list [OPTIONS]
```

**Options**:

* `-n, --partner-id PARTNER_ID`: Only the apps belonging to this partner will be listed. If not provided, all apps are listed.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID]
* `-o, --output OUTPUT_PATH`: Saves the app list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace app update`

Update a Nextmv Marketplace application.

This command allows you to update the attributes of an existing marketplace
application, including its title, description, categories, features, and
state. Only the fields you specify will be updated; all other fields will
remain unchanged.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the title of a marketplace application.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --title &quot;Advanced Hare Routing&quot;</span>

- Update the description of a marketplace application.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --description &quot;Enterprise-grade routing solution&quot;</span>

- Update categories and features.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --categories routing --categories logistics \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --features &quot;real-time optimization&quot;</span>

- Update the state of a marketplace application.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --state released</span>

- Update multiple fields and save the result to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace app update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --title &quot;New Title&quot; --state released \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output app.json</span>

**Usage**:

```console
$ cloud marketplace app update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Marketplace application ID to use for this action.  [env var: NEXTMV_MARKETPLACE_APP_ID; required]
* `-n, --partner-id PARTNER_ID`: The partner ID to use for this action.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-c, --categories CATEGORIES`: Optional categories for the application. Pass multiple categories by repeating the flag.
* `-d, --description DESCRIPTION`: An optional description for the application.
* `-f, --features FEATURES`: Optional features for the application. Pass multiple features by repeating the flag.
* `-o, --output OUTPUT_PATH`: Saves the app information to this location.
* `-s, --state STATE`: The state of the application. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">released</span>, <span style="color: #800080; text-decoration-color: #800080">pre-release</span>, and <span style="color: #800080; text-decoration-color: #800080">retracted</span>.
* `-t, --title TITLE`: The title of the application to update.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud marketplace subscription`

Manage Nextmv Marketplace subscriptions.

These commands allow you to view and manage your subscriptions to
Marketplace applications.

**Usage**:

```console
$ cloud marketplace subscription [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new marketplace subscription.
* `delete`: Delete a marketplace subscription.
* `get`: Get a marketplace subscription.
* `list`: List all marketplace subscriptions.

##### `cloud marketplace subscription create`

Create a new marketplace subscription.

Subscribe to a marketplace application by providing the subscription ID,
which combines the partner ID and application ID in the format
<span style="color: #800080; text-decoration-color: #800080">&lt;PARTNER_ID&gt;-&lt;APP_ID&gt;</span>. This allows you to access and use
the marketplace application in your account.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Subscribe to a marketplace application.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription create --subscription-id my-partner-marketplace-hare</span>

- Subscribe to a marketplace application using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription create --subscription-id my-partner-marketplace-hare \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --profile hare</span>

**Usage**:

```console
$ cloud marketplace subscription create [OPTIONS]
```

**Options**:

* `-s, --subscription-id SUBSCRIPTION_ID`: The ID of the marketplace application and partner to subscribe to. Format of the subscription ID: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&lt;PARTNER_ID&gt;-&lt;APP_ID&gt;</span>.  [env var: NEXTMV_MARKETPLACE_SUBSCRIPTION_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace subscription delete`

Delete a marketplace subscription.

Use the --yes flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete a marketplace subscription.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription delete --subscription-id my-partner-marketplace-hare</span>

- Delete a marketplace subscription without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription delete --subscription-id my-partner-marketplace-hare \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --yes</span>

**Usage**:

```console
$ cloud marketplace subscription delete [OPTIONS]
```

**Options**:

* `-s, --subscription-id SUBSCRIPTION_ID`: The Nextmv Marketplace subscription ID to use for this action. Format of the subscription ID: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&lt;PARTNER_ID&gt;-&lt;APP_ID&gt;</span>.  [env var: NEXTMV_MARKETPLACE_SUBSCRIPTION_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

##### `cloud marketplace subscription get`

Get a marketplace subscription.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get a marketplace subscription.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription get --subscription-id my-partner-marketplace-hare</span>

- Get a marketplace subscription and save the information to a <span style="color: #800080; text-decoration-color: #800080">subscription.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription get --subscription-id my-partner-marketplace-hare \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output subscription.json</span>

**Usage**:

```console
$ cloud marketplace subscription get [OPTIONS]
```

**Options**:

* `-s, --subscription-id SUBSCRIPTION_ID`: The Nextmv Marketplace subscription ID to use for this action. Format of the subscription ID: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&lt;PARTNER_ID&gt;-&lt;APP_ID&gt;</span>.  [env var: NEXTMV_MARKETPLACE_SUBSCRIPTION_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the subscription information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace subscription list`

List all marketplace subscriptions.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all marketplace subscriptions.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription list</span>

- List all subscriptions using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription list --profile hare</span>

- List all subscriptions and save the information to a <span style="color: #800080; text-decoration-color: #800080">subscriptions.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace subscription list --output subscriptions.json</span>

**Usage**:

```console
$ cloud marketplace subscription list [OPTIONS]
```

**Options**:

* `-o, --output OUTPUT_PATH`: Saves the subscription list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud marketplace version`

Create and manage Nextmv Marketplace application versions.

**Usage**:

```console
$ cloud marketplace version [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new marketplace version for an...
* `get`: Get a marketplace version for an application.
* `list`: List all versions of a marketplace...
* `update`: Update a marketplace version&#x27;s change log.

##### `cloud marketplace version create`

Create a new marketplace version for an application.

Marketplace versions are created by referencing an existing version from
the underlying application. The change log provides information about what
has changed in this marketplace version. If no version ID is provided, a
random ID will be generated.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a marketplace version with change log entries. A random ID will be generated.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version create --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --reference-version-id v1.0.0 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Improved performance&quot; --change-log &quot;Fixed bug in routing&quot;</span>

- Create a marketplace version with a specific version ID.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version create --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --reference-version-id v1.0.0 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --version-id mkt-v1 --change-log &quot;Initial marketplace release&quot;</span>

- Create a marketplace version with multiple change log entries.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version create --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --reference-version-id v2.0.0 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Added new features&quot; --change-log &quot;Performance improvements&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Updated documentation&quot;</span>

**Usage**:

```console
$ cloud marketplace version create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Marketplace application ID to use for this action.  [env var: NEXTMV_MARKETPLACE_APP_ID; required]
* `-c, --change-log CHANGE_LOG`: Changelog entries for the version. Pass multiple entries by repeating the flag.  [required]
* `-n, --partner-id PARTNER_ID`: The partner ID to use for this action.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-r, --reference-version-id REFERENCE_VERSION_ID`: The ID of the version to reference.  [required]
* `-v, --version-id VERSION_ID`: The ID to assign to the new marketplace version. If not provided, a random ID will be generated.  [env var: NEXTMV_MARKETPLACE_VERSION_ID]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace version get`

Get a marketplace version for an application.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the marketplace version with the ID <span style="color: #800080; text-decoration-color: #800080">mkt-v1</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version get --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --version-id mkt-v1</span>

- Get the marketplace version and save the information to a <span style="color: #800080; text-decoration-color: #800080">version.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version get --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --version-id mkt-v1 --output version.json</span>

**Usage**:

```console
$ cloud marketplace version get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Marketplace application ID to use for this action.  [env var: NEXTMV_MARKETPLACE_APP_ID; required]
* `-n, --partner-id PARTNER_ID`: The partner ID to use for this action.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Marketplace version ID to use for this action.  [env var: NEXTMV_MARKETPLACE_VERSION_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the version information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace version list`

List all versions of a marketplace application.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all marketplace versions for an application.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version list --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare</span>

- List all versions using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version list --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --profile hare</span>

- List all versions and save the information to a <span style="color: #800080; text-decoration-color: #800080">versions.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version list --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --output versions.json</span>

**Usage**:

```console
$ cloud marketplace version list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Marketplace application ID to use for this action.  [env var: NEXTMV_MARKETPLACE_APP_ID; required]
* `-n, --partner-id PARTNER_ID`: The partner ID to use for this action.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the version list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

##### `cloud marketplace version update`

Update a marketplace version&#x27;s change log.

This command allows you to update the change log entries for an existing
marketplace version. Pass multiple change log entries by repeating the
--change-log flag.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update a version&#x27;s change log with a single entry.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --version-id mkt-v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Fixed critical bug in routing algorithm&quot;</span>

- Update a version&#x27;s change log with multiple entries.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --version-id mkt-v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Performance improvements&quot; --change-log &quot;Added new features&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Updated documentation&quot;</span>

- Update a version and save the updated information to a <span style="color: #800080; text-decoration-color: #800080">updated_version.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud marketplace version update --partner-id my-partner \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --app-id marketplace-hare --version-id mkt-v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --change-log &quot;Bug fixes&quot; --output updated_version.json</span>

**Usage**:

```console
$ cloud marketplace version update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Marketplace application ID to use for this action.  [env var: NEXTMV_MARKETPLACE_APP_ID; required]
* `-n, --partner-id PARTNER_ID`: The partner ID to use for this action.  [env var: NEXTMV_MARKETPLACE_PARTNER_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Marketplace version ID to use for this action.  [env var: NEXTMV_MARKETPLACE_VERSION_ID; required]
* `-c, --change-log CHANGE_LOG`: Changelog entries for the version. Pass multiple entries by repeating the flag.  [required]
* `-o, --output OUTPUT_PATH`: Saves the updated version information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud run`

Create and manage Nextmv Cloud application runs.

A run represents the execution of a decision model within a Nextmv Cloud
application. Each run takes an input, processes it using the decision model,
and produces an output.

**Usage**:

```console
$ cloud run [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `cancel`: Cancel a queued/running Nextmv Cloud...
* `clone`: Clone an existing Nextmv Cloud application...
* `compare`: Compare multiple Nextmv Cloud application...
* `create`: Create a new Nextmv Cloud application run.
* `delete`: Deletes a Nextmv Cloud application run.
* `get`: Get the result (output) of a Nextmv Cloud...
* `information`: Get the information of a Nextmv Cloud...
* `input`: Get the input of a Nextmv Cloud...
* `list`: Get the list of runs for a Nextmv Cloud...
* `logs`: Get the logs of a Nextmv Cloud application...
* `metadata`: This command is deprecated, use... (DEPRECATED)
* `track`: Track an external run as a Nextmv Cloud...

#### `cloud run cancel`

Cancel a queued/running Nextmv Cloud application run.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Cancel the run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span> belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run cancel --app-id hare-app --run-id burrow-123</span>

- Cancel the run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span> belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run cancel --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run cancel [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run clone`

Clone an existing Nextmv Cloud application run.

All information of the original (cloned) run will be reused. You may
override any information you wish, such as the input, content format, or
instance, for example. All the options for creating the new run work the
same way as in the <span style="font-weight: bold">nextmv cloud run create</span> command. You may
inspect the documentation of that command for more details on what each
option does.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>,
  reusing the original run&#x27;s input.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>,
  overriding the input with a <span style="color: #800080; text-decoration-color: #800080">json</span> file via <span style="color: #800080; text-decoration-color: #800080">stdin</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">cat input.json | nextmv cloud run clone --app-id hare-app --cloned-run-id run-123</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>,
  overriding the input with an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --input input.json</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete and print the result to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --wait</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Tail the run&#x27;s logs, streaming to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --tail</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete and write the result to an <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --output output.json</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete, and write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --logs logs.log</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Wait for the run to complete. Tail
  the run&#x27;s logs, streaming to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
  Write the result to an <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --tail --logs logs.log \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json </span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, overriding the input with a
  <span style="color: #800080; text-decoration-color: #800080">multi-file</span> directory, using the <span style="color: #800080; text-decoration-color: #800080">default</span> instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --input inputs \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --instance-id default</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, overriding the input with a
  <span style="color: #800080; text-decoration-color: #800080">multi-file</span> directory, using the <span style="color: #800080; text-decoration-color: #800080">burrow</span> instance.
  Wait for the run to complete and download the result files to an <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --input inputs --instance-id burrow \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output outputs</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from app <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, overriding the input with a
  <span style="color: #800080; text-decoration-color: #800080">Nextmv managed</span> input with ID <span style="color: #800080; text-decoration-color: #800080">carrot-input</span>.
  Wait for the run to complete and download the result files to an <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run clone --app-id hare-app --cloned-run-id run-123 --managed-input-id carrot-input \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output outputs</span>

**Usage**:

```console
$ cloud run clone [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --cloned-run-id CLONED_RUN_ID`: The original Nextmv run ID that you want to clone.  [env var: NEXTMV_CLONED_RUN_ID; required]
* `-i, --input INPUT_PATH`: The input path to use. File or directory depending on content format. Uses <span style="color: #800080; text-decoration-color: #800080">stdin</span> if not defined. Can be a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file for multi-file content format.
* `-m, --managed-input-id MANAGED_INPUT_ID`: The Nextmv Cloud managed input ID to use as the input for the run.  [env var: NEXTMV_MANAGED_INPUT_ID]
* `-l, --logs LOGS_PATH`: Waits for the run to complete and saves the logs to this location.
* `-u, --output OUTPUT_PATH`: Waits for the run to complete and save the output to this location. A file or directory will be created depending on content format.
* `-t, --tail`: Tail the logs until the run completes. Logs are streamed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Specify log output location with --logs.
* `-w, --wait`: Wait for the run to complete. Run result is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span> for <span style="color: #800080; text-decoration-color: #800080">json</span>, to a dir for <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Specify output location with --output.
* `-c, --content-format CONTENT_FORMAT`: The content format of the run to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.
* `-d, --definition-id DEFINITION_ID`: The definition ID to use for the run. Required for certain run types like ensemble runs.
* `--description DESCRIPTION`: An optional description for the new run.
* `-e, --execution-class EXECUTION_CLASS`: The execution class to use for the run, if applicable.
* `--instance-id INSTANCE_ID`: The instance ID to use for the run.
* `--integration-id INTEGRATION_ID`: The integration ID to use for the run, if applicable.
* `-n, --name NAME`: An optional name for the new run.
* `--no-queuing`: Do not queue run. Default is <span style="color: #800080; text-decoration-color: #800080">False</span>, meaning the run <span style="font-style: italic">will</span> be queued.
* `-o, --options KEY=VALUE`: Options passed to the run. Format: <span style="color: #800080; text-decoration-color: #800080">key=value</span>. Pass multiple options by repeating the flag, or separating with commas.
* `--priority PRIORITY`: The priority of the run. Priority is between 1 and 9, with 1 being the highest priority.
* `--run-type RUN_TYPE`: The type of run to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">standard</span>, <span style="color: #800080; text-decoration-color: #800080">external</span>, and <span style="color: #800080; text-decoration-color: #800080">ensemble</span>.
* `-s, --secret-collection-id SECRET_COLLECTION_ID`: The secret collection ID to use for the run, if applicable.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run compare`

Compare multiple Nextmv Cloud application runs.

By default this command prints a human-readable table to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. You may use the --flat option to print the
comparison result to <span style="color: #800080; text-decoration-color: #800080">stdout</span> as <span style="color: #800080; text-decoration-color: #800080">json</span>
instead. When the --output option is used, the --flat flag is automatically
activated and the result is saved as <span style="color: #800080; text-decoration-color: #800080">json</span>.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Compare two runs belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>
  repeating the --run-ids flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run compare --app-id hare-app --run-ids fluff --run-ids white</span>

- Compare three runs belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>
  separating the run IDs with commas.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run compare --app-id hare-app --run-ids fluff,white,thumper</span>

- Compare two runs and print the result as <span style="color: #800080; text-decoration-color: #800080">json</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run compare --app-id hare-app --run-ids fluff,white --flat</span>

- Compare two runs and save the result to a file named <span style="color: #800080; text-decoration-color: #800080">comparison.json</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run compare --app-id hare-app --run-ids fluff,white --output comparison.json</span>

**Usage**:

```console
$ cloud run compare [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-ids RUN_IDS`: List of run IDs to compare. Pass multiple run IDs by repeating the flag, or separating with commas.  [required]
* `-f, --flat`: Print the comparison result as <span style="color: #800080; text-decoration-color: #800080">json</span>, instead of a table.
* `-o, --output OUTPUT_PATH`: Saves the comparison result to this location. Activates the --flat option.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run create`

Create a new Nextmv Cloud application run.

Input for the run should be given through <span style="color: #800080; text-decoration-color: #800080">stdin</span>, the --input flag,
or a Nextmv managed input by passing its ID into the --managed-input-id flag.
When using the --input flag, the value can be one of the following:

- <span style="color: #808000; text-decoration-color: #808000">&lt;FILE_PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">file</span> containing
  the input data. Use with the <span style="color: #800080; text-decoration-color: #800080">json</span> content format.
- <span style="color: #808000; text-decoration-color: #808000">&lt;DIR_PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">directory</span>
  containing the input data files. Use with the
  <span style="color: #800080; text-decoration-color: #800080">multi-file</span> content format.
- <span style="color: #808000; text-decoration-color: #808000">&lt;.tar.gz PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file
  containing tarred input data files. Use with the
  <span style="color: #800080; text-decoration-color: #800080">multi-file</span> content format.

The CLI determines how to send the input to the application based on the
value.

Use the --wait flag to wait for the run to complete, polling for results.
Using the --output flag will also activate waiting, and allows you to
specify a destination (file or dir) for the output, depending on the
content type.

Use the --tail flag to stream logs to <span style="color: #800080; text-decoration-color: #800080">stderr</span> until the
run completes. Using the --logs flag will also activate waiting, and allows
you to specify a file to write the logs to.

An application run executes against a specific instance. An instance
represents the combination of executable code and configuration. You can
specify the instance with the --instance-id flag. These are the possible
values for this flag:

- <span style="color: #808000; text-decoration-color: #808000">unspecified</span>: Run against the default instance of the
  application. When an application is created, the default instance is <span style="color: #800080; text-decoration-color: #800080">latest</span>.
- <span style="color: #808000; text-decoration-color: #808000">latest</span>: uses the special <span style="color: #800080; text-decoration-color: #800080">latest</span>
  instance of the application. This corresponds to the latest pushed
  executable.
- <span style="color: #808000; text-decoration-color: #808000">&lt;INSTANCE_ID&gt;</span>: uses the instance with the given ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input via <span style="color: #800080; text-decoration-color: #800080">stdin</span>, from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file,
  and submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">cat input.json | nextmv cloud run create --app-id hare-app</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input input.json</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
  Wait for the run to complete and print the result to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input input.json --wait</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
  Tail the run&#x27;s logs, streaming to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input input.json --tail</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
  Wait for the run to complete and write the result to an <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input input.json --output output.json</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
  Wait for the run to complete, and write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input input.json --logs logs.log</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and submit a run to an app with
  ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance. Wait for the run to complete. Tail
  the run&#x27;s logs, streaming to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
  Write the result to an <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input input.json --tail --logs logs.log \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json </span>

- Read a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">default</span> instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input inputs --instance-id default</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">default</span> instance.
  Wait for the run to complete, and save the results to the default location (a directory named after the run ID).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input inputs --instance-id default --wait</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">burrow</span> instance.
  Wait for the run to complete and download the result files to an <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --input inputs --instance-id burrow --output outputs</span>

- Set the run to use a <span style="color: #800080; text-decoration-color: #800080">Nextmv managed</span> input with ID <span style="color: #800080; text-decoration-color: #800080">carrot-input</span>,
  and submit a run to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> instance.
  Wait for the run to complete and download the result files to an <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run create --app-id hare-app --managed-input-id carrot-input --output outputs</span>

**Usage**:

```console
$ cloud run create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --input INPUT_PATH`: The input path to use. File or directory depending on content format. Uses <span style="color: #800080; text-decoration-color: #800080">stdin</span> if not defined. Can be a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file for multi-file content format.
* `-m, --managed-input-id MANAGED_INPUT_ID`: The Nextmv Cloud managed input ID to use as the input for the run.  [env var: NEXTMV_MANAGED_INPUT_ID]
* `-l, --logs LOGS_PATH`: Waits for the run to complete and saves the logs to this location.
* `-u, --output OUTPUT_PATH`: Waits for the run to complete and save the output to this location. A file or directory will be created depending on content format.
* `-t, --tail`: Tail the logs until the run completes. Logs are streamed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Specify log output location with --logs.
* `-w, --wait`: Wait for the run to complete. Run result is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span> for <span style="color: #800080; text-decoration-color: #800080">json</span>, to a dir for <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Specify output location with --output.
* `-c, --content-format CONTENT_FORMAT`: The content format of the run to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.
* `-d, --definition-id DEFINITION_ID`: The definition ID to use for the run. Setting it converts the run into an ensemble run.
* `--description DESCRIPTION`: An optional description for the new run.
* `-e, --execution-class EXECUTION_CLASS`: The execution class to use for the run, if applicable.
* `--instance-id INSTANCE_ID`: The instance ID to use for the run.
* `--integration-id INTEGRATION_ID`: The integration ID to use for the run, if applicable.
* `-n, --name NAME`: An optional name for the new run.
* `--no-queuing`: Do not queue run. Default is <span style="color: #800080; text-decoration-color: #800080">False</span>, meaning the run <span style="font-style: italic">will</span> be queued.
* `-o, --options KEY=VALUE`: Options passed to the run. Format: <span style="color: #800080; text-decoration-color: #800080">key=value</span>. Pass multiple options by repeating the flag, or separating with commas.
* `--priority PRIORITY`: The priority of the run. Priority is between 1 and 9, with 1 being the highest priority.  [default: 6]
* `-r, --run-type RUN_TYPE`: The type of run to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">standard</span>, <span style="color: #800080; text-decoration-color: #800080">external</span>, and <span style="color: #800080; text-decoration-color: #800080">ensemble</span>.  [default: standard]
* `-s, --secret-collection-id SECRET_COLLECTION_ID`: The secret collection ID to use for the run, if applicable.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run delete`

Deletes a Nextmv Cloud application run.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span> belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run delete --app-id hare-app --run-id burrow-123</span>

- Delete the run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span> belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run delete --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run get`

Get the result (output) of a Nextmv Cloud application run.

Use the --wait flag to wait for the run to complete, polling
for results. Using the --output flag will also activate
waiting, and allows you to specify a destination (file or dir) for the
output, depending on the content type.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run get --app-id hare-app --run-id burrow-123</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Wait for the run to complete if necessary.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run get --app-id hare-app --run-id burrow-123 --wait</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. The app is a <span style="color: #800080; text-decoration-color: #800080">json</span> app.
  Save the results to a <span style="color: #800080; text-decoration-color: #800080">results.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run get --app-id hare-app --run-id burrow-123 --output results.json</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. The app is a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> app.
  Save the results to the <span style="color: #800080; text-decoration-color: #800080">results</span> dir.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run get --app-id hare-app --run-id burrow-123 --output results</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run get --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-o, --output OUTPUT_PATH`: Waits for the run to complete and save the output to this location. A file or directory will be created depending on content format.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the run to complete. Run result is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span> for <span style="color: #800080; text-decoration-color: #800080">json</span>, to a dir for <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run information`

Get the information of a Nextmv Cloud application run.

By default, the information (including metadata) is fetched and printed to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. Use the --output flag to save the information to
a file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the information of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Information is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run information --app-id hare-app --run-id burrow-123</span>

- Get the information of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the information to a <span style="color: #800080; text-decoration-color: #800080">information.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run information --app-id hare-app --run-id burrow-123 --output information.json</span>

- Get the information of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run information --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run information [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run input`

Get the input of a Nextmv Cloud application run.

By default, the input is fetched and printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
Use the --output flag to save the input to a file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the input of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Input is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run input --app-id hare-app --run-id burrow-123</span>

- Get the input of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the input to a <span style="color: #800080; text-decoration-color: #800080">input.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run input --app-id hare-app --run-id burrow-123 --output input.json</span>

- Get the input of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run input --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run input [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the input to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run list`

Get the list of runs for a Nextmv Cloud application.

By default, the list of runs is fetched and printed to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. Use the --output flag to save the list to a
file. You can use the optional --status flag to filter runs by their
status. This command paginates the list of runs, which means multiple API
calls may be made to retrieve all runs. You may use the --no-pagination
option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. List is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run list --app-id hare-app</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the list to a
  <span style="color: #800080; text-decoration-color: #800080">runs.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run list --app-id hare-app --output runs.json</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run list --app-id hare-app --profile hare</span>

- Get the list of <span style="color: #800080; text-decoration-color: #800080">queued</span> runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run list --app-id hare-app --status queued</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud run list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of runs to this location.
* `-s, --status STATUS`: Filter runs by their status. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">canceled</span>, <span style="color: #800080; text-decoration-color: #800080">failed</span>, <span style="color: #800080; text-decoration-color: #800080">none</span>, <span style="color: #800080; text-decoration-color: #800080">queued</span>, <span style="color: #800080; text-decoration-color: #800080">running</span>, and <span style="color: #800080; text-decoration-color: #800080">succeeded</span>.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run logs`

Get the logs of a Nextmv Cloud application run.

By default, the logs are fetched and printed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
Use the --tail flag to stream logs to <span style="color: #800080; text-decoration-color: #800080">stderr</span> until the
run completes. Using the --output flag will also activate waiting, and
allows you to specify a file to write the logs to.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Logs are printed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run logs --app-id hare-app --run-id burrow-123</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Tail the logs until the run completes.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run logs --app-id hare-app --run-id burrow-123 --tail</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run logs --app-id hare-app --run-id burrow-123 --output logs.log</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Tail the logs and save them to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run logs --app-id hare-app --run-id burrow-123 --tail --output logs.log</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run logs --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run logs [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-o, --output OUTPUT_PATH`: Waits for the run to complete and saves the logs to this location.
* `-t, --tail`: Tail the logs until the run completes. Logs are streamed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Specify log output location with --output.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run metadata`

This command is deprecated, use <span style="font-weight: bold">nextmv cloud run information</span> instead.

Get the metadata of a Nextmv Cloud application run.

By default, the metadata is fetched and printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
Use the --output flag to save the metadata to a file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the metadata of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Metadata is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run metadata --app-id hare-app --run-id burrow-123</span>

- Get the metadata of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the metadata to a <span style="color: #800080; text-decoration-color: #800080">metadata.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run metadata --app-id hare-app --run-id burrow-123 --output metadata.json</span>

- Get the metadata of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run metadata --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ cloud run metadata [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the metadata to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud run track`

Track an external run as a Nextmv Cloud application run.

Please see the help of the --content-type option for details on valid
content types.

If the content type is <span style="color: #800080; text-decoration-color: #800080">json</span>, then input for the run can
be given through <span style="color: #800080; text-decoration-color: #800080">stdin</span>. The --input option allows you to
specify a file or directory path for the input, instead of using
<span style="color: #800080; text-decoration-color: #800080">stdin</span>. In the case of <span style="color: #800080; text-decoration-color: #800080">multi-file</span>
content type, the input must be given through a directory specified via the
--input option.

The --output option allows you to specify a file or directory path for the
output of the run. The behavior depends on the content type. If the content
type is <span style="color: #800080; text-decoration-color: #800080">json</span>, then a file path must be provided. If the
content type is <span style="color: #800080; text-decoration-color: #800080">multi-file</span>, then a directory path must
be provided.

Run logs, assets, and metrics can be provided via files using the
--logs, --assets, and --metrics options, respectively. Assets and
metrics must be provided as <span style="color: #800080; text-decoration-color: #800080">json</span> files, while logs
must be provided as a utf-8 encoded text file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> <span style="color: #800080; text-decoration-color: #800080">json</span> run via <span style="color: #800080; text-decoration-color: #800080">stdin</span>
  input, for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">cat input.json | nextmv cloud run track --app-id hare-app --status succeeded</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> <span style="color: #800080; text-decoration-color: #800080">json</span> run with input from an
  <span style="color: #800080; text-decoration-color: #800080">input.json</span> file and output from an
  <span style="color: #800080; text-decoration-color: #800080">output.json</span> file, for an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status succeeded --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> <span style="color: #800080; text-decoration-color: #800080">json</span> run including logs from a
  <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file, for an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status succeeded --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json --logs logs.log</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> <span style="color: #800080; text-decoration-color: #800080">json</span> run with assets and metrics
  from <span style="color: #800080; text-decoration-color: #800080">json</span> files, for an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status succeeded --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json --assets assets.json --metrics metrics.json</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">failed</span> run with an error message, for an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status failed --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --error-msg &quot;Solver timed out&quot;</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> <span style="color: #800080; text-decoration-color: #800080">multi-file</span> run from an
  <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory with output to an
  <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory, for an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>, using the <span style="color: #800080; text-decoration-color: #800080">default</span>
  instance.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status succeeded --input inputs \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output outputs --content-type multi-file --instance-id default</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> run with a name, description, and duration, for an app
  with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status succeeded --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json --name &quot;Production run&quot; --description &quot;Weekly optimization&quot; --duration 5000</span>

- Track a <span style="color: #800080; text-decoration-color: #800080">successful</span> <span style="color: #800080; text-decoration-color: #800080">json</span> run with all available options,
  for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud run track --app-id hare-app --status succeeded --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json --logs logs.log --assets assets.json --metrics metrics.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            --name &quot;Full run&quot; --description &quot;Complete example&quot; --duration 10000 --instance-id burrow</span>

**Usage**:

```console
$ cloud run track [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-o, --output OUTPUT_PATH`: The output of the run being tracked. A file or directory depending on content format.  [required]
* `-s, --status STATUS`: Status of the tracked run. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">succeeded</span> and <span style="color: #800080; text-decoration-color: #800080">failed</span>.  [required]
* `--assets ASSETS_PATH`: The assets of the run being tracked. A <span style="color: #800080; text-decoration-color: #800080">json</span> file to read the assets from.
* `-c, --content-format CONTENT_FORMAT`: The content format of the run to track. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.  [default: json]
* `--description DESCRIPTION`: An optional description for the tracked run.
* `-d, --duration DURATION_MS`: The duration of the run being tracked, in milliseconds.  [default: 0]
* `-e, --error-msg ERROR_MESSAGE`: An error message if the run being tracked failed.
* `-i, --input INPUT_PATH`: The input of the run being tracked. File or directory depending on content format. Uses <span style="color: #800080; text-decoration-color: #800080">stdin</span> if not defined.
* `-l, --logs LOGS_PATH`: The logs of the run being tracked. A utf-8 encoded text file to read the logs from.
* `-n, --name NAME`: An optional name for the tracked run.
* `--statistics STATISTICS_PATH`: <span style="color: #800000; text-decoration-color: #800000">(deprecated) Use --metrics instead.</span> The statistics of the run being tracked. A <span style="color: #800080; text-decoration-color: #800080">json</span> file to read the statistics from.
* `--metrics METRICS_PATH`: The metrics of the run being tracked. A <span style="color: #800080; text-decoration-color: #800080">json</span> file to read the metrics from.
* `--instance-id INSTANCE_ID`: The instance ID to use for the run.  [default: latest]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud scenario`

Create and manage Nextmv Cloud scenario tests.

**Usage**:

```console
$ cloud scenario [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud scenario test.
* `delete`: Deletes a Nextmv Cloud scenario test.
* `get`: Get a Nextmv Cloud scenario test,...
* `list`: List all Nextmv Cloud scenario tests for...
* `metadata`: Get metadata for a Nextmv Cloud scenario...
* `update`: Update a Nextmv Cloud scenario test.

#### `cloud scenario create`

Create a new Nextmv Cloud scenario test.

A scenario test allows you to run multiple scenarios with different inputs,
instances/versions, and configurations in a single test.

Use the --wait flag to wait for the scenario test to complete,
polling for results. Using the --output flag will also
activate waiting, and allows you to specify a destination file for the
results.

<span style="font-weight: bold; text-decoration: underline">Scenarios</span>

Scenarios are provided as <span style="color: #800080; text-decoration-color: #800080">json</span> objects using the
--scenarios flag. Each scenario defines the configuration for a scenario
test execution.

You can provide scenarios in three ways:
- A single scenario as a <span style="color: #800080; text-decoration-color: #800080">json</span> object.
- Multiple scenarios by repeating the --scenarios flag.
- Multiple scenarios as a <span style="color: #800080; text-decoration-color: #800080">json</span> array in a single --scenarios flag.

Each scenario must have the following fields:
- <span style="color: #800080; text-decoration-color: #800080">instance_id</span>: ID of the instance to use for this scenario (required).
- <span style="color: #800080; text-decoration-color: #800080">scenario_input</span>: Object containing the scenario input (required), with:
    - <span style="color: #800080; text-decoration-color: #800080">scenario_input_type</span>: Type of the scenario input (required).
    - <span style="color: #800080; text-decoration-color: #800080">scenario_input_data</span>: Data for the scenario input (required).
- <span style="color: #800080; text-decoration-color: #800080">scenario_id</span>: ID of the scenario (optional). The
  default value will be set as <span style="color: #800080; text-decoration-color: #800080">scenario-&lt;index&gt;</span> if not set.
- <span style="color: #800080; text-decoration-color: #800080">configuration</span>: An array of configuration objects
  (optional). Use this attribute to configure variation of options for the scenario. Each scenario
  configuration object requires:
    - <span style="color: #800080; text-decoration-color: #800080">name</span>: Name of the configuration option.
    - <span style="color: #800080; text-decoration-color: #800080">values</span>: List of values for the configuration option.

Example object format:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;instance_id&quot;: &quot;bunny-hopper-v2&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;input_id&quot;: &quot;meadow-input-a1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;input_set_id&quot;: &quot;spring-gardens&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;configuration&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;name&quot;: &quot;speed&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;values&quot;: [&quot;optimized&quot;, &quot;balanced&quot;, &quot;safe&quot;]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    ]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a scenario test with a single scenario.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">SCENARIO=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;warren-planner-v1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_id&quot;: &quot;carrot-patch-a&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_set_id&quot;: &quot;spring-gardens&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud scenario create --app-id hare-app --scenarios &quot;$SCENARIO&quot;</span>

- Create with multiple scenarios by repeating the flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">SCENARIO1=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_id&quot;: &quot;lettuce-field-1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_set_id&quot;: &quot;veggie-gardens&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    SCENARIO2=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_id&quot;: &quot;lettuce-field-2&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_set_id&quot;: &quot;veggie-gardens&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud scenario create --app-id hare-app --scenarios &quot;$SCENARIO1&quot; --scenarios &quot;$SCENARIO2&quot;</span>

- Create with multiple scenarios in a single <span style="color: #800080; text-decoration-color: #800080">json</span> array.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">SCENARIOS=&#x27;[</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;instance_id&quot;: &quot;burrow-builder&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                    &quot;input_id&quot;: &quot;warren-zone-a&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                    &quot;input_set_id&quot;: &quot;burrow-sites&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;instance_id&quot;: &quot;tunnel-planner-v3&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                    &quot;input_id&quot;: &quot;warren-zone-b&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                    &quot;input_set_id&quot;: &quot;burrow-sites&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    ]&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud scenario create --app-id hare-app --scenarios &quot;$SCENARIOS&quot;</span>

- Create a scenario test and wait for it to complete.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">SCENARIO=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;foraging-route&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_id&quot;: &quot;carrot-harvest&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_set_id&quot;: &quot;harvest-season&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud scenario create --app-id hare-app --scenarios &quot;$SCENARIO&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --wait</span>

- Create a scenario test and save the results to a file, waiting for completion.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">SCENARIO=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;safe-hopper&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_id&quot;: &quot;predator-zones&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_set_id&quot;: &quot;danger-zones&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud scenario create --app-id hare-app --scenarios &quot;$SCENARIO&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output bunny-safety-results.json</span>

- Create a scenario test with configuration options.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">SCENARIO=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;instance_id&quot;: &quot;hop-optimizer&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;scenario_input&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_type&quot;: &quot;input_set&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;scenario_input_data&quot;: {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_id&quot;: &quot;garden-route-1&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;input_set_id&quot;: &quot;garden-paths&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        },</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;configuration&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            {</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;name&quot;: &quot;speed&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">                &quot;values&quot;: [&quot;fast&quot;, &quot;careful&quot;]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            }</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        ]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud scenario create --app-id hare-app --scenarios &quot;$SCENARIO&quot;</span>

**Usage**:

```console
$ cloud scenario create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --scenarios SCENARIOS`: Scenarios to use for the test. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple scenarios by repeating the flag, or providing a list of objects. See command help for details on scenario formatting.  [required]
* `-d, --description DESCRIPTION`: Description of the scenario test.
* `-n, --name NAME`: Optional name of the scenario test. If not provided, the ID will be used as the name.
* `-r, --repetitions REPETITIONS`: Number of times the scenario test is <span style="font-style: italic">repeated</span>. 0 repetitions = 1 execution, 1 repetition = 2 executions, etc.  [default: 0]
* `-i, --scenario-test-id SCENARIO_TEST_ID`: ID for the scenario test. Will be generated if not provided.  [env var: NEXTMV_SCENARIO_TEST_ID]
* `-o, --output OUTPUT_PATH`: Waits for the test to complete and saves the results to this location.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the scenario test to complete. Results are printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud scenario delete`

Deletes a Nextmv Cloud scenario test.

This action is permanent and cannot be undone. The scenario test and all
associated data will be deleted. Use the --yes flag to skip
the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the scenario test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario delete --app-id hare-app --scenario-test-id hop-analysis</span>

- Delete the scenario test without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario delete --app-id hare-app --scenario-test-id carrot-routes --yes</span>

**Usage**:

```console
$ cloud scenario delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --scenario-test-id SCENARIO_TEST_ID`: The Nextmv Cloud scenario test ID to use for this action.  [env var: NEXTMV_SCENARIO_TEST_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud scenario get`

Get a Nextmv Cloud scenario test, including its runs.

Use the --wait flag to wait for the scenario test to
complete, polling for results. Using the --output flag will
also activate waiting, and allows you to specify a destination file for the
results.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the scenario test with ID <span style="color: #800080; text-decoration-color: #800080">carrot-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario get --app-id hare-app --scenario-test-id carrot-optimization</span>

- Get the scenario test and wait for it to complete if necessary.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario get --app-id hare-app --scenario-test-id bunny-hop-test --wait</span>

- Get the scenario test and save the results to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario get --app-id hare-app --scenario-test-id warren-planning \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output results.json</span>

- Get the scenario test using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario get --app-id hare-app --scenario-test-id lettuce-routes --profile prod</span>

**Usage**:

```console
$ cloud scenario get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --scenario-test-id SCENARIO_TEST_ID`: The Nextmv Cloud scenario test ID to use for this action.  [env var: NEXTMV_SCENARIO_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Waits for the scenario test to complete and saves the results to this location.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the scenario test to complete. Results are printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud scenario list`

List all Nextmv Cloud scenario tests for an application.

This command retrieves all scenario tests associated with the specified
application. By default this command paginates the list of tests, which
means multiple API calls may be made to retrieve all tests. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all scenario tests for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario list --app-id hare-app</span>

- List all scenario tests and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario list --app-id hare-app --output scenario_tests.json</span>

- List all scenario tests using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario list --app-id hare-app --profile</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    prod</span>

- List all scenario tests without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud scenario list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of scenario tests to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud scenario metadata`

Get metadata for a Nextmv Cloud scenario test.

This command retrieves metadata for a specific scenario test, including
status, creation date, and other high-level information without the full
run details.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get metadata for scenario test <span style="color: #800080; text-decoration-color: #800080">bunny-warren-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario metadata --app-id hare-app --scenario-test-id bunny-warren-optimization</span>

- Get metadata and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario metadata --app-id hare-app --scenario-test-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output metadata.json</span>

- Get metadata using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario metadata --app-id hare-app --scenario-test-id hop-schedule --profile prod</span>

**Usage**:

```console
$ cloud scenario metadata [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --scenario-test-id SCENARIO_TEST_ID`: The Nextmv Cloud scenario test ID to use for this action.  [env var: NEXTMV_SCENARIO_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the scenario test metadata to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud scenario update`

Update a Nextmv Cloud scenario test.

Update the name and/or description of a scenario test. Any fields not
specified will remain unchanged.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of a scenario test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario update --app-id hare-app --scenario-test-id carrot-feast \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Spring Carrot Harvest&quot;</span>

- Update the description of a scenario test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario update --app-id hare-app --scenario-test-id bunny-hop-routes \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Optimizing hop paths through the meadow&quot;</span>

- Update both name and description and save the result.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud scenario update --app-id hare-app --scenario-test-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Warren Lettuce Express&quot; --description &quot;Fast lettuce delivery to all burrows&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output updated-scenario.json</span>

**Usage**:

```console
$ cloud scenario update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --scenario-test-id SCENARIO_TEST_ID`: The Nextmv Cloud scenario test ID to use for this action.  [env var: NEXTMV_SCENARIO_TEST_ID; required]
* `-d, --description DESCRIPTION`: Updated description of the scenario test.
* `-n, --name NAME`: Updated name of the scenario test.
* `-o, --output OUTPUT_PATH`: Saves the updated scenario test information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud secrets`

Create and manage Nextmv Cloud secrets collections.

A secret collection defines one or more secrets used by your optimization
model during execution. You can reference a secret collection either in an
application instance configuration, or directly when starting a run. The
platform then injects the secrets into the container during the
optimization run as environment variables and files.

**Usage**:

```console
$ cloud secrets [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud secrets collection.
* `delete`: Deletes a Nextmv Cloud secrets collection.
* `get`: Get a Nextmv Cloud secrets collection.
* `list`: List all secrets collections of a Nextmv...
* `update`: Update a Nextmv Cloud secrets collection.

#### `cloud secrets create`

Create a new Nextmv Cloud secrets collection.

A secrets collection is a group of key-value pairs that can be used by
your application instances during execution. Each collection can contain
up to 20 secrets. Secrets are provided as JSON objects using the
--secrets flag.

Each secret must include three fields:
- <span style="color: #800080; text-decoration-color: #800080">type</span>: Either <span style="color: #800080; text-decoration-color: #800080">env</span> or <span style="color: #800080; text-decoration-color: #800080">file</span>,
  which determines how the secret is injected into the runtime.
- <span style="color: #800080; text-decoration-color: #800080">location</span>: Where to place the secret.
  - <span style="color: #800080; text-decoration-color: #800080">env</span>: the environment variable name. E.g.: <span style="color: #800080; text-decoration-color: #800080">BURROW_ENTRANCE</span>.
  - <span style="color: #800080; text-decoration-color: #800080">file</span>: the relative path from the execution
    directory. E.g.: <span style="color: #800080; text-decoration-color: #800080">licenses/burrow.entr</span>.
- <span style="color: #800080; text-decoration-color: #800080">value</span>: The secret value as text (limited to 1 KB).

You can provide secrets in three ways:
- A single secret as a <span style="color: #800080; text-decoration-color: #800080">json</span> object.
- Multiple secrets by repeating the --secrets flag.
- Multiple secrets as a <span style="color: #800080; text-decoration-color: #800080">json</span> array in a single --secrets flag.

The --secrets-collection-id and --name are optional.
If not provided, they will be automatically generated.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a secrets collection with a single environment variable secret.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;API_KEY&quot;, &quot;value&quot;: &quot;secret-value&quot;}&#x27;</span>

- Create a secrets collection with multiple secrets by repeating the flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;API_KEY&quot;, &quot;value&quot;: &quot;secret-value&quot;}&#x27; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;DATABASE_URL&quot;, &quot;value&quot;: &quot;postgres://localhost&quot;}&#x27;</span>

- Create a secrets collection with multiple secrets in a single JSON array.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;[{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;DB_USER&quot;, &quot;value&quot;: &quot;admin&quot;}, {...}]&#x27;</span>

- Create a secrets collection with custom ID, name, and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id db-creds --name &quot;Database Credentials&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Production database credentials&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;DB_USER&quot;, &quot;value&quot;: &quot;admin&quot;}&#x27; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;DB_PASS&quot;, &quot;value&quot;: &quot;secure123&quot;}&#x27;</span>

- Create a secrets collection with file-based secrets.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id certs --name &quot;Certificates&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;file&quot;, &quot;location&quot;: &quot;licenses/acme.lic&quot;, &quot;value&quot;: &quot;LICENSE_CONTENT_HERE&quot;}&#x27;</span>

- Mix environment and file-based secrets.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets create --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;ACME_LICENSE_KEY&quot;, &quot;value&quot;: &quot;abc123&quot;}&#x27; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;file&quot;, &quot;location&quot;: &quot;config/app.conf&quot;, &quot;value&quot;: &quot;server=prod\nport=8080&quot;}&#x27;</span>

**Usage**:

```console
$ cloud secrets create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-e, --secrets SECRETS`: Secrets to configure in the app. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple secrets by repeating the flag, or providing a list of objects. Allowed values for <span style="color: #800080; text-decoration-color: #800080">type</span> are: <span style="color: #800080; text-decoration-color: #800080">env</span> and <span style="color: #800080; text-decoration-color: #800080">file</span>. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{&#x27;type&#x27;: type, &#x27;location&#x27;: location, &#x27;value&#x27;: value}</span>.  [required]
* `-d, --description DESCRIPTION`: An optional description for the secrets collection.
* `-n, --name NAME`: An optional name for the secrets collection. If not provided, the ID will be used as the name.
* `-s, --secrets-collection-id SECRETS_COLLECTION_ID`: The ID to assign to the new secrets collection. If not provided, a random ID will be generated.  [env var: NEXTMV_SECRETS_COLLECTION_ID]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud secrets delete`

Deletes a Nextmv Cloud secrets collection.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the secrets collection with the ID <span style="color: #800080; text-decoration-color: #800080">api-keys</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets delete --app-id hare-app --secrets-collection-id api-keys</span>

- Delete the secrets collection without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets delete --app-id hare-app --secrets-collection-id api-keys --yes</span>

**Usage**:

```console
$ cloud secrets delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --secrets-collection-id SECRETS_COLLECTION_ID`: The Nextmv Cloud secrets collection ID to use for this action.  [env var: NEXTMV_SECRETS_COLLECTION_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud secrets get`

Get a Nextmv Cloud secrets collection.

This command is useful to get the attributes of an existing Nextmv Cloud
secrets collection by its ID. 🚧 <span style="color: #808000; text-decoration-color: #808000; font-weight: bold">Warning:</span>
<span style="color: #808000; text-decoration-color: #808000; font-weight: bold">secret values will be included in the output.</span>

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the secrets collection with the ID <span style="color: #800080; text-decoration-color: #800080">api-keys</span> from
  application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets get --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    --secrets-collection-id api-keys</span>

- Get the secrets collection with the ID <span style="color: #800080; text-decoration-color: #800080">api-keys</span> and
  save the information to a <span style="color: #800080; text-decoration-color: #800080">secrets.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets get --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys --output secrets.json</span>

**Usage**:

```console
$ cloud secrets get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --secrets-collection-id SECRETS_COLLECTION_ID`: The Nextmv Cloud secrets collection ID to use for this action.  [env var: NEXTMV_SECRETS_COLLECTION_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the secrets collection information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud secrets list`

List all secrets collections of a Nextmv Cloud application.

By default this command paginates the list of secrets, which means multiple
API calls may be made to retrieve all secrets. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all secrets collections of application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets list --app-id hare-app</span>

- List all secrets collections using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets list --app-id hare-app --profile hare</span>

- List all secrets collections and save the information to a <span style="color: #800080; text-decoration-color: #800080">secrets.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets list --app-id hare-app --output secrets.json</span>

- List all secrets collections without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud secrets list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the secrets collections list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud secrets update`

Update a Nextmv Cloud secrets collection.

You can update the name, description, and/or secrets of an existing
secrets collection. When updating secrets, all existing secrets will be
replaced with the new ones provided.

Secrets are provided as JSON objects using the --secrets flag,
following the same format as the create command. You can provide secrets as:
- A single secret as a JSON object
- Multiple secrets by repeating the --secrets flag
- Multiple secrets as a JSON array in a single --secrets flag

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of a secrets collection.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys --name &quot;Updated API Keys&quot;</span>

- Update the description of a secrets collection.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Updated collection of API keys&quot;</span>

- Update both name and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys --name &quot;Production API Keys&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;API keys for production environment&quot;</span>

- Replace all secrets in a collection with new secrets.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;API_KEY&quot;, &quot;value&quot;: &quot;new-value&quot;}&#x27; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;DATABASE_URL&quot;, &quot;value&quot;: &quot;postgres://newhost&quot;}&#x27;</span>

- Replace all secrets with a JSON array.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;[{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;API_KEY&quot;, &quot;value&quot;: &quot;new-value&quot;}, {...}]&#x27;</span>

- Update multiple attributes at once and save the result.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud secrets update --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets-collection-id api-keys --name &quot;New Name&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;New Description&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --secrets &#x27;{&quot;type&quot;: &quot;env&quot;, &quot;location&quot;: &quot;NEW_KEY&quot;, &quot;value&quot;: &quot;new-value&quot;}&#x27; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output updated.json</span>

**Usage**:

```console
$ cloud secrets update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --secrets-collection-id SECRETS_COLLECTION_ID`: The Nextmv Cloud secrets collection ID to use for this action.  [env var: NEXTMV_SECRETS_COLLECTION_ID; required]
* `-d, --description DESCRIPTION`: A new description for the secrets collection.
* `-n, --name NAME`: A new name for the secrets collection.
* `-u, --output OUTPUT_PATH`: Saves the updated secrets collection information to this location.
* `-e, --secrets SECRETS`: Secrets to configure in the app. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Pass multiple secrets by repeating the flag, or providing a list of objects. Allowed values for <span style="color: #800080; text-decoration-color: #800080">type</span> are: <span style="color: #800080; text-decoration-color: #800080">env</span> and <span style="color: #800080; text-decoration-color: #800080">file</span>. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{&#x27;type&#x27;: type, &#x27;location&#x27;: location, &#x27;value&#x27;: value}</span>. This will replace all existing secrets in the collection.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud shadow`

Create and manage Nextmv Cloud shadow tests.

**Usage**:

```console
$ cloud shadow [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud shadow test in...
* `delete`: Deletes a Nextmv Cloud shadow test.
* `get`: Get a Nextmv Cloud shadow test, including...
* `list`: List all Nextmv Cloud shadow tests for an...
* `metadata`: Get metadata for a Nextmv Cloud shadow test.
* `start`: Starts a Nextmv Cloud shadow test.
* `stop`: Stops a Nextmv Cloud shadow test.
* `update`: Update a Nextmv Cloud shadow test.

#### `cloud shadow create`

Create a new Nextmv Cloud shadow test in draft mode.

Use the --comparisons option to define how to set up instance comparisons.
The value should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. The keys of the
comparisons object are the baseline instance IDs, and the values are the
candidate lists of instance IDs to compare against the respective baseline.

Here is an example comparisons object:
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;baseline-instance-1&quot;: [&quot;candidate-instance-1&quot;, &quot;candidate-instance-2&quot;],</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    &quot;baseline-instance-2&quot;: [&quot;candidate-instance-3&quot;]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">}</span>

You may specify the --start-time option to make the shadow test start at a
specific time. Alternatively, you may use the <span style="font-weight: bold">nextmv cloud shadow</span>
<span style="font-weight: bold">start</span> command to start the test.

The --termination-maximum-runs option is required and provides control over
when the shadow test should terminate, after said number of runs.
Alternatively, you may specify the --termination-time option or use the
<span style="font-weight: bold">nextmv cloud shadow stop</span> command to stop the test.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a shadow test with a baseline and two candidate instances.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">COMPARISONS=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;fluffy-bunny-baseline&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;hopping-candidate-ears&quot;,</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;speedy-cottontail&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        ]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud shadow create --app-id hare-app --shadow-test-id bunny-hop-shadow --name &quot;Bunny Hop Showdown&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --comparisons &quot;$COMPARISONS&quot; --termination-maximum-runs 100</span>

- Create a shadow test with multiple baselines and candidates.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">COMPARISONS=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;fluffy-bunny-baseline&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;hopping-candidate-ears&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        ],</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;wise-old-rabbit&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;burrow-master&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        ]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud shadow create --app-id hare-app --shadow-test-id warren-race --name &quot;Warren Race Test&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --comparisons &quot;$COMPARISONS&quot; --termination-maximum-runs 50</span>

- Create a shadow test with a scheduled start and termination time.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">COMPARISONS=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;fluffy-bunny-baseline&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;hopping-candidate-ears&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        ]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud shadow create --app-id hare-app --shadow-test-id sunrise-hop --name &quot;Sunrise Hop Test&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --comparisons &quot;$COMPARISONS&quot; --start-time &#x27;2026-01-23T10:00:00Z&#x27; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --termination-time &#x27;2026-01-23T18:00:00Z&#x27; --termination-maximum-runs 20</span>

- Create a shadow test with a description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">COMPARISONS=&#x27;{</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        &quot;fluffy-bunny-baseline&quot;: [</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">            &quot;hopping-candidate-ears&quot;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        ]</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    }&#x27;</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">    nextmv cloud shadow create --app-id hare-app --shadow-test-id carrot-compare --name &quot;Carrot Comparison&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Testing cool bunnies&quot; --comparisons &quot;$COMPARISONS&quot; --termination-maximum-runs 10</span>

**Usage**:

```console
$ cloud shadow create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-c, --comparisons COMPARISONS`: Object mapping baseline instance IDs to a list of comparison instance IDs. Data should be valid <span style="color: #800080; text-decoration-color: #800080">json</span>. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">{&#x27;baseline_id1&#x27;: [&#x27;comparison_id1&#x27;, &#x27;comparison_id2&#x27;], &#x27;baseline_id2&#x27;: ...}</span>  [required]
* `-m, --termination-maximum-runs TERMINATION_MAXIMUM_RUNS`: Maximum number of runs for the shadow test termination condition.  [1&lt;=x&lt;=300; required]
* `-d, --description DESCRIPTION`: Description of the shadow test.
* `-n, --name NAME`: Optional name of the shadow test. If not provided, the ID will be used as the name.
* `-s, --shadow-test-id SHADOW_TEST_ID`: Optional ID for the shadow test. Will be generated if not provided.  [env var: NEXTMV_SHADOW_TEST_ID]
* `-r, --start-time START_TIME`: Scheduled time for shadow test start in <span style="color: #800080; text-decoration-color: #800080">RFC 3339</span> format. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&#x27;2024-01-01T00:00:00Z&#x27;</span>
* `-t, --termination-time TERMINATION_TIME`: Scheduled time for shadow test end in <span style="color: #800080; text-decoration-color: #800080">RFC 3339</span> format. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&#x27;2024-01-01T00:00:00Z&#x27;</span>
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow delete`

Deletes a Nextmv Cloud shadow test.

This action is permanent and cannot be undone. The shadow test and all
associated data, including runs, will be deleted. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the shadow test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow delete --app-id hare-app --shadow-test-id hop-analysis</span>

- Delete the shadow test without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow delete --app-id hare-app --shadow-test-id carrot-routes --yes</span>

**Usage**:

```console
$ cloud shadow delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --shadow-test-id SHADOW_TEST_ID`: The Nextmv Cloud shadow test ID to use for this action.  [env var: NEXTMV_SHADOW_TEST_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow get`

Get a Nextmv Cloud shadow test, including its runs.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the shadow test with ID <span style="color: #800080; text-decoration-color: #800080">carrot-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow get --app-id hare-app --shadow-test-id carrot-optimization</span>

- Get the shadow test using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow get --app-id hare-app --shadow-test-id lettuce-routes --profile prod</span>

**Usage**:

```console
$ cloud shadow get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --shadow-test-id SHADOW_TEST_ID`: The Nextmv Cloud shadow test ID to use for this action.  [env var: NEXTMV_SHADOW_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the results to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow list`

List all Nextmv Cloud shadow tests for an application.

This command retrieves all shadow tests associated with the specified
application. By default this command paginates the list of tests, which
means multiple API calls may be made to retrieve all tests. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all shadow tests for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow list --app-id hare-app</span>

- List all shadow tests and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow list --app-id hare-app --output tests.json</span>

- List all shadow tests using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow list --app-id hare-app --profile prod</span>

- List all shadow tests without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud shadow list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of shadow tests to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow metadata`

Get metadata for a Nextmv Cloud shadow test.

This command retrieves metadata for a specific shadow test, including
status, creation date, and other high-level information without the full
run details.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get metadata for shadow test <span style="color: #800080; text-decoration-color: #800080">bunny-warren-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow metadata --app-id hare-app --shadow-test-id bunny-warren-optimization</span>

- Get metadata and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow metadata --app-id hare-app --shadow-test-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output metadata.json</span>

- Get metadata using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow metadata --app-id hare-app --shadow-test-id hop-schedule --profile prod</span>

**Usage**:

```console
$ cloud shadow metadata [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --shadow-test-id SHADOW_TEST_ID`: The Nextmv Cloud shadow test ID to use for this action.  [env var: NEXTMV_SHADOW_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the shadow test metadata to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow start`

Starts a Nextmv Cloud shadow test.

Before starting a shadow test, it must be created in draft state. You may
use the <span style="font-weight: bold">nextmv cloud shadow create</span> command to create a new
shadow test. Alternatively, define a --start-time when using the
<span style="font-weight: bold">nextmv cloud shadow create</span> command to have the shadow test
start automatically at a specific time.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Start the shadow test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow start --app-id hare-app --shadow-test-id hop-analysis</span>

**Usage**:

```console
$ cloud shadow start [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --shadow-test-id SHADOW_TEST_ID`: The Nextmv Cloud shadow test ID to use for this action.  [env var: NEXTMV_SHADOW_TEST_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow stop`

Stops a Nextmv Cloud shadow test.

Before stopping a shadow test, it must be in a started state. Experiments
in a <span style="color: #800080; text-decoration-color: #800080">draft</span> state, that haven&#x27;t started, can be deleted
with the <span style="font-weight: bold">nextmv cloud shadow delete</span> command.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Stop the shadow test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow stop --app-id hare-app --shadow-test-id hop-analysis</span>

**Usage**:

```console
$ cloud shadow stop [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --intent INTENT`: Intent for stopping the shadow test. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">complete</span> and <span style="color: #800080; text-decoration-color: #800080">cancel</span>.  [required]
* `-s, --shadow-test-id SHADOW_TEST_ID`: The Nextmv Cloud shadow test ID to use for this action.  [env var: NEXTMV_SHADOW_TEST_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud shadow update`

Update a Nextmv Cloud shadow test.

Update the name and/or description of a shadow test. Any fields not
specified will remain unchanged.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of a shadow test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow update --app-id hare-app --shadow-test-id carrot-feast \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Spring Carrot Harvest&quot;</span>

- Update the description of a shadow test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow update --app-id hare-app --shadow-test-id bunny-hop-routes \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Optimizing hop paths through the meadow&quot;</span>

- Update both name and description and save the result.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud shadow update --app-id hare-app --shadow-test-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Warren Lettuce Express&quot; --description &quot;Fast lettuce delivery to all burrows&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output updated-shadow-test.json</span>

**Usage**:

```console
$ cloud shadow update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --shadow-test-id SHADOW_TEST_ID`: The Nextmv Cloud shadow test ID to use for this action.  [env var: NEXTMV_SHADOW_TEST_ID; required]
* `-d, --description DESCRIPTION`: Updated description of the shadow test.
* `-n, --name NAME`: Updated name of the shadow test.
* `-o, --output OUTPUT_PATH`: Saves the updated shadow test information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud sso`

Manage SSO for your Nextmv Cloud organization (account).

Please contact <span style="font-weight: bold"><a href="https://www.nextmv.io/contact">Nextmv support</a></span>
for assistance configuring SSO for your organization.

**Usage**:

```console
$ cloud sso [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new SSO configuration for your...
* `delete`: Deletes the SSO configuration.
* `disable`: Disables the SSO configuration.
* `enable`: Enables the SSO configuration.
* `get`: Get the information of a Nextmv Cloud SSO...
* `update`: Updates information of a Nextmv Cloud SSO...
* `domain`: Manage SSO mapped domains for your Nextmv...

#### `cloud sso create`

Create a new SSO configuration for your Nextmv Cloud organization.

SSO must be configured to enable managed accounts in your organization.
Please contact <span style="font-weight: bold"><a href="https://www.nextmv.io/contact">Nextmv support</a></span> for assistance.

You must use either the --metadata-url or --metadata-document option. When
working with the metadata document, you have three options:

- Pipe the document into the command via <span style="color: #800080; text-decoration-color: #800080">stdin</span>.
- Provide the document as a string with --metadata-document.
- Provide a path to a file containing the document with --metadata-document.

You can use the <span style="font-weight: bold">nextmv cloud sso get</span> to get the newly-created
configuration after running this command.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an SSO configuration using a metadata URL.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso create --metadata-url &quot;https://sso.carrotexpress.com/saml/metadata&quot;</span>

- Create and enable SSO configuration immediately.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso create --metadata-url &quot;https://sso.bunnylogistics.io/metadata&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --enabled</span>

- Create SSO configuration allowing non-domain users.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso create --metadata-url &quot;https://idp.hopmail.com/saml/metadata&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --allow-non-domain-users</span>

- Create SSO configuration using a metadata document string.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso create --metadata-document &quot;&lt;EntityDescriptor ...&lt;/EntityDescriptor&gt;&quot;</span>

- Create SSO configuration using a metadata document file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso create --metadata-document &quot;/path/to/metadata_document.xml&quot;</span>

- Create SSO configuration using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso create --metadata-url &quot;https://sso.cottontailcouriers.net/metadata&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --profile hare</span>

**Usage**:

```console
$ cloud sso create [OPTIONS]
```

**Options**:

* `-a, --allow-non-domain-users`: Allow users who are not part of the SSO domain to access the Nextmv Cloud organization (account).
* `-e, --enabled`: Enable SSO for the Nextmv Cloud organization (account) at the time of creation. Run <span style="font-weight: bold">nextmv cloud sso enable</span> to enable SSO after creation.
* `-u, --metadata-url METADATA_URL`: The URL to the SSO metadata document.
* `-d, --metadata-document METADATA_DOCUMENT`: The SSO metadata document as a string or a path to a file containing the document.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud sso delete`

Deletes the SSO configuration.

You must have the <span style="color: #800080; text-decoration-color: #800080">administrator</span> role on the organization
in order to delete it. Use the --yes flag to skip the confirmation prompt.
You can create a new SSO configuration again with <span style="font-weight: bold">nextmv cloud sso create</span>.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the SSO configuration.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso delete</span>

- Delete the SSO configuration without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso delete --yes</span>

**Usage**:

```console
$ cloud sso delete [OPTIONS]
```

**Options**:

* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud sso disable`

Disables the SSO configuration.

Use the --yes flag to skip the confirmation prompt. Use the <span style="font-weight: bold">nextmv</span>
<span style="font-weight: bold">cloud sso enable</span> command to re-enable SSO.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Disable the SSO configuration.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso disable</span>

- Disable the SSO configuration without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso disable --yes</span>

**Usage**:

```console
$ cloud sso disable [OPTIONS]
```

**Options**:

* `-y, --yes`: Agree to disable confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud sso enable`

Enables the SSO configuration.

Use the --yes flag to skip the confirmation prompt. Use the <span style="font-weight: bold">nextmv</span>
<span style="font-weight: bold">cloud sso disable</span> command to disable SSO.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Enable the SSO configuration.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso enable</span>

- Enable the SSO configuration without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso enable --yes</span>

**Usage**:

```console
$ cloud sso enable [OPTIONS]
```

**Options**:

* `-y, --yes`: Agree to enable confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud sso get`

Get the information of a Nextmv Cloud SSO configuration.

This command is useful to get the attributes of an existing Nextmv Cloud
SSO configuration.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the SSO configuration.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso get</span>

- Get the SSO configuration and save the information to an <span style="color: #800080; text-decoration-color: #800080">sso_config.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso get --output sso_config.json</span>

**Usage**:

```console
$ cloud sso get [OPTIONS]
```

**Options**:

* `-o, --output OUTPUT_PATH`: Saves the SSO configuration information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud sso update`

Updates information of a Nextmv Cloud SSO configuration.

This command allows you to update the metadata URL or metadata document of
an existing SSO configuration. You can use the <span style="font-weight: bold">nextmv cloud sso</span>
<span style="font-weight: bold">get</span> to get the updated configuration after running this command.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the SSO configuration with a new metadata URL.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso update --metadata-url &quot;https://example.com/metadata.xml&quot;</span>

- Update the SSO configuration with a new metadata document.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso update --metadata-document &quot;&lt;xml&gt;...&lt;/xml&gt;&quot;</span>

**Usage**:

```console
$ cloud sso update [OPTIONS]
```

**Options**:

* `-u, --metadata-url METADATA_URL`: The URL to the SSO metadata document to update.
* `-d, --metadata-document METADATA_DOCUMENT`: The SSO metadata document as a string to update.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud sso domain`

Manage SSO mapped domains for your Nextmv Cloud organization (account).

Mapped domains redirect additional domains to your IDP for federated authentication.

Please contact <span style="font-weight: bold"><a href="https://www.nextmv.io/contact">Nextmv support</a></span>
for assistance configuring SSO for your organization.

**Usage**:

```console
$ cloud sso domain [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Delete a mapped domain from a Nextmv Cloud...

##### `cloud sso domain delete`

Delete a mapped domain from a Nextmv Cloud SSO configuration.


This action will prevent users from the deleted domain from accessing your
account using SSO. Use the --yes flag to skip the confirmation prompt.

You can use the <span style="font-weight: bold">nextmv cloud sso get</span> command to view all
mapped domains in your SSO configuration.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete a mapped domain from the SSO configuration.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud sso domain delete --domain &quot;example.com&quot;</span>

**Usage**:

```console
$ cloud sso domain delete [OPTIONS]
```

**Options**:

* `-d, --domain DOMAIN`: The domain to delete from the SSO configuration.  [required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud switchback`

Create and manage Nextmv Cloud switchback tests.

**Usage**:

```console
$ cloud switchback [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud switchback test...
* `delete`: Deletes a Nextmv Cloud switchback test.
* `get`: Get a Nextmv Cloud switchback test,...
* `list`: List all Nextmv Cloud switchback tests for...
* `metadata`: Get metadata for a Nextmv Cloud switchback...
* `start`: Starts a Nextmv Cloud switchback test.
* `stop`: Stops a Nextmv Cloud switchback test.
* `update`: Update a Nextmv Cloud switchback test.

#### `cloud switchback create`

Create a new Nextmv Cloud switchback test in draft mode.

The test will alternate between the --baseline-instance-id and
--candidate-instance-id over specified time intervals.

You may specify the --start option to make the switchback test start at a
specific time. Alternatively, you may use the <span style="font-weight: bold">nextmv cloud switchback</span>
<span style="font-weight: bold">start</span> command to start the test.

Use the <span style="font-weight: bold">nextmv cloud switchback stop</span> command to stop the test.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a switchback test alternating between two bunny instances.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback create --app-id hare-app --baseline-instance-id fluffy-bunny-baseline \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id speedy-cottontail --unit-duration-minutes 15 --units 10</span>

- Create a switchback test with a scheduled start time.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback create --app-id hare-app --baseline-instance-id wise-old-rabbit \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id burrow-master --unit-duration-minutes 30 --units 8 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --start &#x27;2026-01-23T10:00:00Z&#x27;</span>

- Create a switchback test with a description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback create --app-id hare-app --baseline-instance-id fluffy-bunny-baseline \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --candidate-instance-id hopping-candidate-ears --unit-duration-minutes 20 --units 12 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Which bunny hops best for carrots?&quot;</span>

**Usage**:

```console
$ cloud switchback create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-b, --baseline-instance-id BASELINE_INSTANCE_ID`: ID of the baseline instance for the switchback test.  [required]
* `-c, --candidate-instance-id CANDIDATE_INSTANCE_ID`: ID of the candidate instance for the switchback test.  [required]
* `-u, --unit-duration-minutes UNIT_DURATION_MINUTES`: Duration of each interval in minutes.  [1&lt;=x&lt;=10080; required]
* `-t, --units UNITS`: Total number of intervals in the switchback test.  [1&lt;=x&lt;=1000; required]
* `-d, --description DESCRIPTION`: Description of the switchback test.
* `-n, --name NAME`: Optional name of the switchback test. If not provided, the ID will be used as the name.
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: ID for the switchback test. Will be generated if not provided.  [env var: NEXTMV_SWITCHBACK_TEST_ID]
* `-r, --start START`: Scheduled time for switchback test start in <span style="color: #800080; text-decoration-color: #800080">RFC 3339</span> format. Object format: <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">&#x27;2024-01-01T00:00:00Z&#x27;</span>
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback delete`

Deletes a Nextmv Cloud switchback test.

This action is permanent and cannot be undone. The switchback test and all
associated data, including runs, will be deleted. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the switchback test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback delete --app-id hare-app --switchback-test-id hop-analysis</span>

- Delete the switchback test without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback delete --app-id hare-app --switchback-test-id carrot-routes --yes</span>

**Usage**:

```console
$ cloud switchback delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: The Nextmv Cloud switchback test ID to use for this action.  [env var: NEXTMV_SWITCHBACK_TEST_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback get`

Get a Nextmv Cloud switchback test, including its runs.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the switchback test with ID <span style="color: #800080; text-decoration-color: #800080">carrot-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback get --app-id hare-app --switchback-test-id carrot-optimization</span>

- Get the switchback test using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback get --app-id hare-app --switchback-test-id lettuce-routes \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --profile prod</span>

**Usage**:

```console
$ cloud switchback get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: The Nextmv Cloud switchback test ID to use for this action.  [env var: NEXTMV_SWITCHBACK_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the results to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback list`

List all Nextmv Cloud switchback tests for an application.

This command retrieves all switchback tests associated with the specified
application. By default this command paginates the list of tests, which
means multiple API calls may be made to retrieve all tests. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all switchback tests for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback list --app-id hare-app</span>

- List all switchback tests and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback list --app-id hare-app --output tests.json</span>

- List all switchback tests using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback list --app-id hare-app --profile prod</span>

- List all switchback tests without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud switchback list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the list of switchback tests to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback metadata`

Get metadata for a Nextmv Cloud switchback test.

This command retrieves metadata for a specific switchback test, including
status, creation date, and other high-level information without the full
run details.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get metadata for switchback test <span style="color: #800080; text-decoration-color: #800080">bunny-warren-optimization</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback metadata --app-id hare-app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --switchback-test-id bunny-warren-optimization</span>

- Get metadata and save to a file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback metadata --app-id hare-app --switchback-test-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output metadata.json</span>

- Get metadata using a specific profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback metadata --app-id hare-app --switchback-test-id hop-schedule \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --profile prod</span>

**Usage**:

```console
$ cloud switchback metadata [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: The Nextmv Cloud switchback test ID to use for this action.  [env var: NEXTMV_SWITCHBACK_TEST_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the switchback test metadata to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback start`

Starts a Nextmv Cloud switchback test.

Before starting a switchback test, it must be created in draft state. You
may use the <span style="font-weight: bold">nextmv cloud switchback create</span> command to create a
new switchback test. Alternatively, define a --start when using the
<span style="font-weight: bold">nextmv cloud switchback create</span> command to have the switchback
test start automatically at a specific time.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Start the switchback test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback start --app-id hare-app --switchback-test-id hop-analysis</span>

**Usage**:

```console
$ cloud switchback start [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: The Nextmv Cloud switchback test ID to use for this action.  [env var: NEXTMV_SWITCHBACK_TEST_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback stop`

Stops a Nextmv Cloud switchback test.

Before stopping a switchback test, it must be in a started state. Experiments
in a <span style="color: #800080; text-decoration-color: #800080">draft</span> state, that haven&#x27;t started, can be deleted
with the <span style="font-weight: bold">nextmv cloud switchback delete</span> command.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Stop the switchback test with the ID <span style="color: #800080; text-decoration-color: #800080">hop-analysis</span> from application
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback stop --app-id hare-app --switchback-test-id hop-analysis</span>

**Usage**:

```console
$ cloud switchback stop [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-i, --intent INTENT`: Intent for stopping the switchback test. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">complete</span> and <span style="color: #800080; text-decoration-color: #800080">cancel</span>.  [required]
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: The Nextmv Cloud switchback test ID to use for this action.  [env var: NEXTMV_SWITCHBACK_TEST_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud switchback update`

Update a Nextmv Cloud switchback test.

Update the name and/or description of a switchback test. Any fields not
specified will remain unchanged.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the name of a switchback test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback update --app-id hare-app --switchback-test-id carrot-feast \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Spring Carrot Harvest&quot;</span>

- Update the description of a switchback test.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback update --app-id hare-app --switchback-test-id bunny-hop-routes \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Optimizing hop paths through the meadow&quot;</span>

- Update both name and description and save the result.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud switchback update --app-id hare-app --switchback-test-id lettuce-delivery \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Warren Lettuce Express&quot; --description &quot;Fast lettuce delivery to all burrows&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output updated-switchback-test.json</span>

**Usage**:

```console
$ cloud switchback update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-s, --switchback-test-id SWITCHBACK_TEST_ID`: The Nextmv Cloud switchback test ID to use for this action.  [env var: NEXTMV_SWITCHBACK_TEST_ID; required]
* `-d, --description DESCRIPTION`: Updated description of the switchback test.
* `-n, --name NAME`: Updated name of the switchback test.
* `-o, --output OUTPUT_PATH`: Saves the updated switchback test information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud upload`

Create temporary upload URLs for Nextmv Cloud applications.

When data is too large, or you are working with multiple files, you can use
upload URLs to upload data directly to Nextmv Cloud storage.

**Usage**:

```console
$ cloud upload [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud application...

#### `cloud upload create`

Create a new Nextmv Cloud application upload URL.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create an upload URL for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud upload create --app-id hare-app</span>

- Create an upload URL for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span> using profile <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud upload create --app-id hare-app --profile hare</span>

**Usage**:

```console
$ cloud upload create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `cloud version`

Create and manage Nextmv Cloud application versions.

A version represents a snapshot of an application&#x27;s code at a specific
point in time. Versions are used to track changes to the decision model.
You can think of versions as Git tags for your Nextmv Cloud applications.

**Usage**:

```console
$ cloud version [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new Nextmv Cloud application...
* `delete`: Deletes a Nextmv Cloud application version.
* `exists`: Check if a Nextmv Cloud application...
* `get`: Get a Nextmv Cloud application version.
* `list`: List all versions of a Nextmv Cloud...
* `update`: Updates a Nextmv Cloud application version.

#### `cloud version create`

Create a new Nextmv Cloud application version.

Use the --exist-ok flag to avoid errors when creating a version with an ID
that already exists. This is useful for scripts that need to ensure a
version exists without worrying about whether it was created previously.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Create a version for application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. A random ID will be generated.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version create --app-id hare-app</span>

- Create a version with a specific name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version create --app-id hare-app --name &quot;v1.0.0&quot;</span>

- Create a version with a specific ID.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version create --app-id hare-app --version-id v1</span>

- Create a version with a name and description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version create --app-id hare-app --name &quot;v1.0.0&quot; \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Initial release with routing optimization&quot;</span>

- Create a version, or get it if it already exists.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version create --app-id hare-app --version-id v1 --exist-ok</span>

**Usage**:

```console
$ cloud version create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-d, --description DESCRIPTION`: An optional description for the version.
* `-e, --exist-ok`: If a version with the given ID already exists, do not raise an error, and simply return it.
* `-n, --name NAME`: Optional name for the version. If a name is not provided, the version ID will be used as the name.
* `-v, --version-id VERSION_ID`: The ID to assign to the new version. If not provided, a random ID will be generated.  [env var: NEXTMV_VERSION_ID]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud version delete`

Deletes a Nextmv Cloud application version.

This action is permanent and cannot be undone. Use the --yes
flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the version with the ID <span style="color: #800080; text-decoration-color: #800080">v1</span> from application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version delete --app-id hare-app --version-id v1</span>

- Delete the version without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version delete --app-id hare-app --version-id v1 --yes</span>

**Usage**:

```console
$ cloud version delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Cloud version ID to use for this action.  [env var: NEXTMV_VERSION_ID; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud version exists`

Check if a Nextmv Cloud application version exists.

This command is useful in scripting applications to verify the existence of
a Nextmv Cloud application version by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Check if the version with the ID <span style="color: #800080; text-decoration-color: #800080">v1</span> exists in application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version exists --app-id hare-app --version-id v1</span>

- Check if the version exists using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version exists --app-id hare-app --version-id v1 --profile hare</span>

**Usage**:

```console
$ cloud version exists [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Cloud version ID to use for this action.  [env var: NEXTMV_VERSION_ID; required]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud version get`

Get a Nextmv Cloud application version.

This command is useful to get the attributes of an existing Nextmv Cloud
application version by its ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the version with the ID <span style="color: #800080; text-decoration-color: #800080">v1</span> from application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version get --app-id hare-app --version-id v1</span>

- Get the version with the ID <span style="color: #800080; text-decoration-color: #800080">v1</span> and save the information to a
  <span style="color: #800080; text-decoration-color: #800080">version.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version get --app-id hare-app --version-id v1 --output version.json</span>

**Usage**:

```console
$ cloud version get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Cloud version ID to use for this action.  [env var: NEXTMV_VERSION_ID; required]
* `-o, --output OUTPUT_PATH`: Saves the version information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud version list`

List all versions of a Nextmv Cloud application.

By default this command paginates the list of versions, which means
multiple API calls may be made to retrieve all versions. You may use the
--no-pagination option to disable pagination.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all versions of application <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version list --app-id hare-app</span>

- List all versions using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version list --app-id hare-app --profile hare</span>

- List all versions and save the information to a <span style="color: #800080; text-decoration-color: #800080">versions.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version list --app-id hare-app --output versions.json</span>

- List all versions without pagination.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version list --app-id hare-app --no-pagination</span>

**Usage**:

```console
$ cloud version list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `--no-pagination`: Whether to disable pagination when listing this type of entity.
* `-o, --output OUTPUT_PATH`: Saves the version list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `cloud version update`

Updates a Nextmv Cloud application version.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update a version&#x27;s name.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version update --app-id hare-app --version-id v1 --name &quot;Version 1.0&quot;</span>

- Update a version&#x27;s description.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version update --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --description &quot;Initial stable release&quot;</span>

- Update a version&#x27;s name and description at once.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version update --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Version 1.0&quot; --description &quot;Initial stable release&quot;</span>

- Update a version and save the updated information to a <span style="color: #800080; text-decoration-color: #800080">updated_version.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv cloud version update --app-id hare-app --version-id v1 \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --name &quot;Version 1.0&quot; --output updated_version.json</span>

**Usage**:

```console
$ cloud version update [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The Nextmv Cloud application ID to use for this action.  [env var: NEXTMV_APP_ID; required]
* `-v, --version-id VERSION_ID`: The Nextmv Cloud version ID to use for this action.  [env var: NEXTMV_VERSION_ID; required]
* `-d, --description DESCRIPTION`: A new description for the version.
* `-n, --name NAME`: A new name for the version.
* `-o, --output OUTPUT_PATH`: Saves the updated version information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

## `community`

Interact with community apps, which are pre-built decision models.

Community apps are maintained in the following GitHub repository:
<span style="font-weight: bold"><a href="https://github.com/nextmv-io/community-apps">nextmv-io/community-apps</a></span>.

**Usage**:

```console
$ community [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clone`: Clone a community app locally.
* `list`: List the available community apps

### `community clone`

Clone a community app locally.

By default, the <span style="color: #800080; text-decoration-color: #800080">latest</span> version will be used. You can
specify a version with the --version flag, and customize the output
directory with the --directory flag. If you want to list the available
apps, use the <span style="font-weight: bold">nextmv community list</span> command. When an app is
cloned, it is automatically registered locally, so you can run it with the
<span style="font-weight: bold">nextmv local run</span> command using the generated app ID.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Clone the <span style="color: #800080; text-decoration-color: #800080">go-nextroute</span> community app (under the
  <span style="color: #800080; text-decoration-color: #800080">&quot;go-nextroute&quot;</span> directory), using the <span style="color: #800080; text-decoration-color: #800080">latest</span> version.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community clone --app go-nextroute</span>

- Clone the <span style="color: #800080; text-decoration-color: #800080">go-nextroute</span> community app under the
  <span style="color: #800080; text-decoration-color: #800080">&quot;~/sample/my_app&quot;</span> directory, using the <span style="color: #800080; text-decoration-color: #800080">latest</span> version.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community clone --app go-nextroute --directory ~/sample/my_app</span>

- Clone the <span style="color: #800080; text-decoration-color: #800080">go-nextroute</span> community app (under the
  <span style="color: #800080; text-decoration-color: #800080">&quot;go-nextroute&quot;</span> directory), using version <span style="color: #800080; text-decoration-color: #800080">v1.2.0</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community clone --app go-nextroute --version v1.2.0</span>

- Clone the <span style="color: #800080; text-decoration-color: #800080">go-nextroute</span> community app (under the
  <span style="color: #800080; text-decoration-color: #800080">&quot;go-nextroute&quot;</span> directory), using the <span style="color: #800080; text-decoration-color: #800080">latest</span> version
  and a profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community clone --app go-nextroute --profile hare</span>

**Usage**:

```console
$ community clone [OPTIONS]
```

**Options**:

* `-a, --app COMMUNITY_APP`: The name of the community app to clone.  [required]
* `-d, --directory DIRECTORY`: The directory in which to clone the app. Default is the name of the app at current directory.
* `-v, --version VERSION`: The version of the community app to clone.  [default: latest]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

### `community list`

List the available community apps

Use the --app flag to list that app&#x27;s versions. Use the --flat flag to
flatten the list of names/versions. If you want to clone a community app
locally, use the <span style="font-weight: bold">nextmv community clone</span> command.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List the available community apps.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community list</span>

- List the available versions of the <span style="color: #800080; text-decoration-color: #800080">go-nextroute</span> community app.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community list --app go-nextroute</span>

- List the names of the available community apps as a flat list.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community list --flat</span>

- List the available versions of the <span style="color: #800080; text-decoration-color: #800080">go-nextroute</span> community app as a flat list.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community list --app go-nextroute --flat</span>

- List the available community apps using a profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv community list --profile hare</span>

**Usage**:

```console
$ community list [OPTIONS]
```

**Options**:

* `-a, --app COMMUNITY_APP`: The community app to list versions for.
* `-f, --flat`: Flatten the list output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

## `configuration`

Configure the CLI and manage profiles.

**Usage**:

```console
$ configuration [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new configuration or update an...
* `delete`: Delete a profile from the configuration.
* `list`: List the current configuration and all...

### `configuration create`

Create a new configuration or update an existing one.

<span style="color: #800080; text-decoration-color: #800080">pkce</span> profiles require a separate login step via
<span style="font-weight: bold">nextmv auth login</span> before they can be used.

Multiple <span style="color: #800080; text-decoration-color: #800080">pkce</span> profiles can share a single browser login
by referencing the same <span style="color: #800080; text-decoration-color: #800080">--auth-session</span> name, automatically
done by default auth-session &#x27;default&#x27; if not specified.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Default configuration (prompts for type and API key or opens browser).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration create</span>

- Default API key configuration without prompting.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration create --api-key NEXTMV_API_KEY</span>

- Configure an <span style="color: #800080; text-decoration-color: #800080">api_key</span> profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration create --api-key NEXTMV_API_KEY --profile hare</span>

- Configure a named <span style="color: #800080; text-decoration-color: #800080">pkce</span> profile.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration create --profile hare --auth-type pkce</span>

- Configure two <span style="color: #800080; text-decoration-color: #800080">pkce</span> profiles that share a single login session.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration create --profile dev --auth-type pkce --auth-session my-work</span>
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration create --profile staging --auth-type pkce --auth-session my-work</span>

**Usage**:

```console
$ configuration create [OPTIONS]
```

**Options**:

* `-a, --api-key NEXTMV_API_KEY`: A valid Nextmv Cloud API key. Get one from <span style="font-weight: bold"><a href="https://cloud.nextmv.io">https://cloud.nextmv.io</a></span>. Setting this flag automatically selects the api_key auth type.  [env var: NEXTMV_API_KEY]
* `-s, --auth-session SESSION_NAME`: Named auth session to share tokens across profiles. Only applies to <span style="color: #800080; text-decoration-color: #800080">pkce</span> profiles.  [default: default]
* `-t, --auth-type AUTH_TYPE`: The authentication type for this profile. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">api_key</span> and <span style="color: #800080; text-decoration-color: #800080">pkce</span>. Ignored when --api-key is provided.  [default: (api_key)]
* `-p, --profile PROFILE_NAME`: Profile name to save the configuration under.  [env var: NEXTMV_PROFILE]
* `--email EMAIL`: Your login email to detect a third-party SSO provider. Only the domain part is stored.
* `--system-certs`: Use the operating system certificate store for TLS connections.
* `--team TEAM_NAME`: Team name to associate with this <span style="color: #800080; text-decoration-color: #800080">pkce</span> profile.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

### `configuration delete`

Delete a profile from the configuration.

Use the --yes flag to skip the confirmation prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete a profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration delete --profile hare</span>

- Delete a profile named <span style="color: #800080; text-decoration-color: #800080">hare</span> without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration delete --profile hare --yes</span>

**Usage**:

```console
$ configuration delete [OPTIONS]
```

**Options**:

* `-p, --profile PROFILE_NAME`: Profile name to delete.  [env var: NEXTMV_PROFILE; required]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

### `configuration list`

List the current configuration and all profiles.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Show current configuration and all profiles.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv configuration list</span>

**Usage**:

```console
$ configuration list [OPTIONS]
```

**Options**:

* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

## `init`

Get started with the Nextmv CLI.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Start the tutorial.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv init</span>

**Usage**:

```console
$ init [OPTIONS]
```

**Options**:

* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

## `local`

Interact with local Nextmv apps and make runs.

**Usage**:

```console
$ local [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `app`: Manage and sync local Nextmv applications.
* `run`: Create and manage Nextmv local application...

### `local app`

Manage and sync local Nextmv applications.

A Nextmv application is an entity that contains a decision model as
executable code. An application can make a run by taking an input,
executing the decision model, and producing an output.

**Usage**:

```console
$ local app [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: Deletes a Nextmv application from the...
* `get`: Get a registered local Nextmv application.
* `list`: List all local registered Nextmv...
* `register`: Register a local Nextmv application.
* `registered`: Check if a Nextmv application is...
* `sync`: Sync a local Nextmv application to the...
* `update`: Update a registered local Nextmv application.

#### `local app delete`

Deletes a Nextmv application from the local registry.

You may identify the app by using --app-src or --app-id. This action is
permanent and cannot be undone. Use the --yes flag to skip the confirmation
prompt.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Delete the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app delete --app-id hare-app</span>

- Delete the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> without confirmation prompt.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app delete --app-id hare-app --yes</span>

**Usage**:

```console
$ local app delete [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC]
* `-y, --yes`: Agree to deletion confirmation prompt. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local app get`

Get a registered local Nextmv application.

You may identify the app by using --app-src or --app-id.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app get --app-id hare-app</span>

- Get the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> and save the information to an
  <span style="color: #800080; text-decoration-color: #800080">app.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app get --app-id hare-app --output app.json</span>

**Usage**:

```console
$ local app get [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC]
* `-o, --output OUTPUT_PATH`: Saves the app information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local app list`

List all local registered Nextmv applications.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- List all registered applications.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app list</span>

- List all registered applications and save the information to an <span style="color: #800080; text-decoration-color: #800080">apps.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app list --output apps.json</span>

**Usage**:

```console
$ local app list [OPTIONS]
```

**Options**:

* `-o, --output OUTPUT_PATH`: Saves the app list information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local app register`

Register a local Nextmv application.

After an application is registered, you may use the resulting app ID to
interact with the application from different locations on your machine
without needing to specify the source path. You may also use the app ID to
refer to the application in other Nextmv CLI commands. If an app ID is not
provided, the CLI will generate one for you. The source path must be a
local path on your machine that contains a Nextmv application manifest
file (<span style="color: #800080; text-decoration-color: #800080">app.yaml</span>).

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Register a local application with the source path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app register --app-src ./my-app</span>

- Register a local application with the source path <span style="color: #800080; text-decoration-color: #800080">./my-app</span> and save the
  information to an <span style="color: #800080; text-decoration-color: #800080">app.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app register --app-src ./my-app --output app.json</span>

**Usage**:

```console
$ local app register [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC]
* `-d, --description DESCRIPTION`: An optional description for the application.
* `-o, --output OUTPUT_PATH`: Saves the app information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local app registered`

Check if a Nextmv application is registered locally.

You may identify the app by using --app-src or --app-id. This command is
useful in scripting applications to verify the existence of a local
application.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Check if the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> is registered.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app registered --app-id hare-app</span>

- Check if the application with source path <span style="color: #800080; text-decoration-color: #800080">./hare-app/</span> is registered.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app registered --app-src ./hare-app/</span>

**Usage**:

```console
$ local app registered [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local app sync`

Sync a local Nextmv application to the Nextmv Cloud.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. Using the --run-ids option allows you to specify a subset of
runs to sync. By default, all runs are synced. You can also specify an
--instance-id to associate the synced runs with a specific Cloud instance.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Sync the registered local application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> to the Cloud application
    with the ID <span style="color: #800080; text-decoration-color: #800080">hare-cloud-app</span>, syncing all runs.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app sync --target-app-id hare-cloud-app --app-id hare-app</span>

- Sync the local application at source path <span style="color: #800080; text-decoration-color: #800080">./hare_app</span> to the Cloud application
    with the ID <span style="color: #800080; text-decoration-color: #800080">hare-cloud-app</span>, syncing only runs <span style="color: #800080; text-decoration-color: #800080">run1, run2</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app sync --target-app-id hare-cloud-app --app-src ./hare_app \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --run-ids run1 --run-ids run2</span>

- Sync the registered local application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> to the Cloud application
    with the ID <span style="color: #800080; text-decoration-color: #800080">hare-cloud-app</span>, linking runs to instance <span style="color: #800080; text-decoration-color: #800080">fluffy-inst</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app sync --target-app-id hare-cloud-app --app-id hare-app --instance-id fluffy-inst</span>

- Sync local applications using the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app sync --target-app-id hare-cloud-app --app-id hare-app --profile hare</span>

**Usage**:

```console
$ local app sync [OPTIONS]
```

**Options**:

* `-t, --target-app-id TARGET_APP_ID`: The target Nextmv Cloud application ID to sync to.  [env var: NEXTMV_TARGET_APP_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC]
* `-i, --instance-id INSTANCE_ID`: Optional Cloud instance ID if you want to associate the runs with a specific instance.
* `-r, --run-ids RUN_IDS`: List of run IDs to sync. All are used if not specified. Pass multiple run IDs by repeating the flag.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `-p, --profile PROFILE_NAME`: Profile to use for this action. Use <span style="font-weight: bold">nextmv configuration</span> to manage profiles.  [env var: NEXTMV_PROFILE]
* `--help`: Show this message and exit.

#### `local app update`

Update a registered local Nextmv application.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. You can update the app&#x27;s ID through the --new-app-id option.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Update the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app update --app-id hare-app --description &quot;New description&quot;</span>

- Update the application with the ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span> and save the information to an
  <span style="color: #800080; text-decoration-color: #800080">app.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app update --app-id hare-app --description &quot;New description&quot; --output app.json</span>

- Update the ID of the application located at <span style="color: #800080; text-decoration-color: #800080">./my-app</span> to <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local app update --app-src ./my-app --new-app-id hare-app --description &quot;New description&quot;</span>

**Usage**:

```console
$ local app update [OPTIONS]
```

**Options**:

* `-d, --description DESCRIPTION`: A new description for the application.  [required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC]
* `-n, --new-app-id NEW_APP_ID`: A new ID for the local Nextmv application.
* `-o, --output OUTPUT_PATH`: Saves the app information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

### `local run`

Create and manage Nextmv local application runs.

A run represents the execution of a decision model within a Nextmv local
application. Each run takes an input, processes it using the decision model,
and produces an output.

**Usage**:

```console
$ local run [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `clone`: Clone an existing local application run.
* `compare`: Compare multiple Nextmv local application...
* `create`: Create a new local application run.
* `get`: Get the result (output) of a Nextmv local...
* `information`: Get the information of a Nextmv local...
* `input`: Get the input of a local application run.
* `list`: Get the list of runs for a Nextmv local...
* `logs`: Get the logs of a local application run.
* `metadata`: This command is deprecated, use... (DEPRECATED)
* `visuals`: Get the visuals of a Nextmv local...

#### `local run clone`

Clone an existing local application run.

All information of the original (cloned) run will be reused. You may
override any information you wish, such as the input, content format, or
options, for example. All the options for creating the new run work the
same way as in the <span style="font-weight: bold">nextmv local run create</span> command. You may
inspect the documentation of that command for more details on what each
option does.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Clone run <span style="color: #800080; text-decoration-color: #800080">run-123</span> from an app in the current directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input via <span style="color: #800080; text-decoration-color: #800080">stdin</span>, from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file,
  and create a run for an app in the current directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">cat input.json | nextmv local run clone --cloned-run-id run-123</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input input.json</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
  Wait for the run to complete and print the result to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json --wait</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
  Tail the run&#x27;s logs, streaming to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json --tail</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete and write the result to an <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete, and write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input input.json --logs logs.log</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and create a run for an app at
  path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>. Wait for the run to complete. Tail the run&#x27;s logs, streaming to
  <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file. Write the result to an
  <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json --tail \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --logs logs.log --output output.json</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  create a run for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input inputs \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --content-format multi-file</span>

- Clone a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete and save the result files to an <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-id hare-app --input inputs --output outputs</span>

- Clone a run with custom options for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run clone --cloned-run-id run-123 --app-src ./my-app --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --options duration=10s --options verbose=true</span>

**Usage**:

```console
$ local run clone [OPTIONS]
```

**Options**:

* `-r, --cloned-run-id CLONED_RUN_ID`: The original Nextmv run ID that you want to clone.  [env var: NEXTMV_CLONED_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-i, --input INPUT_PATH`: The input path to use. File or directory depending on content format. Uses <span style="color: #800080; text-decoration-color: #800080">stdin</span> if not defined. Can be a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file for multi-file content format.
* `-l, --logs LOGS_PATH`: Waits for the run to complete and saves the logs to this location.
* `-u, --output OUTPUT_PATH`: Waits for the run to complete and save the output to this location. A file or directory will be created depending on content format.
* `-t, --tail`: Tail the logs until the run completes. Logs are streamed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Specify log output location with --logs.
* `-w, --wait`: Wait for the run to complete. Run result is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span> for <span style="color: #800080; text-decoration-color: #800080">json</span>, to a dir for <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Specify output location with --output.
* `-c, --content-format CONTENT_FORMAT`: The content format of the run to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.
* `--description DESCRIPTION`: An optional description for the new run.
* `-n, --name NAME`: An optional name for the new run.
* `-o, --options KEY=VALUE`: Options passed to the run. Format: <span style="color: #800080; text-decoration-color: #800080">key=value</span>. Pass multiple options by repeating the flag, or separating with commas.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run compare`

Compare multiple Nextmv local application runs.

By default this command prints a human-readable table to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. You may use the --flat option to print the
comparison result to <span style="color: #800080; text-decoration-color: #800080">stdout</span> as <span style="color: #800080; text-decoration-color: #800080">json</span>
instead. When the --output option is used, the --flat flag is automatically
activated and the result is saved as <span style="color: #800080; text-decoration-color: #800080">json</span>.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Compare two runs belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>
  repeating the --run-ids flag.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run compare --app-id hare-app --run-ids fluff --run-ids white</span>

- Compare three runs belonging to an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>
  separating the run IDs with commas.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run compare --app-id hare-app --run-ids fluff,white,thumper</span>

- Compare two runs and print the result as <span style="color: #800080; text-decoration-color: #800080">json</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run compare --app-id hare-app --run-ids fluff,white --flat</span>

- Compare two runs and save the result to a file named <span style="color: #800080; text-decoration-color: #800080">comparison.json</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run compare --app-id hare-app --run-ids fluff,white --output comparison.json</span>

**Usage**:

```console
$ local run compare [OPTIONS]
```

**Options**:

* `-r, --run-ids RUN_IDS`: List of run IDs to compare. Pass multiple run IDs by repeating the flag, or separating with commas.  [required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-f, --flat`: Print the comparison result as <span style="color: #800080; text-decoration-color: #800080">json</span>, instead of a table.
* `-o, --output OUTPUT_PATH`: Saves the comparison result to this location. Activates the --flat option.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run create`

Create a new local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. Input for the run should be given through
<span style="color: #800080; text-decoration-color: #800080">stdin</span> or the --input flag. When using the --input flag,
the value can be one of the following:

- <span style="color: #808000; text-decoration-color: #808000">&lt;FILE_PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">file</span> containing
  the input data. Use with the <span style="color: #800080; text-decoration-color: #800080">json</span> content format.
- <span style="color: #808000; text-decoration-color: #808000">&lt;DIR_PATH&gt;</span>: path to a <span style="color: #800080; text-decoration-color: #800080">directory</span>
  containing the input data files. Use with the
  <span style="color: #800080; text-decoration-color: #800080">multi-file</span> content format.

The CLI determines how to send the input to the application based on the
value.

Use the --wait flag to wait for the run to complete, polling for results.
Using the --output flag will also activate waiting, and allows you to
specify a destination (file or dir) for the output, depending on the
content type.

Use the --tail flag to stream logs to <span style="color: #800080; text-decoration-color: #800080">stderr</span> until the
run completes. Using the --logs flag will also activate waiting, and allows
you to specify a file to write the logs to.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input via <span style="color: #800080; text-decoration-color: #800080">stdin</span>, from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file,
  and create a run for an app at the current directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">cat input.json | nextmv local run create</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-id hare-app --input input.json</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
  Wait for the run to complete and print the result to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-src ./my-app --input input.json --wait</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
  Tail the run&#x27;s logs, streaming to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-src ./my-app --input input.json --tail</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete and write the result to an <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-id hare-app --input input.json --output output.json</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete, and write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-id hare-app --input input.json --logs logs.log</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">json</span> input from an <span style="color: #800080; text-decoration-color: #800080">input.json</span> file, and create a run for an app at
  path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>. Wait for the run to complete. Tail the run&#x27;s logs, streaming to
  <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Write the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file. Write the result to an
  <span style="color: #800080; text-decoration-color: #800080">output.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-src ./my-app --input input.json --tail --logs logs.log \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --output output.json</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  create a run for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-src ./my-app --input inputs --content-format multi-file</span>

- Read a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> input from an <span style="color: #800080; text-decoration-color: #800080">inputs</span> directory, and
  create a run for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Wait for the run to complete and save the result files to an <span style="color: #800080; text-decoration-color: #800080">outputs</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-id hare-app --input inputs --output outputs</span>

- Create a run with custom options for an app at path <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run create --app-src ./my-app --input input.json \</span>
<span style="color: #7f7f7f; text-decoration-color: #7f7f7f">        --options duration=10s --options verbose=true</span>

**Usage**:

```console
$ local run create [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-i, --input INPUT_PATH`: The input path to use. File or directory depending on content format. Uses <span style="color: #800080; text-decoration-color: #800080">stdin</span> if not defined. Can be a <span style="color: #800080; text-decoration-color: #800080">.tar.gz</span> file for multi-file content format.
* `-l, --logs LOGS_PATH`: Waits for the run to complete and saves the logs to this location.
* `-u, --output OUTPUT_PATH`: Waits for the run to complete and save the output to this location. A file or directory will be created depending on content format.
* `-t, --tail`: Tail the logs until the run completes. Logs are streamed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Specify log output location with --logs.
* `-w, --wait`: Wait for the run to complete. Run result is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span> for <span style="color: #800080; text-decoration-color: #800080">json</span>, to a dir for <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Specify output location with --output.
* `-c, --content-format CONTENT_FORMAT`: The content format of the run to create. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>.
* `--description DESCRIPTION`: An optional description for the new run.
* `-n, --name NAME`: An optional name for the new run.
* `-o, --options KEY=VALUE`: Options passed to the run. Format: <span style="color: #800080; text-decoration-color: #800080">key=value</span>. Pass multiple options by repeating the flag, or separating with commas.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run get`

Get the result (output) of a Nextmv local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. Use the --wait flag to wait for the run to complete, polling
for results. Using the --output flag will also activate waiting, and allows
you to specify a destination (file or dir) for the output, depending on the
content type.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run get --app-id hare-app --run-id burrow-123</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Wait for the run to complete if necessary.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run get --app-id hare-app --run-id burrow-123 --wait</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. The app is a <span style="color: #800080; text-decoration-color: #800080">json</span> app.
  Save the results to a <span style="color: #800080; text-decoration-color: #800080">results.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run get --app-id hare-app --run-id burrow-123 --output results.json</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. The app is a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> app.
  Save the results to the <span style="color: #800080; text-decoration-color: #800080">results</span> dir.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run get --app-id hare-app --run-id burrow-123 --output results</span>

- Get the results of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run get --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ local run get [OPTIONS]
```

**Options**:

* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-o, --output OUTPUT_PATH`: Waits for the run to complete and save the output to this location. A file or directory will be created depending on content format.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `-w, --wait`: Wait for the run to complete. Run result is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span> for <span style="color: #800080; text-decoration-color: #800080">json</span>, to a dir for <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Specify output location with --output.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run information`

Get the information of a Nextmv local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. By default, the information (including metadata) is fetched
and printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>. Use the --output flag to save the
information to a file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the information of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Information is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run information --app-id hare-app --run-id burrow-123</span>

- Get the information of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the information to a <span style="color: #800080; text-decoration-color: #800080">information.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run information --app-id hare-app --run-id burrow-123 --output information.json</span>

- Get the information of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run information --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ local run information [OPTIONS]
```

**Options**:

* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-o, --output OUTPUT_PATH`: Saves the information to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run input`

Get the input of a local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. By default, the input is fetched and printed to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. Use the --output flag to save the input to a
file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the input of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Input is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run input --app-id hare-app --run-id burrow-123</span>

- Get the input of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the input to a <span style="color: #800080; text-decoration-color: #800080">input.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run input --app-id hare-app --run-id burrow-123 --output input.json</span>

- Get the input of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run input --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ local run input [OPTIONS]
```

**Options**:

* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-o, --output OUTPUT_PATH`: Saves the input to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run list`

Get the list of runs for a Nextmv local application.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. By default, the list of runs is fetched and printed to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. Use the --output flag to save the list to a
file. You can use the optional --status flag to filter runs by their status.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. List is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run list --app-id hare-app</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the list to a
  <span style="color: #800080; text-decoration-color: #800080">runs.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run list --app-id hare-app --output runs.json</span>

- Get the list of runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
  Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run list --app-id hare-app --profile hare</span>

- Get the list of <span style="color: #800080; text-decoration-color: #800080">queued</span> runs for an app with ID <span style="color: #800080; text-decoration-color: #800080">hare-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run list --app-id hare-app --status queued</span>

**Usage**:

```console
$ local run list [OPTIONS]
```

**Options**:

* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-o, --output OUTPUT_PATH`: Saves the list of runs to this location.
* `-t, --status STATUS`: Filter runs by their status. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">canceled</span>, <span style="color: #800080; text-decoration-color: #800080">failed</span>, <span style="color: #800080; text-decoration-color: #800080">none</span>, <span style="color: #800080; text-decoration-color: #800080">queued</span>, <span style="color: #800080; text-decoration-color: #800080">running</span>, and <span style="color: #800080; text-decoration-color: #800080">succeeded</span>.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run logs`

Get the logs of a local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it.

By default, the logs are fetched and printed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
Use the --tail flag to stream logs to <span style="color: #800080; text-decoration-color: #800080">stderr</span> until the
run completes. Using the --output flag will also activate waiting, and
allows you to specify a file to write the logs to.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Logs are printed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run logs --app-id hare-app --run-id burrow-123</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Tail the logs until the run completes.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run logs --app-id hare-app --run-id burrow-123 --tail</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the logs to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run logs --app-id hare-app --run-id burrow-123 --output logs.log</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Tail the logs and save them to a <span style="color: #800080; text-decoration-color: #800080">logs.log</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run logs --app-id hare-app --run-id burrow-123 --tail --output logs.log</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with source path
  <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run logs --app-src ./my-app --run-id burrow-123</span>

- Get the logs of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with source path
  <span style="color: #800080; text-decoration-color: #800080">./my-app</span>. Set a timeout of <span style="color: #800080; text-decoration-color: #800080">60</span> seconds.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run logs --app-src ./my-app --run-id burrow-123 --timeout 60</span>

**Usage**:

```console
$ local run logs [OPTIONS]
```

**Options**:

* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-o, --output OUTPUT_PATH`: Waits for the run to complete and saves the logs to this location.
* `-t, --tail`: Tail the logs until the run completes. Logs are streamed to <span style="color: #800080; text-decoration-color: #800080">stderr</span>. Specify log output location with --output.
* `--timeout TIMEOUT_SECONDS`: The maximum time in seconds to wait for results when polling. Poll indefinitely if not set.  [default: -1]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run metadata`

This command is deprecated, use <span style="font-weight: bold">nextmv local run information</span> instead.

Get the metadata of a Nextmv local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it. By default, the metadata is fetched and printed to
<span style="color: #800080; text-decoration-color: #800080">stdout</span>. Use the --output flag to save the metadata to a
file.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the metadata of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Metadata is printed to <span style="color: #800080; text-decoration-color: #800080">stdout</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run metadata --app-id hare-app --run-id burrow-123</span>

- Get the metadata of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Save the metadata to a <span style="color: #800080; text-decoration-color: #800080">metadata.json</span> file.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run metadata --app-id hare-app --run-id burrow-123 --output metadata.json</span>

- Get the metadata of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Use the profile named <span style="color: #800080; text-decoration-color: #800080">hare</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run metadata --app-id hare-app --run-id burrow-123 --profile hare</span>

**Usage**:

```console
$ local run metadata [OPTIONS]
```

**Options**:

* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `-o, --output OUTPUT_PATH`: Saves the metadata to this location.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

#### `local run visuals`

Get the visuals of a Nextmv local application run.

You may identify the app by using --app-src, or --app-id if it has been
registered. If the app is not already registered, this command will
register it.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Get the visuals of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with ID
  <span style="color: #800080; text-decoration-color: #800080">hare-app</span>. Visuals are opened in a web browser.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run visuals --app-id hare-app --run-id burrow-123</span>

- Get the visuals of a run with ID <span style="color: #800080; text-decoration-color: #800080">burrow-123</span>, belonging to an app with source path
  <span style="color: #800080; text-decoration-color: #800080">./my-app</span>.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv local run visuals --app-src ./my-app --run-id burrow-123</span>

**Usage**:

```console
$ local run visuals [OPTIONS]
```

**Options**:

* `-r, --run-id RUN_ID`: The Nextmv run ID to use for this action.  [env var: NEXTMV_RUN_ID; required]
* `-a, --app-id APP_ID`: The local Nextmv application ID to use for this action.  [env var: NEXTMV_APP_ID]
* `-s, --app-src APP_SRC`: The source (filesystem path) of the local Nextmv application to use for this action. Defaults to the current working directory.  [env var: NEXTMV_APP_SRC; default: .]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

## `manifest`

Manage <span style="color: #800080; text-decoration-color: #800080">app.yaml</span> (app manifest/config) files.

**Usage**:

```console
$ manifest [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `init`: Initialize an <span style="color: #800080; text-decoration-color: #800080">app.yaml</span>...
* `validate`: Validate an <span style="color: #800080; text-decoration-color: #800080">app.yaml</span>...

### `manifest init`

Initialize an <span style="color: #800080; text-decoration-color: #800080">app.yaml</span> (app manifest) file.

Creates a sample <span style="color: #800080; text-decoration-color: #800080">app.yaml</span> manifest file by prompting the
user to provide certain information. You can use --content-format,
--dirpath, --type, --options-yes, and --options-no to skip the prompts. If
the directory does not exist, it will be created. If a manifest file
already exists in the directory, it will be overwritten.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Initialize a Python manifest in the current directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv manifest init</span>

- Initialize a <span style="color: #800080; text-decoration-color: #800080">json</span> Go manifest in the <span style="color: #800080; text-decoration-color: #800080">./my-app</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv manifest init --type go --content-format json --dirpath ./my-app</span>

- Initialize a <span style="color: #800080; text-decoration-color: #800080">multi-file</span> Java manifest in the <span style="color: #800080; text-decoration-color: #800080">./my-app</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv manifest init --type java --content-format multi-file --dirpath ./my-app</span>

**Usage**:

```console
$ manifest init [OPTIONS]
```

**Options**:

* `-c, --content-format CONTENT_FORMAT`: The content format of the manifest. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">json</span> and <span style="color: #800080; text-decoration-color: #800080">multi-file</span>. Useful for non-interactive sessions.
* `-d, --dirpath DIRPATH`: The directory path where the manifest file will be initialized. Useful for non-interactive sessions.
* `-t, --type TYPE`: The type of manifest to initialize. Allowed values are: <span style="color: #800080; text-decoration-color: #800080">python</span>, <span style="color: #800080; text-decoration-color: #800080">go</span>, <span style="color: #800080; text-decoration-color: #800080">java</span>, and <span style="color: #800080; text-decoration-color: #800080">binary</span>. Useful for non-interactive sessions.
* `-y, --options-yes`: Add options (parameters) to the manifest. Useful for non-interactive sessions.
* `-n, --options-no`: Do not add options (parameters) to the manifest. Useful for non-interactive sessions.
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

### `manifest validate`

Validate an <span style="color: #800080; text-decoration-color: #800080">app.yaml</span> (app manifest) file.

Loads the <span style="color: #800080; text-decoration-color: #800080">app.yaml</span> manifest from the given directory and
validates it. If no directory is provided, the current directory is used.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Validate the manifest in the current directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv manifest validate</span>

- Validate the manifest in the <span style="color: #800080; text-decoration-color: #800080">./my-app</span> directory.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv manifest validate --dirpath ./my-app</span>

**Usage**:

```console
$ manifest validate [OPTIONS]
```

**Options**:

* `-d, --dirpath DIRPATH`: The directory path where the manifest file is located. Defaults to the current directory.  [default: .]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

## `version`

Show the current version of the Nextmv CLI.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Show the version.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv version</span>

**Usage**:

```console
$ version [OPTIONS]
```

**Options**:

* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.

## `mcp`

Model Context Protocol (MCP) server for LLM integrations.

Start an MCP server so that any MCP-compatible client (Claude Code,
Cursor, VS Code, etc.) can interact with Nextmv Cloud through natural
language.

<span style="font-weight: bold; text-decoration: underline">Quick start</span>

- Register with Claude Code.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">claude mcp add nextmv -- nextmv mcp serve</span>

**Usage**:

```console
$ mcp [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `serve`: Start the Nextmv MCP server.

### `mcp serve`

Start the Nextmv MCP server.

The MCP server exposes Nextmv Cloud functionality as tools that any
MCP-compatible client can use. The default transport is
<span style="color: #800080; text-decoration-color: #800080">stdio</span>, which is what Claude Code, Cursor, and most
local clients expect.

<span style="font-weight: bold; text-decoration: underline">Examples</span>

- Start the MCP server with stdio transport (default).
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv mcp serve</span>

- Start the MCP server with HTTP transport on port 9090.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">nextmv mcp serve --transport streamable-http --port 9090</span>

- Register with Claude Code.
    $ <span style="color: #7f7f7f; text-decoration-color: #7f7f7f">claude mcp add nextmv -- nextmv mcp serve</span>

**Usage**:

```console
$ mcp serve [OPTIONS]
```

**Options**:

* `--port PORT`: Port for the HTTP transport.  [default: 8080]
* `-t, --transport TRANSPORT`: Transport protocol. Allowed values: <span style="color: #800080; text-decoration-color: #800080">stdio</span>, <span style="color: #800080; text-decoration-color: #800080">streamable-http</span>.  [default: stdio]
* `--debug`: Enable debug mode, which will print out the full traceback in case of errors.
* `--help`: Show this message and exit.
