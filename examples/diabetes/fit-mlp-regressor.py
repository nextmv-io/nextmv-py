#!/usr/bin/env python3

import time

from sklearn import datasets

import nextmv
from nextmv.sklearn import neural_network as nnn


def main():
    start_time = time.time()

    opt = nnn.MLPRegressorOptions()
    data = datasets.load_diabetes()
    X = data.data
    y = data.target

    m = opt.to_model()
    m.fit(X, y)

    solution = nnn.MLPRegressorSolution.from_model(m)
    output = nextmv.Output(
        options=opt,
        solution=nextmv.to_dict(solution),
        statistics=nextmv.Statistics(
            run=nextmv.RunStatistics(duration=time.time() - start_time),
            result=nnn.MLPRegressorResultStatistics.from_model(m, X, y),
        ),
    )

    nextmv.write_local(output)


if __name__ == "__main__":
    main()
