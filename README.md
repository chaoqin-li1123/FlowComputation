# MPCS 51046 (Autumn 2019) Course Project, Chaoqin Li

## Background Knowledge

Flow computation is a method to analyze power system in steady state. It models eletricity generators and consumers(the so called buses) as vertex, power transmission lines as edges, solve equations to determined the state of the power network. There are many ways to solve the equations, among them Newton-Raphson is the most popular. Detaied explaination can be found [Flow Computation](https://en.wikipedia.org/wiki/Power-flow_study)

## Design

flow.py focus on the power flow computation based on Newton-Raphson Method. The input is some parameters of the power network, output is the state of the power network. The procedure is divied into 2 steps: updating jacobian matrix, updating the voltage magnitude and angles. Updating the J matrix doesn't require any information from J matrx in the last iteration, so it can be parallelized without race conditions. Use shmarray module to share the Jacobian Matrix across process and use multiprocess module to update the matrix in parallel.

network\_visualiztion.py is an object-oriented visualization program. It input the state of vertex(buses) and edges(transmission lines) of the network and draw the graph "power_network.png". A report named "flow.report" will also be generated. There are 3 class in the program. 

- Bus with bus type, voltage, power and position(for visualization) as attribute.
- Line with transmitted power, power loss, start and end point as attributes.
- Network with a list of buses and a list of lines as attributes, call "visualize" to generate graph of power network, call "report_generate" to generate report.

interface.py is an object-oriented program that has a window, 2 buttons(import file and close", a check box(parallelism), a canvas to display power network and a text box to display report or error logs.

get\_param.py parse the input file and send parameters to flow\_compute function. Then use the return value from flow\_compute to initialize a network object, which, in turn, do the visualiztion and report generation.

flow\_test.py contain 3 unit test to test accuracy and error handling of the flow_compute function of flow.py.

## User Guide

Run interface.py with "python3 interface.py" command. / or download interface repository and run application executable with "./interface" command.

Click "source file" button, select a file(pq.txt, pq_pv.txt, not\_converge.txt or any text file).

Image(power_network.jpg) and report(flow.report) are also saved in the same directory as the scropt.

Check box "parallelism?" decide whether to use multiprocess to do the computation. 

If you want to switch file, just click the "source file" button again and the image and text will be refreshed.

After you click the "close" button, the window is shut down and process will be terminated.

The process doesn't terminate after clicking the default escape button, so please use "close" button instead.

## Required Packages

- numpy
- matplotlib
- tkinter
- shmarray
- multiprocessing

