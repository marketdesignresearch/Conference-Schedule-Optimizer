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
|||||
| bidder_cost      | Cost for a bidder attending a subsession | 5 | int |
| topic_cost      | Cost for a "topic"-bidder attending a subsession | 25 | int |
| topic_utility      | Constant utility for a "topic"-bidder attending a subsession (constant analogue to U map) | 100 | int |
|||||
| U      | Bidders' utilities map U: U(b,p) represents bidder b’s bid on paper p. | {(1,12): 23.45, (1,14):22.7, (7,4):9.3,...} | dict |
| M      | Paper-author map M: M(a,p)=1 iff author a is and author of paper p and author a has at least 2 papers (otherwise she can’t have a conflict with herself). | {(1,3): 1, (1,6):1, (3,4):1,...} | dict |
| T      | Paper-session map T: T(j,p)=1 iff paper p cannot be presented in session j | {(5,1): 1, (14,1):1, (7,2):1,...} | dict |
| Q      | Paper-topic map Q: Q(p,t)==1 iff paper p has topic t. | {(1,2): 1, (1,7):1, (26,4):1,...} | dict |
|||||
| paper_title_dict      | Mapping between paperID and title of the paper | {1: 'Paper Title 1', 2: 'Paper Title 2', 3: 'Paper Title3',...} | dict |
| paper_author_dict      | Mapping between paperID and all authors of the corresponding paper | {1: ['Author1','Author2'], 2: ['Author5'], 3:['Author2', 'Author4', 'Author8'] ,...} | dict(list) |
| paper_topic_dict      | Mapping between paperID and all topics of the corresponding paper | {1: ['Topic1','Topic2'], 2: ['Topic5'], 3: ['Topic2', 'Topic4', 'Topic8'] ,...} | dict(list) |

### 3.2 Binary Decision Variables

### 3.2.1 Paper Variables
$x_{p,j,k} \in \\\{0,1\\\}\quad \forall (p,j,k) \in paper\\\_ids \times track\\\_ids \times session\\\_ids$. 

The decision variable $x_{p,j,k}$ is used to model if a paper is allocated to a specific subsession (i.e. a session-track combination). Specifically, paper $p$ is allocated to session $j$ and track $k$ iff $x_{p,j,k}=1$. Note, that the final schedule is given by {$x_{p,j,k}: x_{p,j,k}=1$}.

### 3.2.2 Bidder Variables
**$y_{b,j,k} \in \\\{0,1\\\}\quad \forall (b,j,k) \in bidder\\\_ids \times track\\\_ids \times session\\\_ids$.**

The decision variable $y_{b,j,k}$ is used to model if a bidder attends a specific subsession (i.e. a session-track combination). Specifically, author $b$ attends session $j$ in track $k$ iff $y_{b,j,k}=1$. This decision variable is used  as an indication of audience interest, e.g., two papers with a high interest should not be presented simulatenously.

### 3.2.3 Author Variables
**$z_{a,j,k} \in \\\{0,1\\\}\quad \forall  (a,j,k) \in author\\\_ids \times track\\\_ids \times session\\\_ids$.**

The decision variable $z_{a,j,k}$ is used to model if a author presents her paper in a specific subsession (i.e. a session-track combination). Specifically, author $a$ presents her paper in session $j$ and track $k$ iff $z_{a,j,k}=1$. This decision variable is used to handle author-specific constraints, e.g., an author of 2 papers cannot present simulatenously both papers.

### 3.2.4 Topic Variables
**$q_{a,j,k} \in  \\\{0,1\\\}\quad \forall (t,j,k) \in topic\\\_ids \times track\\\_ids \times session\\\_ids$.**

The decision variable $q_{t,j,k}$ is used to model if a topic is present in a specific subsession (i.e. a session-track combination). Specifically, topci $t$ is present in session $j$ and track $k$ iff $q_{t,j,k}=1$. This decision variable is used to cluster papers with similar topics.

### 3.2 QIP Formulation

#### 3.2.1 Objective

$$ \large \max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k},\\\,\\\, q_{t,j,k}} \quad \sum_{(b,p) : U(b,p)>0}\quad \sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} x_{p,j,k} \cdot y_{b,j,k} \cdot U(b,p) \\\,- \quad (obj1)$$ 

$$ \large \hphantom{\max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k},\\\,\\\, q_{t,j,k}}} \sum_{b \in bidder\\\_ids}\quad\sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} y_{b,j,k} \cdot bidder\\\_cost \\\,+ \quad (obj2)$$ 

$$ \large \hphantom{aaaaaa\max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k},\\\,\\\, q_{t,j,k}}} \sum_{(t,p):Q(t,p)=1}\quad\sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} x_{p,j,k} \cdot q_{t,j,k} \cdot topic\\\_utility \\\,- \quad (obj3)$$ 

$$ \large \hphantom{\max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k}}} \sum_{t \in topic\\\_ids}\quad\sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} q_{t,j,k} \cdot topic\\\_cost. \quad (obj4)$$ 

*Explanation:*

*(obj1): sum up bidders' utility*

*(obj2): substract bidders' costs for attending a session using a constant bidder-cost $bidder\\\_cost$*

*(obj3): sum up topics' utilities for using a constant topic utilitiy $topic\\\_utility$*

*(obj4): substract topics' costs for beeing present in a session using a constant topic-cost $topic\\\_cost$*

s.t.

#### 3.2.2 Constraints

##### Paper variables
1. For all $p \in paper\\\_ids: \\\, \sum_{j \in session\\\_ids} \sum_{k \in track\\\_ids} x_{p,j,k} = 1\quad$ (*Each paper appears exactly once*)
2. For all $j \in session\\\_ids$, for all $k \in track\\\_ids: \\\, \sum_{p \in paper\\\_ids}  x_{p,j,k} <= track\\\_session\\\_capacity\quad$ (*Each Track has track_session_capacity papers*)
3. For all $\\\{(j,p): T(j,p)==1\\\}$ and for all $k \in track\\\_ids: \\\, x_{p,j,k} = 0$ (*Time conflicts*)

##### Bidder variables
4. For all $j \in session\\\_ids$, for all $b \in bidder\\\_ids: \\\, \sum_{k \in track\\\_ids}  y_{b,j,k} <= 1\quad$ (*A bidder cannot be in more than one track per session*)

##### Author variables
5. For all $\\\{(a,p): M(a,p)==1\\\}$,  for all  $j \in session\\\_ids$ and for all $k \in track\\\_ids: \\\, z_{a,j,k} >= x_{p,j,k}\quad$ (*An author needs to attend if her paper is allocated*)
6. For all $j \in session\\\_ids$, for all $a \in author\\\_ids: \\\, \sum_{k \in track\\\_ids}  z_{a,j,k} <= 1\quad$ (*An author cannot be in more than one track per session*)


##### Topic variables
7. For all $j \in session\\\_ids$, for all $t \in topic\\\_ids: \\\, \sum_{k \in track\\\_ids}  q_{t,j,k} <= 1\quad$ (*A "topic"-bidder cannot be in more than one track per session*)



## 4. How to Run
TODO




## Contact
Maintained by: Jakob Weissteiner (weissteiner)

Website: www.jakobweissteiner.com

E-mail: weissteiner@ifi.uzh.ch
