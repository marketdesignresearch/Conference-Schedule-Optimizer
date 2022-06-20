# -*- coding: utf-8 -*-
"""
Created on Tue May 24 16:59:42 2022

@author: jakob
"""


# Libs
import logging
import docplex.mp.model as cpx
from itertools import product
from collections import OrderedDict
from datetime import datetime
import json
import pickle as pkl
from copy import deepcopy
import pandas as pd
import os
import xlsxwriter
# DOCPLEX documentation: http://ibmdecisionoptimization.github.io/docplex-doc/mp/docplex.mp.model.html


# %%
class QIP:

    '''
    This implements the class QIP.
    This class is used for solving the QIP formulation of the scheduling problem.
    '''

    def __init__(self,
                 session_ids,
                 track_ids,
                 paper_ids,
                 bidder_ids,
                 author_ids,
                 topic_ids,
                 track_session_capacity,
                 paper_distribution,
                 U,
                 M,
                 T,
                 Q,
                 QIP_parameters,
                 bidder_cost,
                 topic_cost,
                 topic_utility,
                 save_results,
                 savefolder=None):

        self.session_ids = session_ids
        self.track_ids = track_ids
        self.session_track_tuple_ids = list(product(self.session_ids,self.track_ids))
        self.paper_ids = paper_ids
        self.paper_track_tuple_ids = list(product(self.paper_ids,self.track_ids))
        self.bidder_ids = bidder_ids
        self.author_ids = author_ids
        self.topic_ids = topic_ids
        self.track_session_capacity = track_session_capacity
        self.paper_distribution = paper_distribution
        self.QIP_date_time = datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        self.QIP_parameters = QIP_parameters
        self.name = "QIP"
        self.QIP = cpx.Model(name=self.name)  # QIP docplex instance
        self.save_results = save_results

        if self.save_results:
            if savefolder:
                self.savefolder = savefolder+'_'+self.QIP_date_time
                os.makedirs(self.savefolder, exist_ok=True)
            else:
                self.savefolder = os.getcwd()


        self.U = U
        self.M = M
        self.T = T
        self.Q = Q

        self.bidder_cost = bidder_cost
        self.topic_cost = topic_cost
        self.topic_utility = topic_utility

        self.allocation = OrderedDict()
        self.schedule = OrderedDict()
        self.attendance = OrderedDict()
        self.soltime = None  # timing

        self.objective1_ids = [] # 1st sum in objective: bidders' utilitites, i.e. bids
        self.objective2_ids = [] # 2nd sum in objective: bidders' costs, i.e. bids
        self.objective3_ids = [] # 3rd sum in objective: topics' utilitites
        self.objective4_ids = [] # 4th sum in objective: topics' costs

        self.QIP_built = False

        self.set_logging()
        logging.info(f'CREATE QIP: {self.name} on {self.QIP_date_time}')
        logging.info(self.log_sep)


    def set_logging(self):
        # Clear existing logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # --------------------------------------
        # LOG TO CONSOLE and TO FILE qip_logs.txt
        logging.basicConfig(level=logging.DEBUG,
                            datefmt='%Y-%m-%d %H:%M:%S',
                            format='%(asctime)s: %(message)s',
                            filename = os.path.join(self.savefolder,'qip_logs_'+ self.QIP_date_time +'.log'),
                            filemode='w')

        # define a Handler which writes DEBUG messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        self.log_sep = ''.join(['-']*80)


    def print_input_info(self):
        logging.info('')
        logging.info('QIP INPUT:')
        logging.info(self.log_sep)
        logging.info(f'TRACK-SESSION-CAPACITY:{self.track_session_capacity}')
        logging.info(f'PAPER-DISTRIBUTION-METHOD:{self.paper_distribution}')
        logging.info(f'SESSIONS:{len(self.session_ids)} | {self.session_ids}')
        logging.info(f'TRACKS:{len(self.track_ids)} | {self.track_ids}')
        logging.info(f'BIDS (=len(U)):{len(self.U.keys())}')
        logging.info(f'PAPER-SESSION CONFLICTS (=len(T)):{len(self.T.keys())}')
        logging.info(f'PAPERS:{len(self.paper_ids)}')
        logging.info(f'{self.paper_ids}')
        logging.info('')
        logging.info(f'BIDDERS:{len(self.bidder_ids)}')
        logging.info(f'{self.bidder_ids}')
        logging.info('')
        logging.info(f'AUTHORS:{len(self.author_ids)}')
        logging.info(f'{self.author_ids}')


    def define_QIP_variables(self):
        self.x = {}  # binary QIP paper variable, i.e., x_{p,j,k} in {0,1} where x_{p,j,k}==1 iff paper_id:p is allocated to session_id:j and track_id:k
        for p in self.paper_ids:
            for j,k in self.session_track_tuple_ids:
                self.x[(p, j, k)] = self.QIP.binary_var(name=f'x_{p}_{j}_{k}')

        self.y = {}  # binary QIP bidder variable, i.e., y_{b,j,k} in {0,1} where y_{b,j,k}==1 iff bidder_id:b is attending session_id:j and track_id:k
        for b in self.bidder_ids:
            for j,k in self.session_track_tuple_ids:
                self.y[(b, j, k)] = self.QIP.binary_var(name=f'y_{b}_{j}_{k}')

        self.z = {}  # binary QIP author variable, i.e., z_{a,j,k} in {0,1} where z_{a,j,k}==1 iff author_id:a is presenting in session_id:j and track_id:k
        for a in self.author_ids:
            for j,k in self.session_track_tuple_ids:
                self.z[(a, j, k)] = self.QIP.binary_var(name=f'z_{a}_{j}_{k}')

        self.q = {}  # binary QIP topic variable, i.e., q_{t,j,k} in {0,1} where q_{t,j,k}==1 iff topic_id:t is attending in session_id:j and track_id:k
        for t in self.topic_ids:
            for j,k in self.session_track_tuple_ids:
                self.q[(t, j, k)] = self.QIP.binary_var(name=f'q_{t}_{j}_{k}')


    def check_paper_allocation(self,
                               verbose=0):
        for p in self.paper_ids:

            if verbose > 0:
                logging.info(f'PaperID:{p} allocated:{1==sum([self.x[(p,j,k)].solution_value for j,k in self.session_track_tuple_ids])}')
            paper_allocated = (1==sum([self.x[(p,j,k)].solution_value for j,k in self.session_track_tuple_ids]))
            if not paper_allocated:
                raise RuntimeError(f'Paper{p} was not allocated!')
        logging.info(f'{len(self.paper_ids)} Papers allocated')
        logging.info('')


    def print_optimal_allocation(self):
        logging.info('QIP Solution:')
        logging.info(f'{len(self.allocation)} papers allocated')
        for p,v in self.allocation.items():
            logging.info(f'PaperID{p} -> Session:{v[0]}|Track:{v[1]}')


    def print_schedule(self):
        i = 0
        for key, v in self.schedule.items():
            logging.info(f'({i}) Session:{key[0]} | Track:{key[1]}')
            logging.info('|'.join([str(x) for x in v]))
            logging.info('')
            i +=1


    def solve(self):
        if not self.QIP_built:
            raise ValueError('QIP build-status:{QIP_built}, first call .build()!')

        log_output = self.QIP_parameters['log_output']
        time_limit = self.QIP_parameters['time_limit']
        mip_relative_gap = self.QIP_parameters['mip_relative_gap']
        integrality_tol = self.QIP_parameters['integrality_tol']
        feasibility_tol = self.QIP_parameters['feasibility_tol']

        # set time limit
        if time_limit is not None:
            self.QIP.set_time_limit(time_limit)
        # set mip relative gap
        if mip_relative_gap is not None:
            self.QIP.parameters.mip.tolerances.mipgap.set(mip_relative_gap)
        # set mip integrality tolerance
        if integrality_tol is not None:
            self.QIP.parameters.mip.tolerances.integrality.set(integrality_tol)
        # Set feasibility tolerance
        if feasibility_tol is not None:
            self.QIP.parameters.simplex.tolerances.feasibility.set(feasibility_tol)

        logging.info('')
        logging.info('SOLVE QIP')
        logging.info(self.log_sep)
        logging.info('QIP time Limit of %s', self.QIP.get_time_limit())
        logging.info('QIP relative gap %s', self.QIP.parameters.mip.tolerances.mipgap.get())
        logging.info('QIP integrality tol %s', self.QIP.parameters.mip.tolerances.integrality.get())
        logging.info('QIP feasibility tol %s', self.QIP.parameters.simplex.tolerances.feasibility.get())

        # solve QIP
        Sol = self.QIP.solve(log_output=log_output)
        if Sol:
            self.soltime = Sol.solve_details._time
            qip_solve_details = self.log_solve_details()

            unsatisfied_constraints = Sol.find_unsatisfied_constraints(self.QIP)
            logging.info(f'QIP unsatisfied constraints: {unsatisfied_constraints}')
            assert len(unsatisfied_constraints) == 0, \
                f'Solution does not satisfy {len(unsatisfied_constraints)} constraint(s).'
        else:
            self.soltime = None
            self.log_solve_details() # will throw error if not solved sucesfully
            return


        # set the optimal allocation and optimal schedule
        for j,k in self.session_track_tuple_ids:
            for p in self.paper_ids:
                if self.x[(p, j, k)].solution_value == 1:
                    self.allocation[p] = (j,k)
                    if (j,k) in self.schedule:
                        self.schedule[(j,k)].append(p)
                    else:
                        self.schedule[(j,k)] = [p]

        # calculate attendance
        self.calc_attendance()

        if self.save_results:
            Sol.export(file_or_filename=os.path.join(self.savefolder,'qip_solution_'+self.QIP_date_time+'.json'),format='json')
            json.dump(qip_solve_details, open(os.path.join(self.savefolder,'qip_solve_details_'+self.QIP_date_time+'.json'),'w'))
            pkl.dump(self.schedule, open(os.path.join(self.savefolder,'qip_schedule_'+self.QIP_date_time+'.pkl'),'wb'))

        return self.schedule


    def log_solve_details(self):
        details = self.QIP.get_solve_details()
        logging.info('')
        logging.info('SOLVE DETAILS:')
        logging.info('Problem : %s', details.problem_type)
        logging.info('Status  : %s', details.status)
        logging.info('Time    : %s sec', round(details.time))
        logging.info('Rel. Gap: {}'.format(details.mip_relative_gap))
        logging.info('N. Iter : %s', details.nb_iterations)
        logging.info('Hit Lim.: %s', details.has_hit_limit())
        logging.info('Objective Value: %s', self.QIP.objective_value)
        logging.info(f'Status: {self.QIP.get_solve_status()}')

        return {'Problem': details.problem_type,
                'Status': details.status,
                'Time': details.time,
                'Relative_Gap': details.mip_relative_gap,
                'N_Iter': details.nb_iterations,
                'Hit_Time_Limit': details.has_hit_limit(),
                'Objective_Value': self.QIP.objective_value
                }


    def log_build_details(self):
        details = str(self.QIP.get_statistics())
        details = details.replace(' ','').replace('\n','').split('-')[1:]

        logging.info('')
        logging.info('BUILD DETAILS:')
        for detail in details:
            logging.info(detail)


    def summary(self):
        logging.info('')
        logging.info('')
        logging.info(''.join(['#'])*80)
        logging.info(''.join([' '])*30+'QIP SUMMARY')
        logging.info(''.join(['#'])*80)
        self.log_solve_details()
        self.log_build_details()

        logging.info('')
        logging.info('SCHEDULE:')
        self.check_paper_allocation()
        self.print_schedule()
        logging.info(''.join(['#'])*80)


    def create_schedule(self,
                        filename,
                        paper_author_dict,
                        paper_title_dict,
                        paper_topic_dict,
                        ):


        QIP_SCHEDULE = deepcopy(self.schedule)

        # create nice schedule
        FINAL_SCHEDULE = {}
        for subsession, papers in QIP_SCHEDULE.items():

            FINAL_SCHEDULE[subsession] = {}

            subsession_topics = []
            paper_dicts = {}
            i = 1
            for p in papers:
                paper_dicts[f'Paper{i}'] = {}
                paper_dicts[f'Paper{i}']['ID'] = p
                paper_dicts[f'Paper{i}']['Title'] = paper_title_dict[p]
                paper_dicts[f'Paper{i}']['Authors'] = paper_author_dict[p]

                topics = paper_topic_dict[p]
                #paper_dicts[p]['Topics'] = topics #individual paper topics
                for topic in topics:
                    if topic not in subsession_topics:
                        subsession_topics.append(topic)
                i +=1

            subsession_topics.append(f' *ATTENDANCE:{self.attendance[(subsession[0],subsession[1])]}*')

            FINAL_SCHEDULE[subsession]['Topics'] = subsession_topics

            placeholder_dict = {'ID':'','Title':'','Authors':''}
            #placeholder_dict = {'ID':'', 'Title':'','Authors':'','Topics':''} #individual paper topics
            for i in range(1,self.track_session_capacity+1):
                FINAL_SCHEDULE[subsession][f'Paper{i}'] = paper_dicts.get(f'Paper{i}',placeholder_dict)

        # log nice schedule to console
        i = 1
        for k, v in FINAL_SCHEDULE.items():
            logging.info(f'SESSION:{k[0]} TRACK:{k[1]} ATTENDANCE:{self.attendance[(k[0],k[1])]} (Subsession:{i})')
            logging.info(''.join(['-']*60))
            logging.info('TOPICS:')
            logging.info('|'.join(v["Topics"]))
            logging.info('')
            logging.info('PAPERS:')
            for key in v:
                if key != "Topics":
                    logging.info(f'ID:{v[key]["ID"]}')
                    logging.info(f'Title:{v[key]["Title"]}')
                    logging.info(f'Authors:{", ".join(v[key]["Authors"])}')
                    #logging.info(f'Topics:{", ".join(v[key]["Topics"])}') #individual paper topics
                    logging.info('')
            logging.info(''.join(['-']*60))
            logging.info('')
            i +=1

        # save nice schedule as .xlsx file
        # FINAL_SCHEDULE_EXCEL is a pandas dataframe with MULTI-INDEX:(Session,Paper) and COLUMNS:Tracks
        FINAL_SCHEDULE_EXCEL = {}
        for k1, v1 in FINAL_SCHEDULE.items():
            for k2,v2 in v1.items():
                if (f'SESSION{k1[0]}',k2) in FINAL_SCHEDULE_EXCEL:
                    pass
                else:
                    FINAL_SCHEDULE_EXCEL[(f'SESSION{k1[0]}',k2)] = {}
                if k2 != 'Topics':
                    tmp = []
                    for k3,v3 in v2.items():
                        if k3=='Authors':
                            tmp.append(f'{k3}: {", ".join(v3)}')
                        else:
                            tmp.append(f'{k3}: {str(v3)}')
                        FINAL_SCHEDULE_EXCEL[(f'SESSION{k1[0]}',k2)][f'TRACK {k1[1]}'] = '\n'.join(tmp)
                else:
                    FINAL_SCHEDULE_EXCEL[(f'SESSION{k1[0]}',k2)][f'TRACK {k1[1]}'] = '|'.join(FINAL_SCHEDULE[k1][k2])

        if self.save_results:

            col_width = 100
            row_height = 60

            writer = pd.ExcelWriter(os.path.join(self.savefolder,filename + '_' + self.QIP_date_time+'.xlsx'),
                                    engine='xlsxwriter')
            df = pd.DataFrame.from_dict(FINAL_SCHEDULE_EXCEL,orient='index')
            df.to_excel(writer,
                        sheet_name='Conference_Schedule',
                        header=True,
                        index=True
                        )
            workbook=writer.book
            worksheet = writer.sheets['Conference_Schedule']

            worksheet.set_column(first_col=2,
                                 last_col=2+self.track_session_capacity,
                                 width=col_width,
                                 cell_format = workbook.add_format({'align':'vcenter'}))

            # multi-index rows
            col1 = workbook.add_format({'bg_color': '#CDB4DB','text_wrap': True,'align':'vcenter'})
            col_topics1 = workbook.add_format({'bg_color': '#FFAFCC','text_wrap': True,'align':'vcenter','bold': True})
            col2 = workbook.add_format({'bg_color': '#A2D2FF','text_wrap': True,'align':'vcenter'})
            col_topics2 = workbook.add_format({'bg_color': '#BDE0FE','text_wrap': True,'align':'vcenter','bold': True})

            col_change = 0
            for r in range(1,df.shape[0]+1):
                if col_change == self.track_session_capacity+1:
                    col1,col2 = col2, col1
                    col_topics1,col_topics2 = col_topics2,col_topics1
                    col_change = 0
                if col_change == 0:
                    worksheet.set_row(row=r,height=row_height,cell_format=col_topics1)
                else:
                    worksheet.set_row(row=r,height=row_height,cell_format=col1)
                col_change +=1

            worksheet.set_column(first_col=2+self.track_session_capacity+1,
                                 last_col=2+self.track_session_capacity+2,
                                 cell_format = workbook.add_format({'bg_color': '#CCCCCC'}))

            writer.save()


    def print_constraints(self,
                          only_save=False
                          ):
        to_write = 'CONSTRAINTS\n'
        to_write += '##########################################################################\n'

        k = 0
        for m in range(0, self.QIP.number_of_constraints):
            if self.QIP.get_constraint_by_index(m) is not None:
                to_write += f'({k}):   {self.QIP.get_constraint_by_index(m)}\n'
                k = k + 1

        if only_save:
            with open(os.path.join(self.savefolder,'qip_constraints_'+self.QIP_date_time+'.txt'), "w") as text_file:
                text_file.write(to_write)
        else:
            print(to_write)
            with open(os.path.join(self.savefolder,'qip_constraints_'+self.QIP_date_time+'.txt'), "w") as text_file:
                text_file.write(to_write)


    def print_objective(self,
                        only_save=False
                        ):
        obj = 'OBJECTIVE\n'
        obj += '##########################################################################\n'
        obj += str(self.QIP.get_objective_expr())

        if only_save:
            with open(os.path.join(self.savefolder,'qip_objective_'+self.QIP_date_time+'.txt'), "w") as text_file:
                text_file.write(obj)
        else:
            print(obj)
            with open(os.path.join(self.savefolder,'qip_objective_'+self.QIP_date_time+'.txt'), "w") as text_file:
                text_file.write(obj)


    def build(self):
        self.print_input_info()

        logging.info('')
        logging.info('BUILD QIP')
        logging.info(self.log_sep)

        # define QIP variables
        self.define_QIP_variables()

        # add paper variable x constraints
        self.add_paper_constraints()

        # add bidder variable y constraints
        self.add_bidder_constraints()

        # add author variable z constraints
        self.add_author_constraints()

        # add topic variable q constraints
        self.add_topic_constraints()

        # add objective
        self.add_objective()

        self.QIP_built = True
        logging.info('Succesfully Built QIP')
        self.log_build_details()

        if self.save_results:
            self.print_constraints(only_save=True)
            self.print_objective(only_save=True)


    def add_topic_constraints(self):

        # a topic-"bidder" cannot be in more than one track per session
        for t in self.topic_ids:
            for j in self.session_ids:

                C = self.QIP.sum(self.q[(t, j, k)] for k in self.track_ids)

                self.QIP.add_constraint(ct=(C<=1),
                                        ctname=f'TOPIC{t}_SESSION{j}_CAN_ONLY_BE_IN_SINGLE_TRACK')


    def add_paper_constraints(self):

        # Each paper p appears exactly once in a (session,track) tuple
        for p in self.paper_ids:

             C = self.QIP.sum(self.x[(p, j, k)] for j,k in self.session_track_tuple_ids)

             self.QIP.add_constraint(ct=(C==1),
                                     ctname=f'PAPER{p}_ALLOC_EXACTLY_ONCE')

        # Each Track has exactly n_papers_per_track papers
        for j,k in self.session_track_tuple_ids:

            C = self.QIP.sum(self.x[(p, j, k)] for p in self.paper_ids)

            if self.paper_distribution == 'upper_bound':
                self.QIP.add_constraint(ct=C<=self.track_session_capacity,
                                        ctname=f'SESSION{j}_TRACK{k}_HAS_<=_{self.track_session_capacity}_PAPERS')

            elif self.paper_distribution == 'exact':
                self.QIP.add_constraint(ct=C==self.track_session_capacity,
                                        ctname=f'SESSION{j}_TRACK{k}_HAS_==_{self.track_session_capacity}_PAPERS')
            else:
                raise NotImplementedError(f'paper_distribution:{self.paper_distribution} not implemented!')

        # Time Conflicts: paper p cannot be presented in session j
        for j,p in self.T.keys():
            for k in self.track_ids:
                self.QIP.add_constraint(ct=self.x[(p, j, k)] == 0,
                                        ctname=f'PAPER{p}_CANNOT_BE_IN_SESSION{j}')

        # Add specific paper constraints
        self._add_specific_paper_constraints()


    def _add_specific_paper_constraints(self):
        pass

# =============================================================================
#         # EXAMPLE PAPER SPECIFIC CONSTRAINTS for random data input
#         for j,k in self.session_track_tuple_ids:
#             self.QIP.add_constraint(ct=(self.x[(14, j, k)]==self.x[(20, j, k)]),
#                                     ctname=f'SPECIAL_CT_PAPERIDs_14-20-21-29_SESSION{j}_TRACK{k}')
#             self.QIP.add_constraint(ct=(self.x[(20, j, k)]==self.x[(21, j, k)]),
#                                     ctname=f'SPECIAL_CT_PAPERIDs_14-20-21-29_SESSION{j}_TRACK{k}')
#             self.QIP.add_constraint(ct=(self.x[(21, j, k)]==self.x[(29, j, k)]),
#                                     ctname=f'SPECIAL_CT_PAPERIDs_14-20-21-29_SESSION{j}_TRACK{k}')
# =============================================================================



    def calc_attendance(self):
        for j,k in self.session_track_tuple_ids:
            self.attendance[(j,k)]=int(sum([self.y[(b, j, k)].solution_value for b in self.bidder_ids]))



    def add_bidder_constraints(self):
        # Bidder can only be present in one track simulataneously
        for b in self.bidder_ids:
            for j in self.session_ids:

                C = self.QIP.sum(self.y[(b, j, k)] for k in self.track_ids)

                self.QIP.add_constraint(ct=(C<=1),
                                        ctname=f'BIDDER{b}_SESSION{j}_CAN_ONLY_BE_IN_SINGLE_TRACK')


    def add_author_constraints(self):
        # Author must be in session,track where his paper is allocated to
        for a,p in self.M.keys():
            for j in self.session_ids:
                for k in self.track_ids:
                    self.QIP.add_constraint(ct=self.z[(a, j, k)] >= self.x[(p, j, k)],
                                            ctname=f'AUTHOR{a}_PAPER{p}_SESSION{j}_TRACK{j}_PRESENCE')

        # An author cannot be in more than one track per session
        for a in self.author_ids:
            for j in self.session_ids:

                C = self.QIP.sum(self.z[(a, j, k)] for k in self.track_ids)

                self.QIP.add_constraint(ct=(C<=1),
                                        ctname=f'AUTHOR{a}_SESSION{j}_CAN_ONLY_BE_IN_SINGLE_TRACK')


    def add_objective(self):

        # create summation index only for U(b,p)>0
        for b,p in self.U.keys():
            for j,k in self.session_track_tuple_ids:
                self.objective1_ids.append((p,j,k,b))

        # create summation index for bidder cost
        for b in self.bidder_ids:
            for j,k in self.session_track_tuple_ids:
                self.objective2_ids.append((b,j,k))

        # create summation index only for Q(p,t)>0
        for p,t in self.Q.keys():
            for j,k in self.session_track_tuple_ids:
                self.objective3_ids.append((p,j,k,t))

        # create summation index for topic cost
        for t in self.topic_ids:
            for j,k in self.session_track_tuple_ids:
                self.objective4_ids.append((t,j,k))

        # set quadratic objective
        objective1 = self.QIP.sum(self.x[(p, j, k)]*self.y[(b, j, k)]*self.U[(b,p)] for p,j,k,b in self.objective1_ids)

        objective2 = self.QIP.sum(self.bidder_cost*self.y[(b, j, k)] for b,j,k in self.objective2_ids)

        objective3 = self.QIP.sum(self.x[(p, j, k)]*self.q[(t, j, k)]*self.topic_utility for p,j,k,t in self.objective3_ids)

        objective4 = self.QIP.sum(self.topic_cost*self.q[(t, j, k)] for t,j,k in self.objective4_ids)

        self.QIP.maximize(objective1-objective2+objective3-objective4)



