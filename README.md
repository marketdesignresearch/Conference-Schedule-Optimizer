# Conference-Schedule-Optimizer
This software uses a Quadratic Integer Programming (QIP) formulation to produce an optimal conference schedule given reviewers' bidding preferences. The QIP formulation was derived by Jakob Weissteiner (University of Zurich), Sven Seuken (Univeristy of Zurich), and Ilya Segal (Stanford University). This software was used to create the official Conference schedule (150 papers) for the 23rd ACM Conference on Economics and Computation (EC'22).

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

| Parameter        | Explanation | Example  | Type |
| ------------- |-------------| -----| -----|
| session_ids      | Session indices | [1,2] | list |
| track_ids      | Track indices | [1,2,3,4] | list |
| track_session_capacity      | Capacity per subsession, i.e. track-session tuple | 4 | int |
| author_ids      | Author indices | [1,...,20] | list |
| paper_ids      | Paper indices | [1,...,32] | list |
| bidder_ids      | Bidder indices | [1,...,20] | list |
| topic_ids      | Topic indices | [1,...,10] | list |
|############|############|############|############|
| bidder_cost      | Cost for a bidder attending a subsession | 5 | int |
| topic_cost      | Cost for a "topic" attending a subsession | 25 | int |
|############|############|############|############|
| U      | Bidders' utilities map U:** U(b,p) represents bidder b’s bid on paper p. | {(1,12): 23.45, (1,14):22.7, (7,4):9.3,...} | dict |
| M      | Paper-author map M:** M(a,p)=1 iff author a is and author of paper p and author a has at least 2 papers (otherwise she can’t have a conflict with herself). | {(1,3): 1, (1,6):1, (3,4):1,...} | dict |
| T      | Paper-session map T:** T(j,p)=1 iff paper p cannot be presented in session j | {(5,1): 1, (14,1):1, (7,2):1,...} | dict |
| Q      | Paper-topic map Q:** Q(p,t)==1 iff paper p has topic t. | {(1,2): 1, (1,7):1, (26,4):1,...} | dict |
|############|############|############|############|
| paper_title_dict      | Mapping between paperID and title of the paper | {1: 'Paper Title 1', 2: 'Paper Title 2', 3: 'Paper Title3',...} | dict |
| paper_author_dict      | Mapping between paperID and all authors of the corresponding paper | {1: ['Author1','Author2'], 2: ['Author5'], 3:['Author2', 'Author4', 'Author8'] ,...} | dict(list) |
| paper_topic_dict      | Mapping between paperID and all topics of the corresponding paper | {1: ['Topic1','Topic2'], 2: ['Topic5'], 3: ['Topic2', 'Topic4', 'Topic8'] ,...} | dict(list) |

### 3.2 Binary Decision Variables

### 3.2.1 Paper Variables
$x_{p,j,k} \in \\\{0,1\\\}\quad \forall (p,j,k) \in$ paper_ids $\times$ track_ids $\times$ session_ids.

The decision variable $x_{p,j,k}$ is used to model if a paper is allocated to a specific subsession (i.e. a session-track combination). Specifically, paper $p$ is allocated to session $j$ and track $k$ iff $x_{p,j,k}=1$. Note, that the final schedule is given by ${x_{p,j,k}: x_{p,j,k}=1 \forall p,j,k}$.

### 3.2.2 Bidder Variables
**$y_{b,j,k} \in \\\{0,1\\\}\quad \forall (b,j,k) \in$ bidder_ids $\times$ track_ids $\times$ session_ids.**

The decision variable $y_{b,j,k}$ is used to model if a bidder attends a specific subsession (i.e. a session-track combination). Specifically, author $b$ attends session $j$ in track $k$ iff $y_{b,j,k}=1$. This decision variable is used  as an indication of audience interest, e.g., two papers with a high interest should not be presented simulatenously.

### 3.2.3 Author Variables
**$z_{a,j,k} \in \\\{0,1\\\}\quad \forall  (a,j,k) \in$ author_ids $\times$ track_ids $\times$ session_ids.**

The decision variable $z_{a,j,k}$ is used to model if a author presents her paper in a specific subsession (i.e. a session-track combination). Specifically, author $a$ presents her paper in session $j$ and track $k$ iff $z_{a,j,k}=1$. This decision variable is used to handle author-specific constraints, e.g., an author of 2 papers cannot present simulatenously both papers.

### 3.2.4 Topic Variables
**$q_{a,j,k} \in  \\\{0,1\\\}\quad \forall (t,j,k) \in$ topic_ids $\times$ track_ids $\times$ session_ids.**

The decision variable $q_{t,j,k}$ is used to model if a topic is present in a specific subsession (i.e. a session-track combination). Specifically, topci $t$ is present in session $j$ and track $k$ iff $q_{t,j,k}=1$. This decision variable is used to cluster papers with similar topics.





## Contact
Maintained by: Jakob Weissteiner (weissteiner)

Website: www.jakobweissteiner.com

E-mail: weissteiner@ifi.uzh.ch
