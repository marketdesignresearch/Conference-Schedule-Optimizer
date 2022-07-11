# Conference-Schedule-Optimizer
This software uses a Quadratic Integer Programming (QIP) formulation to produce an optimal conference schedule given reviewers' bidding preferences. The QIP formulation was derived by Jakob Weissteiner (University of Zurich), Sven Seuken (Univeristy of Zurich), and Ilya Segal (Stanford University). This software was used to create the official Conference schedule (150 papers) for the 23rd ACM Conference on Economics and Computation (EC'22).

## 1. Requirements

* Python 3.8
* CPLEX 20.01.0 

## 2. Installation Guide

First prepare your python environment *myenv* (`conda`, `virtualenv`, etc.).

Next install CPLEX 20.01.0. Once CPLEX is installed, install the CPLEX python API. For this first activate your environment *myenv* 
		
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

#### 3.1.1 Data Input

| Parameter        | Explanation | Example  | Type |
| ------------- |-------------| -----| -----|
| $session\\\_ids$      | Session indices | [1,2] | list |
| $track\\\_ids$     | Track indices | [1,2,3,4] | list |
| $author\\\_ids$      | Author indices | [1,...,20] | list |
| $paper\\\_ids$      | Paper indices | [1,...,32] | list |
| $bidder\\\_ids$      | Bidder indices | [1,...,20] | list |
| $topic\\\_ids$      | Topic indices | [1,...,10] | list |
|||||
| $U$      | Bidders' utilities map U, i.e., $U(b,p)$ represents bidder $b$’s bid on paper $p$. | {(1,12): 23.45, (1,14): 22.7, (7,4): 9.3,...} | dict |
| $M$      | Paper-author map M, i.e., $M(a,p)=1$ iff author $a$ is and author of paper $p$ and author $a$ has at least 2 papers (otherwise she can’t have a conflict with herself). | {(1,3): 1, (1,6):1, (3,4):1,...} | dict |
| $T$      | Paper-session map $T$, i.e., $T(j,p)=1$ iff paper $p$ cannot be presented in session $j$. | {(5,1): 1, (14,1): 1, (7,2): 1,...} | dict |
| $Q$      | Paper-topic map $Q$, i.e., $Q(p,t)=1$ iff paper $p$ has topic $t$. | {(1,2): 1, (1,7):1, (26,4):1,...} | dict |
|||||
| $paper\\\_title\\\_dict$      | Map between paperID and paper title. | {1: 'Paper Title 1', 2: 'Paper Title 2', 3: 'Paper Title3',...} | dict |
| $paper\\\_author\\\_dict$      | Map between paperID and all authors of the corresponding paper. | {1: ['Author1','Author2'], 2: ['Author5'], 3: ['Author2', 'Author4', 'Author8'] ,...} | dict(list) |
| $paper\\\_topic\\\_dict$      | Map between paperID and all topics of the corresponding paper. | {1: ['Topic1','Topic2'], 2: ['Topic5'], 3: ['Topic2', 'Topic4', 'Topic8'] ,...} | dict(list) |

#### 3.1.2 Parameter Input

| Parameter        | Explanation | Example  | Type |
| ------------- |-------------| -----| -----|
| $track\\\_session\\\_capacity$      | Capacity per subsession, i.e. session-track tuple. | 4 | int |
| $bidder\\\_cost$      | Cost for a bidder attending a subsession, i.e. session-track tuple. | 5 | int |
| $topic\\\_cost$      | Cost for a "topic"-bidder attending a subsession, i.e. session-track tuple. | 25 | int |
| $topic\\\_utility$      | Constant utility (constant analogue to $U$ map) for a "topic"-bidder attending a subsession, i.e. session-track tuple. | 100 | int |

### 3.2 Binary Decision Variables

### 3.2.1 Paper Variables
$x_{p,j,k} \in \\\{0,1\\\}\quad \forall (p,j,k) \in paper\\\_ids \times  session\\\_ids \times track\\\_ids$. 

The decision variable $x_{p,j,k}$ is used to model if a paper is allocated to a specific subsession (i.e. a session-track tuple). Specifically, paper $p$ is allocated to session $j$ and track $k$ iff $x_{p,j,k}=1$. Note that the final schedule is given by {$x_{p,j,k}: x_{p,j,k}=1$}.

### 3.2.2 Bidder Variables
**$y_{b,j,k} \in \\\{0,1\\\}\quad \forall (b,j,k) \in bidder\\\_ids \times  session\\\_ids \times track\\\_ids$.**

The decision variable $y_{b,j,k}$ is used to model if a bidder attends a specific subsession (i.e. a session-track tuple). Specifically, bidder $b$ attends session $j$ in track $k$ iff $y_{b,j,k}=1$. This decision variable is used  as an indication of audience interest, e.g., two papers with a high interest should not be presented simultaneously.

### 3.2.3 Author Variables
**$z_{a,j,k} \in \\\{0,1\\\}\quad \forall  (a,j,k) \in author\\\_ids \times  session\\\_ids \times track\\\_ids$.**

The decision variable $z_{a,j,k}$ is used to model if a author presents her paper in a specific subsession (i.e. a session-track tuple). Specifically, author $a$ presents her paper in session $j$ and track $k$ iff $z_{a,j,k}=1$. This decision variable is used to handle author-specific constraints, e.g., an author of 2 papers cannot simultaneously present both papers.

### 3.2.4 Topic Variables
**$q_{t,j,k} \in  \\\{0,1\\\}\quad \forall (t,j,k) \in topic\\\_ids \times  session\\\_ids \times track\\\_ids$.**

The decision variable $q_{t,j,k}$ is used to model if a topic is present in a specific subsession (i.e. a session-track tuple). Specifically, topic $t$ is present in session $j$ and track $k$ iff $q_{t,j,k}=1$. This decision variable is used to cluster papers with similar topics.

### 3.2 QIP Formulation

In this section, we present the QIP objective and its constraints.

#### 3.2.1 Objective

The QIP maximizes the following objective

$$ \large \max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k},\\\,\\\, q_{t,j,k}} \quad \sum_{(b,p) : U(b,p)>0}\quad \sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} x_{p,j,k} \cdot y_{b,j,k} \cdot U(b,p) \\\,- \quad (obj1)$$ 

$$ \large \hphantom{\max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k},\\\,\\\, q_{t,j,k}}} \sum_{b \in bidder\\\_ids}\quad\sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} y_{b,j,k} \cdot bidder\\\_cost \\\,+ \quad (obj2)$$ 

$$ \large \hphantom{aaaaaa\max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k},\\\,\\\, q_{t,j,k}}} \sum_{(t,p):Q(t,p)=1}\quad\sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} x_{p,j,k} \cdot q_{t,j,k} \cdot topic\\\_utility \\\,- \quad (obj3)$$ 

$$ \large \hphantom{\max_{x_{p,j,k},\\\,\\\, y_{b,j,k},\\\,\\\, z_{a,j,k}}} \sum_{t \in topic\\\_ids}\quad\sum_{j \in session\\\_ids}\quad\sum_{k \in track\\\_ids} q_{t,j,k} \cdot topic\\\_cost. \quad (obj4),$$ 

where the interpretation of each of the four objective terms is given as

**(obj1)**: sum of bidders' utilities.

**(obj2)**: sum of bidders' costs for attending a subsession (i.,e, session-track tuple) using a constant bidder-cost $bidder\\\_cost$.

**(obj3)**: sum of topics' utilities when using a constant topic utility $topic\\\_utility$.

**(obj4)**: sum topics' costs for beeing present in a subsession (i.e., session-track tuple) using a constant topic-cost $topic\\\_cost$.

#### 3.2.2 Constraints

##### Paper variables
1. For all $p \in paper\\\_ids: \\\, \sum_{j \in session\\\_ids} \sum_{k \in track\\\_ids} x_{p,j,k} = 1\quad$ (*Each paper appears exactly once*)
2. For all $j \in session\\\_ids$, for all $k \in track\\\_ids: \\\, \sum_{p \in paper\\\_ids}  x_{p,j,k} = track\\\_session\\\_capacity\quad$ (*Each track has exactly* $track\\\_session\\\_capacity$ *papers*)
3. For all $\\\{(j,p): T(j,p)==1\\\}$ and for all $k \in track\\\_ids: \\\, x_{p,j,k} = 0$ (*Time conflicts*)

##### Bidder variables
4. For all $b \in bidder\\\_ids$ and for all  $j \in session\\\_ids: \\\, \sum_{k \in track\\\_ids}  y_{b,j,k} <= 1\quad$ (*A bidder cannot be in more than one track per session*)

##### Author variables
5. For all $\\\{(a,p): M(a,p)==1\\\}$,  for all  $j \in session\\\_ids$ and for all $k \in track\\\_ids: \\\, z_{a,j,k} >= x_{p,j,k}\quad$ (*An author needs to attend a specific subsession, i.e., session-track tuple, if her paper is allocated to that subsession*)
6. For all $a \in author\\\_ids$ and for all $j \in session\\\_ids: \\\, \sum_{k \in track\\\_ids}  z_{a,j,k} <= 1\quad$ (*An author cannot be in more than one track per session*)


##### Topic variables
7. For all $t \in topic\\\_ids$ and for all $j \in session\\\_ids: \\\, \sum_{k \in track\\\_ids}  q_{t,j,k} <= 1\quad$ (*A "topic"-bidder cannot be in more than one track per session*)



## 4. How to Run

First you need to prepare your raw data and create all the data input objects described in Section **3.1.1 Data Input** and save them in the folder **/data_prepared**.

Note that for testing purposes, we provide random data input files in the folder *data_prepared* (if you wish to create new different random data input, then you can go to the file **create_random_instance.py** and make your desired changes accordingly, e.g., increasing the number of papers).

Next, open the file **create_schedule.py**:


```python
# %% Path
save_data_path = os.path.join(os.getcwd(),'data_prepared')

#create_random_instance(seed=1,save_data_path=save_data_path)
```

If you already created your data input (either real-world data or our random data input) then you can leave the line **create_random_instance(seed=1,save_data_path=save_data_path)** commented. Otherwise, if you want to create new random data input then you have to uncomment this line.

Next, set the input parameters:


```python
# %%  Set Input Parameters

track_session_capacity = 4
paper_distribution = 'exact' # 'exact' or 'upper_bound'
bidder_cost = 5
topic_cost = 25
topic_utility = 100

# QIP parameters
QIP_parameters = {'log_output': False,
                  'time_limit': 60, # in seconds
                  'mip_relative_gap': 0.01,
                  'integrality_tol': None,
                  'feasibility_tol': None,
                  }
```
Specifically, the parameter **paper_distribution** determines if a **$=$** ("exact") or a **$\le$** ("upper_bound") is used in constraint 2. from Section 3.2.2.

Once you set the input parameters first the data input is loaded from the folder **data_prepared**:


```python
# %% Load Data Input

# U MAPPING: U(b,p)= scaled preference of bidder_id:b for paper_id:p
U = pkl.load(open(os.path.join(save_data_path,'U.pkl'), 'rb'))
# M MAPPING: M(a,p)==1 iff author_id: a is an author of paper_id:p
M = pkl.load(open(os.path.join(save_data_path,'M.pkl'), 'rb'))
# T MAPPING: T(j,p)==1 iff paper_id:p CANNOT be presented in session:j
T = pkl.load(open(os.path.join(save_data_path,'T.pkl'), 'rb'))
# Q MAPPING: Q(p,t)==1 iff paper_id:p has topic ID:t
Q = pkl.load(open(os.path.join(save_data_path,'Q.pkl'), 'rb'))

# session_ids
session_ids = pkl.load(open(os.path.join(save_data_path,'session_ids.pkl'), 'rb'))
# track_ids
track_ids = pkl.load(open(os.path.join(save_data_path,'track_ids.pkl'), 'rb'))
# paper_ids
paper_ids = pkl.load(open(os.path.join(save_data_path,'paper_ids.pkl'), 'rb'))
# bidder_ids
bidder_ids = pkl.load(open(os.path.join(save_data_path,'bidder_ids.pkl'), 'rb'))
# author_ids
author_ids = pkl.load(open(os.path.join(save_data_path,'author_ids.pkl'), 'rb'))
# author_ids
topic_ids = pkl.load(open(os.path.join(save_data_path,'topic_ids.pkl'), 'rb'))

# paper_title_dict
paper_title_dict = pkl.load(open(os.path.join(save_data_path,'paper_title_dict.pkl'), 'rb'))
# paper_author_dict
paper_author_dict = pkl.load(open(os.path.join(save_data_path,'paper_author_dict.pkl'), 'rb'))
# paper_topic_dict
paper_topic_dict = pkl.load(open(os.path.join(save_data_path,'paper_topic_dict.pkl'), 'rb'))
```

and finally the QIP is instantiated, solved and an output folder **QIP_RESULTS_<day_month_year>_<hh-mm-ss>** is created.

```python
# %% QIP

#  INSTNATIATE AND BUILD QIP
QIP_instance = QIP(session_ids=session_ids,
                   track_ids=track_ids,
                   paper_ids=paper_ids,
                   bidder_ids=bidder_ids,
                   author_ids=author_ids,
                   topic_ids = topic_ids,
                   track_session_capacity=track_session_capacity,
                   paper_distribution=paper_distribution,
                   U=U,
                   M=M,
                   T=T,
                   Q=Q,
                   bidder_cost = bidder_cost,
                   topic_cost = topic_cost,
                   topic_utility = topic_utility,
                   QIP_parameters = QIP_parameters,
                   save_results=True,
                   savefolder='QIP_RESULTS')

QIP_instance.build()

#  SOLVE QIP
QIP_instance.solve()
QIP_instance.summary()

# TRANSFORM QIP_instance.schedule to nice format and create output folder
QIP_instance.create_schedule(filename = 'schedule',
                             paper_author_dict = paper_author_dict,
                             paper_title_dict = paper_title_dict,
                             paper_topic_dict =  paper_topic_dict,
                             )
```

Once you set all input parameters and prepared the input data you can create a conference schedule by running

```bash
$ python create_schedule.py
```
	
Note that we already provide an output folder **QIP_RESULTS_17_06_2022_15-47-37** that corresponds to our random data input.
	
Each output folder **QIP_RESULTS_<day_month_year>_<hh-mm-ss>** (of a successful QIP run) contains the following files:

| Filename        | Explanation |
| ------------- |-------------|
| qip_constraints_<day_month_year>_<hh-mm-ss>.txt      | QIP constraints |
| qip_objective_<day_month_year>_<hh-mm-ss>.txt      | QIP objective |
| qip_logs_<day_month_year>_<hh-mm-ss>.log      | Log file when running create_schedule.py |
| qip_solution_<day_month_year>_<hh-mm-ss>.json      | CPLEX solution file |
| qip_solve_details_<day_month_year>_<hh-mm-ss>.json      | CPLEX solve details |
| qip_schedule_<day_month_year>_<hh-mm-ss>.pkl      | QIP final schedule saved as pickle file; An OrderedDict with key-value pairs as follows: (session_id,track_id): list of paper_id's which are allocated |
| schedule_<day_month_year>_<hh-mm-ss>.xlsx      | QIP final schedule nicely formatted as .xlsx file. |
	
	
### Final Schedule as Excel File
	
The final schedule schedule_<day_month_year>_<hh-mm-ss>.xlsx contains for each session-track tuple $(j,k)\in session\\\_ids \times track\\\_ids$ (i.e. subsession) the following information: 
	
|        	|| $TRACK k$     |
| -------------------------- |--------------------------|--------------------------|
|  $SESSIONj$  |$Topics$      | Union of topics of papers allocated to that subsession and \*ATTENDANCE\* measure calculated as $\sum_{b \in bidder\\\_ids} y_{b,j,k}$.| 
|	        |$Paper1$	      |ID: <paper ID><br /> Title:<paper title><br /> Authors:<paper authors>|
| ... 		|...| ...|
|	        |$Paper[track\\\_session\\\_capacity]$| ID: <paper ID><br /> Title:<paper title><br /> Authors:<paper authors>|	

## 5. Adding Specific Paper Constraints
	
If you want to add specific "hard" paper constraints in your QIP formulation you can implement them via the method **def _add_specific_paper_constraints(self)** in the class-file **qip.py** as follows:
	
``` python
def _add_specific_paper_constraints(self):
	
	# PAPER SPECIFIC CONSTRAINTS
	for j,k in self.session_track_tuple_ids:
	    self.QIP.add_constraint(ct=(self.x[(14, j, k)]==self.x[(20, j, k)]),
				    ctname=f'SPECIAL_CT_PAPERIDs_14-20-21-29_SESSION{j}_TRACK{k}')
	    self.QIP.add_constraint(ct=(self.x[(20, j, k)]==self.x[(21, j, k)]),
				    ctname=f'SPECIAL_CT_PAPERIDs_14-20-21-29_SESSION{j}_TRACK{k}')
	    self.QIP.add_constraint(ct=(self.x[(21, j, k)]==self.x[(29, j, k)]),
				    ctname=f'SPECIAL_CT_PAPERIDs_14-20-21-29_SESSION{j}_TRACK{k}')
	
```
	
The example above ensures that paper ids 14, 20, 21, and 29 are all alllocated to the same subsession (i.e., session-track tuple). You can use such paper specific constraints for example to make sure that papers with similar topics are allocated to the same subsession (i.e., session-track tuple). Note that for the random data input we used the above defined paper specific constraints (see Session 1 Track 4 in schedule_17_06_2022_15-47-37.xlsx).
	
## Contact
Maintained by: Jakob Weissteiner (weissteiner)

Website: www.jakobweissteiner.com

E-mail: weissteiner@ifi.uzh.ch
