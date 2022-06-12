# Conference-Schedule-Optimizer
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

## 3. Quadratic Integer Program (QIP)
In the following, we describe the QIP.

### 3.1 Input

- **Session indices session_ids:**
- **Track indices track_ids:**

- **Author indices author_ids:**
- **Paper indices paper_ids:**
- **Bidder indices bidder_ids:**
- **Topic indices topic_ids:**

- **Bidders' utilities map U:** U(b,p) represents bidder b’s bid on paper p.
- **Paper-author map M:** M(a,p)=1 iff author a is and author of paper p and author a has at least 2 papers (otherwise she can’t have a conflict with herself).
- **Paper-session Matrix T:** T(j,p)=1 iff paper p cannot be presented in session j.
- **Paper-topic Matrix Q:** Q(p,t)==1 iff paper p has topic t.



