# Options

!!! tip "Reference"

    Find the reference for the `options` module [here](../reference/options.md).

Use options to capture parameters (i.e.: configurations) for the run. The
`ModelOptions` class captures the native `gurobipy` parameters, and the
`to_nextmv()` method allows you to convert them to [`nextmv`
options][nextmv-options], for convenience.

```python
import nextmv_gurobipy as ngp

options = ngp.ModelOptions().to_nextmv()
options.parse()
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or
environment variables.

options:
  -h, --help            show this help message and exit
  -AggFill AGGFILL, --AggFill AGGFILL
                        [env var: AGGFILL] (default: -1) (type: int): Controls
                        the amount of fill allowed during presolve
                        aggregation. Larger values generally lead to presolved
                        models with fewer rows and columns, but with more
                        constraint matrix non-zeros. The default value chooses
                        automatically, and usually works well.
  -Aggregate AGGREGATE, --Aggregate AGGREGATE
                        [env var: AGGREGATE] (default: 1) (type: int):
                        Controls the aggregation level in presolve. The
                        options are off (0), moderate (1), or aggressive (2).
                        In rare instances, aggregation can lead to an
                        accumulation of numerical errors. Turning it off can
                        sometimes improve solution accuracy.
  -BQPCuts BQPCUTS, --BQPCuts BQPCUTS
                        [env var: BQPCUTS] (default: -1) (type: int): Controls
                        Boolean Quadric Polytope (BQP) cut generation. Use 0
                        to disable these cuts, 1 for moderate cut generation,
                        or 2 for aggressive cut generation. The default -1
                        value chooses automatically. Overrides the Cuts
                        parameter. Note: Only affects mixed integer
                        programming (MIP) models
  ...
  ... (truncated for brevity)
  ...
  -WorkerPool WORKERPOOL, --WorkerPool WORKERPOOL
                        [env var: WORKERPOOL] (default: ) (type: str): When
                        using a distributed algorithm (distributed MIP,
                        distributed concurrent, or distributed tuning), this
                        parameter allows you to specify a Remote Services
                        cluster that will provide distributed workers. You
                        should also specify the access password for that
                        cluster, if there is one, in the WorkerPassword
                        parameter. Note that you don’t need to set either of
                        these parameters if your job is running on a Compute
                        Server node and you want to use the same cluster for
                        the distributed workers. You can provide a comma-
                        separated list of machines for added robustness. If
                        the first node in the list is unavailable, the client
                        will attempt to contact the second node, etc. To give
                        an example, if you have a Remote Services cluster that
                        uses port 61000 on a pair of machines named "server1"
                        and "server2", you could set WorkerPool to
                        ""server1:61000"" or ""server1:61000,server2:61000"".
  -ZeroHalfCuts ZEROHALFCUTS, --ZeroHalfCuts ZEROHALFCUTS
                        [env var: ZEROHALFCUTS] (default: -1) (type: int):
                        Controls zero-half cut generation. Use 0 to disable
                        these cuts, 1 for moderate cut generation, or 2 for
                        aggressive cut generation. The default -1 value
                        chooses automatically. Overrides the Cuts parameter.
                        Note: Only affects mixed integer programming (MIP)
                        models
  -ZeroObjNodes ZEROOBJNODES, --ZeroObjNodes ZEROOBJNODES
                        [env var: ZEROOBJNODES] (default: -1) (type: int):
                        Number of nodes to explore in the zero objective
                        heuristic. This heuristic is quite expensive, and
                        generally produces poor quality solutions. You should
                        generally only use it if other means, including
                        exploration of the tree with default settings, fail to
                        produce a feasible solution. Note: Only affects mixed
                        integer programming (MIP) models
```

You can merge `nextmv.Options` together using the `merge` method.

```python
import nextmv_gurobipy as ngp

import nextmv

opt = nextmv.Options(
    nextmv.Option("input", str, "", "Path to input file. Default is stdin.", False),
    nextmv.Option("output", str, "", "Path to output file. Default is stdout.", False),
)
gp_opt = ngp.ModelOptions().to_nextmv()
options = opt.merge(gp_opt)
```

```bash
$ python main.py --help
usage: main.py [options]

Options for main.py. Use command-line arguments (highest precedence) or
environment variables.

options:
  -h, --help            show this help message and exit
  -input INPUT, --input INPUT
                        [env var: INPUT] (default: ) (type: str): Path to
                        input file. Default is stdin.
  -output OUTPUT, --output OUTPUT
                        [env var: OUTPUT] (default: ) (type: str): Path to
                        output file. Default is stdout.
  -AggFill AGGFILL, --AggFill AGGFILL
                        [env var: AGGFILL] (default: -1) (type: int): Controls
                        the amount of fill allowed during presolve
                        aggregation. Larger values generally lead to presolved
                        models with fewer rows and columns, but with more
                        constraint matrix non-zeros. The default value chooses
                        automatically, and usually works well.
  -Aggregate AGGREGATE, --Aggregate AGGREGATE
                        [env var: AGGREGATE] (default: 1) (type: int):
                        Controls the aggregation level in presolve. The
                        options are off (0), moderate (1), or aggressive (2).
                        In rare instances, aggregation can lead to an
                        accumulation of numerical errors. Turning it off can
                        sometimes improve solution accuracy.
  -BQPCuts BQPCUTS, --BQPCuts BQPCUTS
                        [env var: BQPCUTS] (default: -1) (type: int): Controls
                        Boolean Quadric Polytope (BQP) cut generation. Use 0
...
... (truncated for brevity)
...
```

Notice how the `ModelOptions` are merged with the `nextmv.Options` and you can
access the options from both sets.

[nextmv-options]: ../../nextmv/tutorials/options.md
