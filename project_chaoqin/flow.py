import numpy as np
import shmarray as shm
from multiprocessing import Process
from multiprocessing.pool import Pool
def flow_compute(G, B, pq_i, pv_i, n, f, parallel = False):
    """
    :param G:
    :param B:
    :param pq_i: Index of PQ nodes
    :param pv_i: Index of PV nodes
    :param n: Total number of nodes
    :param f:
    :return:
    """
    x = np.zeros((2 * n + 2, 1))
    df = np.ones((2 * n, 1))
    for i in range(n + 1):
        # transverse component of voltage, usually initialized to be 1, x[2 * i] = e[i]
        x[2 * i] = 1

        # vertical component of voltage, usually initialized to be 0, x[2 * i + 1] = f[i]
        x[2 * i + 1] = 0
    # initialize jacob matrix
    jacob = shm.zeros((2 * n, 2 * n))
    step = 0
    while not converge(df):
        if parallel == False:
            update_jacob(G, B, x, pq_i, pv_i, jacob, n)
        else:
            update_jacob_parallel(G, B, x, pq_i, pv_i, jacob, n)
        update_f(G, B, f, df, x, pq_i, pv_i, n)
        update_x(x, jacob, df, n)
        step += 1
        if step > 100:
            raise RuntimeError("Computation fails to converge.")
    return x, step


def update_f(G, B, f, df, x, pq_i, pv_i, n):
    for i in pq_i:
        df[2 * i] = 0
        df[2 * i + 1] = 0
        for j in range(n + 1):
            df[2 * i] += x[2 * i] * (G[i][j] * x[2 * j] - B[i][j] * x[2 * j + 1]) + x[2 * i + 1] * (G[i][j] * x[2 * j + 1] + B[i][j] * x[2 * j])
            df[2 * i + 1] += x[2 * i + 1] * (G[i][j] * x[2 * j] - B[i][j] * x[2 * j + 1]) - x[2 * i] * (G[i][j] * x[2 * j + 1] + B[i][j] * x[2 * j])
    for i in pv_i:
        df[2 * i] = 0
        df[2 * i + 1] = x[2 * i] ** 2 + x[2 * i + 1] ** 2
        for j in range(n + 1):
            df[2 * i] += x[2 * i] * (G[i][j] * x[2 * j] - B[i][j] * x[2 * j + 1]) + x[2 * i + 1] * (G[i][j] * x[2 * j + 1] - B[i][j] * x[2 * j])
    for i in range(n):
        df[2 * i] = f[2 * i] - df[2 * i]
        df[2 * i + 1] = f[2 * i + 1] - df[2 * i + 1]


def update_x(x, jacob, df, n):
    dx = solve_eq(jacob, df)
    for i in range(2 * n):
        x[i] -= dx[i]


def update_jacob_parallel(G, B, x, pq_i, pv_i, jacob, n):
    processes = []
    for i in pq_i:
        p = Process(target = update_jacob, args=(G, B, x, [i], [], jacob, n))
        p.start()
        processes.append(p)
    for i in pv_i:
        p = Process(target = update_jacob, args=(G, B, x, [], [i], jacob, n))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


def update_jacob(G, B, x, pq_i, pv_i, jacob, n):
    """
    update jacob matrix, can be parallelized without race conditions.
    :param G:
    :param B:
    :param e: transverse component of the voltage
    :param j: vertical component of voltage
    :param pq_i: index of PQ nodes
    :param pv_i: index of PV nodes
    :return:
    """
    for i in pq_i:
        temp1, temp2 = 0, 0
        for k in range(n + 1):
            temp1 += (G[i][k] * x[2 * k] - B[i][k] * x[2 * k + 1])
            temp2 += (G[i][k] * x[2 * k + 1] + B[i][k] * x[2 * k])
        for j in range(n):
            if i != j:
                # dp/de
                jacob[2 * i][2 * j] = - G[i][j] * x[2 * i] - B[i][j] * x[2 * i + 1]
                # dp/df
                jacob[2 * i][2 * j + 1] = B[i][j] * x[2 * i] - G[i][j] * x[2 * i + 1]
                # dq/de
                jacob[2 * i + 1][2 * j] = jacob[2 * i][2 * j + 1]
                # dq/df
                jacob[2 * i + 1][2 * j + 1] = -jacob[2 * i][2 * j]
            if i == j:
                # dp/de
                jacob[2 * i][2 * j] = - G[i][j] * x[2 * i] - B[i][j] * x[2 * i + 1]
                # dp/df
                jacob[2 * i][2 * j + 1] = B[i][j] * x[2 * i] - G[i][j] * x[2 * i + 1]
                # dq/de
                jacob[2 * i + 1][2 * j] = jacob[2 * i][2 * j + 1] + temp2
                # dq/df
                jacob[2 * i + 1][2 * j + 1] = -jacob[2 * i][2 * j] - temp1
                jacob[2 * i][2 * j] -= temp1
                jacob[2 * i][2 * j + 1] -= temp2
    # update jacob matrix for all PV nodes
    for i in pv_i:
        for j in range(n):
            if i != j:
                # dp/de
                jacob[2 * i][2 * j] = - G[i][j] * x[2 * i] - B[i][j] * x[2 * i + 1]
                # dp/df
                jacob[2 * i][2 * j + 1] = B[i][j] * x[2 * i] - G[i][j] * x[2 * i + 1]
                # dV^2/de
                jacob[2 * i + 1][2 * j] = 0
                # dV^2/df
                jacob[2 * i + 1][2 * j + 1] = 0
            if i == j:
                temp1, temp2 = 0, 0
                for k in range(n + 1):
                    temp1 += (G[i][k] * x[2 * k] - B[i][k] * x[2 * k + 1])
                    temp2 += (G[i][k] * x[2 * k + 1] + B[i][k] * x[2 * k])
                # dp/de
                jacob[2 * i][2 * j] = - G[i][j] * x[2 * j] - B[i][j] * x[2 * i + 1] - temp1
                # dp/df
                jacob[2 * i][2 * j + 1] = B[i][j] * x[2 * i] - G[i][j] * x[2 * i + 1] - temp2
                # dV^2/de
                jacob[2 * i + 1][2 * j] = -2 * x[2 * i]
                # dV^2/df
                jacob[2 * i + 1][2 * j + 1] = -2 * x[2 * i + 1]


def solve_eq(jacob, df):
    # solve equation df = -J*dx
    return np.linalg.lstsq(jacob, df, rcond=None)[0]


def converge(df):
    precision = 1e-7
    for x in df:
        if x > precision or x < -precision:
            return False
    return True




