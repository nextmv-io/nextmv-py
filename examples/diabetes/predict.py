#!/usr/bin/env python3

import time

from sklearn import datasets

import nextmv


def main():
    start_time = time.time()

    m = nextmv.from_dict(nextmv.load_local().data["solution"]).to_model()
    X = datasets.load_diabetes().data

    output = nextmv.Output(
        solution=m.predict(X).tolist(),
        statistics=nextmv.Statistics(
            run=nextmv.RunStatistics(duration=time.time() - start_time),
        ),
    )

    nextmv.write_local(output)


if __name__ == "__main__":
    main()
