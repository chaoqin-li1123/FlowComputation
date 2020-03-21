# -*- coding: future_fstrings -*-
import numpy as np
import time
import matplotlib.pyplot as plt

PQ, PV, SLACK = 0, 1, 2


class Line:
    def __init__(self, n1, n2, p1, q1, p2, q2, x1, y1, x2, y2):
        # Power is always transmitted from bus 1 to bus 2.
        if p1 < 0:
            p1, p2 = p2, p1
            q1, q2 = q2, q1
            n1, n2 = n2, n1
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        self._n1 = n1
        self._n2 = n2
        self._p1 = p1
        self._q1 = q1
        self._p2 = p2
        self._q2 = q2
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    @property
    def power_loss(self):
        return self._p1 + self._p2

    def __str__(self):
	# To be displayed in the report.
        return f"(bus {self._n1} -> bus {self._n2}) p:{self._p1:.4f}, q:{self._q1:.4f}, power loss:{self.power_loss:.4f}({100 * self.power_loss / self._p1:.2f}%) "

    def label(self):
	# To be displayed in the graph.
        return f"P:{int(self._p1 * 1000)}MW\nloss: {100 * self.power_loss / self._p1:.2f}% "


class Node:
    def __init__(self, index, bus_type, e, f, p, q, x, y):
        self.index = index
        self.bus_type = bus_type
        self.e = float(e)
        self.f = float(f)
        self.p = float(p)
        self.q = float(q)
        self.x = x
        self.y = y

    def __str__(self):
	# To be displayed in the report.
        if self.bus_type == PQ:
            return f"(PQ bus {self.index}) P:{self.p:.4f}, Q:{self.q:.4f}, V:{self.e:.4f}+j({self.f:.4f})"
        elif self.bus_type == PV:
            return f"(PV bus {self.index}) P:{self.p:.4f}, Q:{self.q:.4f}, V:{self.e:.4f}+j({self.f:.4f})"
        else:
            return f"(Slack bus {self.index}) P:{self.p:.4f}, Q:{self.q:.4f}, V:{self.e:.4f}+j({self.f:.4f})"

    def label(self):
	# To be displayed in the graph.
        if self.bus_type == PQ:
            return f"(PQ bus {self.index})\n P:{int(self.p * 1000)}MW\n Q:{int(self.q * 1000)}MW"
        elif self.bus_type == PV:
            return f"(PV bus {self.index})\n P:{int(self.p * 1000)}MW\n Q:{int(self.q * 1000)}MW"
        else:
            return f"(Slack bus {self.index})\n P:{int(self.p * 1000)}MW\n Q:{int(self.q * 1000)}MW"


class Network:
    def __init__(self, G, B, n, pq_i, pv_i, f, x, position=None):
        self._nodes = []
        self._lines = []
        p_line = np.zeros((n + 1, n + 1))
        q_line = np.zeros((n + 1, n + 1))
        # scale the position to make them fit the graph.
        Network.scale(position, n)
        for i in range(n + 1):
            v2 = x[2 * i] ** 2 + x[2 * i + 1] ** 2
            if v2 < 0.81 or v2 > 1.21:
                raise ValueError("Voltage out of bound!")
        for j in range(n + 1):
            for i in range(j + 1):
                if G[i][j] == 0 and B[i][j] == 0 or i == j:
                    continue
                p_line[i][j] = x[2 * i] * (G[i][j] * (x[2 * j] - x[2 * i]) - B[i][j] * (x[2 * j + 1] - x[2 * i + 1])) \
                               + x[2 * i + 1] * (
                                           G[i][j] * (x[2 * j + 1] - x[2 * i + 1]) + B[i][j] * (x[2 * j] - x[2 * i]))
                q_line[i][j] = x[2 * i + 1] * (
                            G[i][j] * (x[2 * j] - x[2 * i]) - B[i][j] * (x[2 * j + 1] - x[2 * i + 1])) \
                               - x[2 * i] * (G[i][j] * (x[2 * j + 1] - x[2 * i + 1]) + B[i][j] * (x[2 * j] - x[2 * i]))
                p_line[j][i] = x[2 * j] * (G[j][i] * (x[2 * i] - x[2 * j]) - B[j][i] * (x[2 * i + 1] - x[2 * j + 1])) \
                               + x[2 * j + 1] * (
                                           G[j][i] * (x[2 * i + 1] - x[2 * j + 1]) + B[j][i] * (x[2 * i] - x[2 * j]))
                q_line[j][i] = x[2 * j + 1] * (
                            G[j][i] * (x[2 * i] - x[2 * j]) - B[j][i] * (x[2 * i + 1] - x[2 * j + 1])) - \
                               x[2 * j] * (G[j][i] * (x[2 * i + 1] - x[2 * j + 1]) + B[j][i] * (x[2 * i] - x[2 * j]))
                self._lines.append(Line(i, j, p_line[i][j], q_line[i][j], p_line[j][i], q_line[j][i], position[2 * i],
                                        position[2 * i + 1], position[2 * j], position[2 * j + 1]))
        for i in pq_i:
            self._nodes.append(
                Node(i, PQ, x[2 * i], x[2 * i + 1], f[2 * i], f[2 * i + 1], position[2 * i], position[2 * i + 1]))
        for i in pv_i:
            q = 0
            for k in range(n + 1):
                q += x[2 * i + 1] * (G[i][k] * x[2 * k] - B[i][j] * x[2 * k + 1]) - x[2 * i] * (
                            G[i][k] * x[2 * k + 1] + B[i][k] * x[2 * k])
            self._nodes.append(Node(i, PV, x[2 * i], x[2 * i + 1], f[2 * i], q, position[2 * i], position[2 * i + 1]))
        p = 0
        q = 0
        i = n
        for j in range(n + 1):
            p += x[2 * i] * (G[i][j] * x[2 * j] - B[i][j] * x[2 * j + 1]) + x[2 * i + 1] * (
                        G[i][j] * x[2 * j + 1] + B[i][j] * x[2 * j])
            q += x[2 * i + 1] * (G[i][j] * x[2 * j] - B[i][j] * x[2 * j + 1]) - x[2 * i] * (
                        G[i][j] * x[2 * j + 1] + B[i][j] * x[2 * j])
        self._nodes.append(Node(n, SLACK, x[2 * i], x[2 * i + 1], p, q, position[2 * i], position[2 * i + 1]))
        self.report_generate()
        self.visualize()

    def visualize(self):
        plt.axis([-0.25, 1.5, -0.25, 1.1])
        for node in self._nodes:
            Network.draw_node(node)
        for line in self._lines:
            Network.draw_line(line)
        plt.axis('off')
        plt.savefig("power_network.png")
        plt.clf()


    def report_generate(self):
        f = open("flow.report", "w+")
        for node in self._nodes:
            f.write(str(node) + "\n")
        for line in self._lines:
            f.write(str(line) + "\n")
        f.close()

    @staticmethod
    def scale(position, n):
        max_x = position[2 * n]
        min_x = position[2 * n]
        max_y = position[2 * n + 1]
        min_y = position[2 * n + 1]
        for i in range(n):
            x = position[2 * i]
            y = position[2 * i + 1]
            if x > max_x:
                max_x = x
            if x < min_x:
                min_x = x
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y
        for i in range(n + 1):
            position[2 * i] = (position[2 * i] - min_x) / (max_x - min_x)
            position[2 * i + 1] = (position[2 * i + 1] - min_y) / (max_y - min_y)

    @staticmethod
    def draw_node(node):
        if node.bus_type == SLACK:
            plt.plot(node.x, node.y, "r*", markersize=18)
        if node.bus_type == PQ:
            plt.plot(node.x, node.y, "bo", markersize=18)
        if node.bus_type == PV:
            plt.plot(node.x, node.y, "bh", markersize=18)
        plt.text(node.x + 0.01, node.y + 0.01, node.label(), fontsize=12)

    @staticmethod
    def draw_line(line):
        x1, x2 = line.x1, line.x2
        y1, y2 = line.y1, line.y2
        dx = x2 - x1
        dy = y2 - y1
        rotn = np.degrees(np.arctan2(dy, dx)) % 180
        plt.plot([x1 + 0.01 * dx, x2 - 0.01 * dx], [y1 + 0.01 * dy, y2 - 0.01 * dy], "b")
        plt.text(x1 + 0.5 * dx, y1 + 0.5 * dy, line.label(), rotation=rotn, rotation_mode='anchor', fontsize=12)
        plt.arrow(x1 + 0.5 * dx, y1 + 0.5 * dy, 0.2 * dx, 0.2 * dy, head_width=0.05, head_length=0.02)
