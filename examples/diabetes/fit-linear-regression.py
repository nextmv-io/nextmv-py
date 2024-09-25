#!/usr/bin/env python3

import time

from sklearn import datasets

import nextmv
from nextmv.sklearn import linear_model as nlm


def main():
    start_time = time.time()

    opt = nlm.LinearRegressionOptions()
    data = datasets.load_diabetes()
    X = data.data
    y = data.target

    m = opt.to_model()
    m.fit(X, y)

    solution = nlm.LinearRegressionSolution.from_model(m)
    output = nextmv.Output(
        options=opt,
        solution=nextmv.to_dict(solution),
        statistics=nextmv.Statistics(
            run=nextmv.RunStatistics(duration=time.time() - start_time),
            result=nlm.LinearRegressionResultStatistics.from_model(m, X, y),
        ),
    )

    nextmv.write_local(output)


if __name__ == "__main__":
    main()
