import os
from typing import Any

import numpy as np
from pyomo.environ import (
    ConcreteModel,
    Constraint,
    NonNegativeReals,
    Objective,
    RangeSet,
    SolverFactory,
    Var,
    minimize,
    value,
)
from visuals import allocation_chart

import nextmv

STATUS_MAP = {
    "optimal": "optimal",
    "feasible": "suboptimal",
    "infeasible": "infeasible",
    "unbounded": "unbounded",
}


def main() -> None:
    """Entry point for the inventory allocation model.

    Loads the manifest and options, parses inputs, builds and solves the
    optimization model, and writes the output. If the solver reports an
    infeasible or unbounded status the function writes an empty solution and
    returns early.
    """

    manifest = nextmv.Manifest.from_yaml(".")
    options = manifest.extract_options()

    inp = nextmv.load(options=options)
    demand, supply, num_warehouses, num_stores, store_labels, warehouse_labels, cost = parse_inputs(inp.data)

    nextmv.log(f"Warehouses: {num_warehouses}, total supply: {sum(supply)}")
    nextmv.log(f"Stores: {num_stores}, total demand: {sum(demand)}")
    nextmv.log(f"Penalty per unmet unit: {options.penalty_unmet_demand}")
    nextmv.log(f"Cost threshold: {options.cost_threshold}")
    nextmv.log(f"Supply utilization min: {options.supply_utilization_min}")

    model = build_model(demand, supply, cost, options)
    results, solver_name, mapped_status = solve_model(model, options)

    if mapped_status in ("infeasible", "unbounded"):
        output = nextmv.Output(
            solution={"allocations": [], "unmet_demand": []},
            metrics={
                "status": mapped_status,
                "total_demand": sum(demand),
                "total_supply": sum(supply),
                "solver": solver_name,
            },
        )
    else:
        model.solutions.load_from(results)
        output = extract_solution(
            model,
            demand,
            supply,
            cost,
            warehouse_labels,
            store_labels,
            solver_name,
            mapped_status,
        )

    nextmv.write(output)


def parse_inputs(
    data: dict[str, Any],
) -> tuple[
    list[int],
    list[int],
    int,
    int,
    list[str],
    list[str],
    list[list[float]],
]:
    """Parse input data into demand, supply, cost arrays and labels.

    Supports two input modes. In *explicit* mode the caller provides
    ``demand`` and ``supply`` lists directly (e.g. from an upstream forecast
    step). In *legacy* mode demand and supply are generated randomly using
    NumPy from size/range fields in *data*.

    Parameters
    ----------
    data : dict[str, Any]
        Raw input payload, typically loaded from a JSON file via
        :func:`nextmv.load`. Expected keys differ by mode:

        Explicit mode
            ``demand`` : list[int]
                Units demanded by each store.
            ``supply`` : list[int]
                Units available at each warehouse.
            ``store_names`` : list[str], optional
                Human-readable store labels; defaults to ``"Store {i}"``.
            ``warehouse_names`` : list[str], optional
                Human-readable warehouse labels; defaults to
                ``"Warehouse {i}"``.
            ``cost`` : list[list[float]], optional
                Transport cost matrix ``cost[w][s]``; generated randomly
                when absent.
            ``seed`` : int, optional
                RNG seed for cost generation (default ``42``).

        Legacy mode
            ``num_warehouses`` : int, optional
                Number of warehouses (default ``5``).
            ``num_stores`` : int, optional
                Number of stores (default ``10``).
            ``supply_range`` : list[int, int], optional
                ``[low, high)`` range for random supply (default
                ``[100, 300]``).
            ``demand_range`` : list[int, int], optional
                ``[low, high)`` range for random demand (default
                ``[50, 150]``).
            ``seed`` : int, optional
                NumPy random seed (default ``42``).

    Returns
    -------
    demand : list[int]
        Units demanded by each store, length *num_stores*.
    supply : list[int]
        Units available at each warehouse, length *num_warehouses*.
    num_warehouses : int
        Total number of warehouses.
    num_stores : int
        Total number of stores.
    store_labels : list[str]
        Human-readable label for each store.
    warehouse_labels : list[str]
        Human-readable label for each warehouse.
    cost : list[list[float]]
        Transport cost matrix of shape ``(num_warehouses, num_stores)``
        where ``cost[w][s]`` is the cost per unit shipped from warehouse
        *w* to store *s*.
    """
    if "demand" in data and "supply" in data:
        demand = [int(d) for d in data["demand"]]
        supply = [int(s) for s in data["supply"]]
        num_stores = len(demand)
        num_warehouses = len(supply)
        store_labels = data.get("store_names", [f"Store {s}" for s in range(num_stores)])
        warehouse_labels = data.get("warehouse_names", [f"Warehouse {w}" for w in range(num_warehouses)])
        if "cost" in data:
            cost = data["cost"]
        else:
            rng = np.random.default_rng(data.get("seed", 42))
            cost = np.round(rng.uniform(1, 10, size=(num_warehouses, num_stores)), 2).tolist()
    else:
        # Legacy mode: generate demand and supply randomly from ranges.
        np.random.seed(data.get("seed", 42))
        num_warehouses = data.get("num_warehouses", 5)
        num_stores = data.get("num_stores", 10)
        supply = np.random.randint(*data.get("supply_range", [100, 300]), size=num_warehouses).tolist()
        demand = np.random.randint(*data.get("demand_range", [50, 150]), size=num_stores).tolist()
        cost = np.round(np.random.uniform(1, 10, size=(num_warehouses, num_stores)), 2).tolist()
        store_labels = [f"Store {s}" for s in range(num_stores)]
        warehouse_labels = [f"Warehouse {w}" for w in range(num_warehouses)]

    return demand, supply, num_warehouses, num_stores, store_labels, warehouse_labels, cost


def build_model(
    demand: list[int],
    supply: list[int],
    cost: list[list[float]],
    options: nextmv.Options,
) -> ConcreteModel:
    """Build the Pyomo optimization model with all variables and constraints.

    Constructs a continuous linear program that minimises total transport cost
    plus a penalty for unmet demand. Optionally excludes lanes whose unit
    cost exceeds *options.cost_threshold* and enforces a minimum aggregate
    supply-utilisation level.

    Parameters
    ----------
    demand : list[int]
        Units demanded by each store, length *num_stores*.
    supply : list[int]
        Units available at each warehouse, length *num_warehouses*.
    cost : list[list[float]]
        Transport cost matrix of shape ``(num_warehouses, num_stores)``
        where ``cost[w][s]`` is the unit cost from warehouse *w* to store *s*.
    options : nextmv.Options
        Parsed run options. Relevant fields:

        ``penalty_unmet_demand`` : float
            Penalty coefficient applied to each unit of unmet demand.
        ``cost_threshold`` : float
            Lanes with unit cost above this value are excluded (upper-bounded
            to zero). No lanes are excluded when this is ``0``.
        ``supply_utilization_min`` : float
            Minimum fraction of total supply that must be shipped. No
            constraint is added when this is ``0``.

    Returns
    -------
    model : ConcreteModel
        Fully-constructed Pyomo ``ConcreteModel`` ready to be passed to a
        solver. Contains the following components:

        ``W`` : RangeSet
            Warehouse indices ``0 … num_warehouses - 1``.
        ``S`` : RangeSet
            Store indices ``0 … num_stores - 1``.
        ``x[w, s]`` : Var
            Non-negative continuous decision variable: units shipped from
            warehouse *w* to store *s*.
        ``unmet[s]`` : Var
            Non-negative continuous slack variable: unmet demand at store *s*.
        ``obj`` : Objective
            Minimise transport cost plus unmet-demand penalty.
        ``supply_con`` : Constraint
            Total shipments from each warehouse do not exceed its supply.
        ``demand_con`` : Constraint
            Shipments to each store plus slack equal its demand.
        ``supply_util_con`` : Constraint, optional
            Total units shipped are at least
            ``supply_utilization_min * sum(supply)``.
    """
    num_warehouses = len(supply)
    num_stores = len(demand)
    W = range(num_warehouses)
    S = range(num_stores)

    if options.cost_threshold > 0:
        excluded = sum(1 for w in W for s in S if cost[w][s] > options.cost_threshold)
        nextmv.log(f"Excluded {excluded} lanes above cost threshold {options.cost_threshold}")

    model = ConcreteModel()
    model.W = RangeSet(0, num_warehouses - 1)
    model.S = RangeSet(0, num_stores - 1)

    model.x = Var(model.W, model.S, domain=NonNegativeReals)
    model.unmet = Var(model.S, domain=NonNegativeReals)

    if options.cost_threshold > 0:
        for w in W:
            for s in S:
                if cost[w][s] > options.cost_threshold:
                    model.x[w, s].setub(0)

    model.obj = Objective(
        expr=(
            sum(cost[w][s] * model.x[w, s] for w in W for s in S)
            + options.penalty_unmet_demand * sum(model.unmet[s] for s in S)
        ),
        sense=minimize,
    )

    model.supply_con = Constraint(
        model.W,
        rule=lambda m, w: sum(m.x[w, s] for s in S) <= supply[w],
    )

    model.demand_con = Constraint(
        model.S,
        rule=lambda m, s: sum(m.x[w, s] for w in W) + m.unmet[s] == demand[s],
    )

    if options.supply_utilization_min > 0:
        min_required = options.supply_utilization_min * sum(supply)
        if min_required > sum(demand):
            nextmv.log(
                f"Warning: supply_utilization_min ({options.supply_utilization_min}) "
                f"requires {min_required:.0f} units shipped but total demand is only {sum(demand)} — "
                "model will be infeasible."
            )
        model.supply_util_con = Constraint(
            expr=sum(model.x[w, s] for w in W for s in S) >= min_required,
        )

    return model


def solve_model(
    model: ConcreteModel,
    options: nextmv.Options,
) -> tuple[Any, str, str]:
    """Solve the model and return the raw results, solver name, and mapped status.

    Selects the appropriate Pyomo solver backend from :data:`SOLVER_MAP`,
    applies the configured time limit, and redirects stdout to stderr during
    the solve call so that solver noise does not pollute the JSON output
    stream.

    Parameters
    ----------
    model : ConcreteModel
        A fully-constructed Pyomo model as returned by :func:`build_model`.
    options : nextmv.Options
        Parsed run options. Relevant fields:

        ``solver`` : str
            Solver key; must be one of ``"highs"``, ``"cbc"``, or
            ``"glpk"``. Defaults to ``"highs"`` when unrecognised.
        ``time_limit`` : float
            Maximum wall-clock seconds allowed for the solve.

    Returns
    -------
    results : Any
        Raw Pyomo solver results object (``SolverResults``). Solutions are
        *not* loaded into the model; call
        ``model.solutions.load_from(results)`` separately after checking the
        status.
    solver_name : str
        The normalised solver key used (e.g. ``"highs"``).
    mapped_status : str
        Human-readable status string mapped through :data:`STATUS_MAP`
        (e.g. ``"optimal"``, ``"suboptimal"``, ``"infeasible"``,
        ``"unbounded"``).

    Raises
    ------
    RuntimeError
        If the selected solver backend is not installed or not found on
        ``PATH``.
    """
    solver_choice, time_limit_key = "highs", "time_limit"

    solver = SolverFactory(solver_choice)
    if not solver.available():
        raise RuntimeError(f"Solver '{solver_choice}' is not installed or not on PATH.")
    solver.options[time_limit_key] = options.time_limit

    _saved = os.dup(1)
    os.dup2(2, 1)
    results = solver.solve(model, load_solutions=False)
    os.dup2(_saved, 1)
    os.close(_saved)

    status = str(results.solver.termination_condition)
    nextmv.log(f"Solver status: {status}")
    mapped_status = STATUS_MAP.get(status, status)

    return results, solver_choice, mapped_status


def extract_solution(
    model: ConcreteModel,
    demand: list[int],
    supply: list[int],
    cost: list[list[float]],
    warehouse_labels: list[str],
    store_labels: list[str],
    solver_name: str,
    mapped_status: str,
) -> nextmv.Output:
    """Extract allocations and unmet demand from a solved model and build the output.

    Reads the values of the decision variables ``x[w, s]`` and ``unmet[s]``
    from the model, computes summary metrics (fill rate, transport cost, etc.),
    generates the allocation chart asset, and packages everything into a
    :class:`nextmv.Output`.

    Parameters
    ----------
    model : ConcreteModel
        A Pyomo model whose solutions have already been loaded via
        ``model.solutions.load_from(results)``.
    demand : list[int]
        Units demanded by each store, length *num_stores*.
    supply : list[int]
        Units available at each warehouse, length *num_warehouses*.
    cost : list[list[float]]
        Transport cost matrix of shape ``(num_warehouses, num_stores)``
        where ``cost[w][s]`` is the unit cost from warehouse *w* to store *s*.
    warehouse_labels : list[str]
        Human-readable label for each warehouse.
    store_labels : list[str]
        Human-readable label for each store.
    solver_name : str
        Normalised solver key used for this run (e.g. ``"highs"``).
    mapped_status : str
        Human-readable solver status (e.g. ``"optimal"``, ``"suboptimal"``).

    Returns
    -------
    output : nextmv.Output
        Contains:

        ``solution``
            ``allocations`` : list[dict]
                One entry per lane with positive flow, each with keys
                ``warehouse``, ``warehouse_name``, ``store``,
                ``store_name``, and ``units``.
            ``unmet_demand`` : list[dict]
                One entry per store with unmet demand > 0.01, each with
                keys ``store``, ``store_name``, and ``unmet_demand``.
        ``assets``
            List containing the allocation bar-chart asset.
        ``metrics``
            ``result_value`` : float
                Optimal objective value (transport cost + penalties).
            ``transportation_cost`` : float
                Pure transport cost without penalties.
            ``fill_rate`` : float
                Fraction of total demand that was fulfilled.
            ``total_units_allocated`` : float
                Total units shipped across all lanes.
            ``total_demand`` : int
                Sum of store demands.
            ``total_supply`` : int
                Sum of warehouse supply capacities.
            ``num_unmet_stores`` : int
                Number of stores with unmet demand.
            ``status`` : str
                Solver status string.
            ``solver`` : str
                Solver name used.
    """
    num_warehouses = len(supply)
    num_stores = len(demand)
    W = range(num_warehouses)
    S = range(num_stores)

    allocations = [
        {
            "warehouse": w,
            "warehouse_name": warehouse_labels[w],
            "store": s,
            "store_name": store_labels[s],
            "units": round(value(model.x[w, s]), 2),
        }
        for w in W
        for s in S
        if value(model.x[w, s]) > 0.01
    ]
    unmet = [
        {
            "store": s,
            "store_name": store_labels[s],
            "unmet_demand": round(value(model.unmet[s]), 2),
        }
        for s in S
        if value(model.unmet[s]) > 0.01
    ]

    total_allocated = sum(a["units"] for a in allocations)
    total_demand = sum(demand)
    fill_rate = total_allocated / total_demand if total_demand > 0 else 0
    transport_cost = sum(cost[a["warehouse"]][a["store"]] * a["units"] for a in allocations)

    chart = allocation_chart(
        allocations=allocations,
        num_warehouses=num_warehouses,
        num_stores=num_stores,
        warehouse_labels=warehouse_labels,
        store_labels=store_labels,
    )

    return nextmv.Output(
        solution={"allocations": allocations, "unmet_demand": unmet},
        assets=[chart],
        metrics={
            "result_value": round(value(model.obj), 2),
            "transportation_cost": round(transport_cost, 2),
            "fill_rate": round(fill_rate, 4),
            "total_units_allocated": round(total_allocated, 2),
            "total_demand": total_demand,
            "total_supply": sum(supply),
            "num_unmet_stores": len(unmet),
            "status": mapped_status,
            "solver": solver_name,
        },
    )


if __name__ == "__main__":
    main()
