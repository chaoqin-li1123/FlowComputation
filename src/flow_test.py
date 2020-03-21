import unittest
import flow
import numpy as np


class FlowComputeTestCase(unittest.TestCase):
    def test_pq(self):
        # Test the flow compute function with network that only contains PQ nodes and Slack node.
        n = 0
        pq_i = []
        pv_i = []
        G = None
        B = None
        f = []
        with open("pq.txt", "r") as file:
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
                    G = np.zeros((n + 1, n + 1))
                    for i in range(n + 1):
                        g = file.readline().split()
                        for j in range(n + 1):
                            G[i][j] = float(g[j])
                elif line == "B":
                    B = np.zeros((n + 1, n + 1))
                    for i in range(n + 1):
                        b = file.readline().split()
                        for j in range(n + 1):
                            B[i][j] = float(b[j])
                elif line == "end":
                    break
        x, step = flow.flow_compute(G, B, pq_i, pv_i, n, f)
        result = []
        for i in range(2 * n):
            result.append(float(x[i]))
        # Standard output
        stdx = [1.0018, 0, 0.9994, 0, 1.0027, 0]
        print("pq test:")
        print(result)
        print(stdx)
        cmp = True
        for i in range(2 * n):
            if abs(stdx[i] - result[i]) > 1e-4:
                cmp = False
                break
        self.assertTrue(cmp)

    def test_pq_pv(self):
        # Test the flow compute function with network that contains PQ buses, PV buses and Slack bus.
        n = 0
        pq_i = []
        pv_i = []
        G = None
        B = None
        f = []
        with open("pq_pv.txt", "r") as file:
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
                    G = np.zeros((n + 1, n + 1))
                    for i in range(n + 1):
                        g = file.readline().split()
                        for j in range(n + 1):
                            G[i][j] = float(g[j])
                elif line == "B":
                    B = np.zeros((n + 1, n + 1))
                    for i in range(n + 1):
                        b = file.readline().split()
                        for j in range(n + 1):
                            B[i][j] = float(b[j])
                elif line == "end":
                    break
        x, step = flow.flow_compute(G, B, pq_i, pv_i, n, f)
        result = []
        for i in range(2 * n):
            result.append(float(x[i]))
        # Standard output.
        stdx = [0.9620, -0.0772, 1.0071, -0.0756]
        print("pq_pv test:")
        print(result)
        print(stdx)
        cmp = True
        for i in range(2 * n):
            if abs(stdx[i] - result[i]) > 1e-4:
                cmp = False
                break
        self.assertTrue(cmp)


    def test_not_converge(self):
        # Test the error handling of the flow_compute function.
        n = 0
        pq_i = []
        pv_i = []
        G = None
        B = None
        f = []
        with open("not_converge.txt", "r") as file:
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
                    G = np.zeros((n + 1, n + 1))
                    for i in range(n + 1):
                        g = file.readline().split()
                        for j in range(n + 1):
                            G[i][j] = float(g[j])
                elif line == "B":
                    B = np.zeros((n + 1, n + 1))
                    for i in range(n + 1):
                        b = file.readline().split()
                        for j in range(n + 1):
                            B[i][j] = float(b[j])
                elif line == "end":
                    break
        self.assertRaises(RuntimeError, flow.flow_compute, G, B, pq_i, pv_i, n, f)


if __name__ == '__main__':
    unittest.main()
