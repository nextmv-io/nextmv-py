# Nextmv library tests

Make sure you have dev requisites installed:

```bash
pip install -e '.[dev]'
```

## Unit tests

Run unit tests with:

```bash
pytest --ignore=tests/integration
```

This will ignore integration tests located in `tests/integration`.

## Integration tests

Make sure you have a valid Nextmv Cloud API key set in your environment:

```bash
export NEXTMV_API_KEY="<YOUR_API_KEY>"
```

Run integration tests with:

```bash
pytest tests/integration -s
```

The integration tests use [Nextpipe][nextpipe] to orchestrate a workflow of
steps that run both in sequence and in parallel. Here is a mermaid diagram of
the steps that are run in the integration tests. This diagram was generated at
the time of writing, and may change as the tests are updated.

```mermaid
 graph LR
  init_app(init_app)
  init_app --> community_push
  init_app --> versions
  init_app --> instances
  init_app --> runs
  init_app --> input_sets
  init_app --> scenario_tests
  init_app --> shadow_tests
  init_app --> switchback_tests
  init_app --> acceptance_tests
  init_app --> secrets
  init_app --> ensembles
  init_app --> cleanup
  community_push(community_push)
  community_push --> versions
  community_push --> secrets
  versions(versions)
  versions --> instances
  versions --> cleanup
  instances(instances)
  instances --> runs
  instances --> input_sets
  instances --> scenario_tests
  instances --> shadow_tests
  instances --> switchback_tests
  instances --> acceptance_tests
  instances --> ensembles
  instances --> cleanup
  runs(runs)
  runs --> input_sets
  runs --> cleanup
  input_sets(input_sets)
  input_sets --> scenario_tests
  input_sets --> acceptance_tests
  input_sets --> cleanup
  scenario_tests(scenario_tests)
  scenario_tests --> cleanup
  shadow_tests(shadow_tests)
  shadow_tests --> switchback_tests
  shadow_tests --> cleanup
  switchback_tests(switchback_tests)
  switchback_tests --> cleanup
  acceptance_tests(acceptance_tests)
  acceptance_tests --> cleanup
  secrets(secrets)
  secrets --> cleanup
  ensembles(ensembles)
  ensembles --> cleanup
  cleanup(cleanup)
```

[nextpipe]: https://github.com/nextmv-io/nextpipe
