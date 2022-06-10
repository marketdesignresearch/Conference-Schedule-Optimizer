# ConferenceScheduleOptimizer
This software uses a Quadratic Integer Programming (QIP) formulation to produce an optimal conference schedule given reviewers' bidding preferences.

## 1. Requirements

* Python 3.8
* CPLEX 20.01.0 

## 2. Installation Guide

First prepare your python environment *myenv* (`conda`, `virtualenv`, etc.).

Next install CPLEX 20.01.0. Once CPLEX is installed, install the CPLEX Python API. For this first activate your environment *myenv* 
		
```bash
$ source ~/myenv/bin/activate
```
		
and then navigate to the file setup.py located in ...\IBM\ILOG\CPLEX_Studio201\python and run

```bash
$ python3 setup.py install
```

## 1. Quadratic Integer Program (QIP)
In the following, we describe the QIP.

### 1.1 Input


