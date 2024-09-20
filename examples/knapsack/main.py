#!/usr/bin/env python3

import time

import gurobipy as gp
from gurobipy import GRB

import nextmv
from nextmv import gurobipy as ngp


def main():
    start_time = time.time()

    opt = ngp.GurobipyOptions()
    env = opt.to_env(params="gurobi.lic")

    data = nextmv.load_local(options=opt).data
    capacity = data["capacity"]
    items = data["items"]

    m = gp.Model(env=env)
    x = m.addVars(len(items), name=[i["id"] for i in items], vtype=GRB.BINARY)
    m.addConstr(x.prod([i["weight"] for i in items]) <= capacity)
    m.setObjective(x.prod([i["value"] for i in items]), sense=GRB.MAXIMIZE)
    m.optimize()

    custom = {"capacity": capacity, "items": len(items)}
    output = nextmv.Output(
        options=opt,
        solution=ngp.GurobipySolution.from_model(m),
        statistics=nextmv.Statistics(
            run=nextmv.RunStatistics(duration=time.time() - start_time),
            result=ngp.GurobipyResultStatistics.from_model(m, custom=custom),
        ),
    )

    nextmv.write_local(output)


if __name__ == "__main__":
    main()
