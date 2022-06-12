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

| Parameter        | Explanation | Example  |
| ------------- |:-------------:| -----:|
| session_ids      | Session indices | [1,2] |
| track_ids      | Track indices | [1,2,3,4] |
| track_session_capacity      | Capacity per subsession, i.e. track-session tuple | 4 |
| author_ids      | Author indices | [1,...,20] |
| paper_ids      | Paper indices | [1,...,32] |
| bidder_ids      | Bidder indices | [1,...,20] |
| topic_ids      | Topic indices | [1,...,10] |
| bidder_cost      | Cost for a bidder attending a subsession | 5 |
| topic_cost      | Cost for a "topic" attending a subsession | 25 |
| U      | Bidders' utilities map U:** U(b,p) represents bidder b’s bid on paper p. | {(1,12): 23.45, (1,14):22.7, (7,4):9.3,...} |
| M      | Paper-author map M:** M(a,p)=1 iff author a is and author of paper p and author a has at least 2 papers (otherwise she can’t have a conflict with herself). | {(1,3): 1, (1,6):1, (3,4):1,...} |
| T      | Paper-session Matrix T:** T(j,p)=1 iff paper p cannot be presented in session j | {(5,1): 1, (14,1):1, (7,2):1,...} |
| Q      | Paper-topic Matrix Q:** Q(p,t)==1 iff paper p has topic t. | {(1,2): 1, (1,7):1, (26,4):1,...} |

