# -*- coding: future_fstrings -*-
import numpy
import flow
import network_visualization as nv
import time

def param(path, parallelism = False):
    """
    read parameters of power network from path and do flow computation by calling flow.py
    """
    n = 0
    pq_i = []
    pv_i = []
    G = None
    B = None
    f = []
    position = []
    with open(path, "r") as file:
        while True:
            line = file.readline().strip()
            if line == "n":
                n = int(file.readline())
            elif line == "pq_bus":
                pq_i = [int(x) for x in file.readline().split()]
            elif line == "pv_bus":
                pv_i = [int(x) for x in file.readline().split()]
            elif line == "f":
                f = [float(x) for x in file.readline().split()]
            elif line == "G":
                G = numpy.zeros((n + 1, n + 1))
                for i in range(n + 1):
                    g = file.readline().split()
                    for j in range(n + 1):
                        G[i][j] = float(g[j])
            elif line == "B":
                B = numpy.zeros((n + 1, n + 1))
                for i in range(n + 1):
                    b = file.readline().split()
                    for j in range(n + 1):
                        B[i][j] = float(b[j])
            elif line == "position":
                position = [float(x) for x in file.readline().split()]
            elif line == "end":
                break
            else:
                raise ValueError("Invalid input!")
    start_time = time.time()
    x, step = flow.flow_compute(G, B, pq_i, pv_i, n, f, parallelism)
    end_time = time.time()
    network = nv.Network(G, B, n, pq_i, pv_i, f, x, position)
    file = open("flow.report", "a")
    file.write(f"Total iterations count: {step}\n")
    file.write(f"Time elapsed: {1000 * (end_time - start_time)} ms\n")
    file.write("src: " + path)
    file.close()




