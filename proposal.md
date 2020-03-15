# Intermediate Python Project Proposal — Power System Analysis Tool
## Plan
Develop a tool that can be used to analyze power system. It should be able to predict energy consumption based on history data. Given the parameter of power network, it should be able to generate report of the steady state of power network, including voltage and transmission loss. Some of the output should be visualized automatically.

## Modules
-Load prediction: given electricity consumption as a time series, use ARIMA or machine learning methods to predict the future electricity consumption. This module should be able to predict energy consumption as well as other time series. The input should be csv file.
-Power Flow Computation: given the parameter(resistance, inductance) of power network and power of energy source, output the voltage of different nodes and energy loss due to transmission. Generate report of computation. Only do AC power flow computation in steady state. The input should be weighted graph represented by adjacency matrix.
-Visualization: Visualize the power network using graph models and plot the distribution of energy consumption.

## Frameworks
Use Numpy and Pandas for matrix computation.
Use Matplotlib for data visualization.

## Milestones
-Complete the module of load prediction before Nov 13.
-Implement power flow computation before Nov 24.
-Implement visualization and user interface before Dec 8.
-Complete testing before Dec 14.
