# -*- coding: utf-8 -*-
"""
Created on Tue May 24 16:48:20 2022

@author: jakob
"""

import pickle as pkl
import os

# own modules
from create_random_instance import create_random_instance
from qip import QIP

# %% Path
save_data_path = os.path.join(os.getcwd(),'data_prepared')

#
create_random_instance(seed=1,save_data_path=save_data_path)

# %% Create Schedule

track_session_capacity = 4
paper_distribution = 'exact' # 'exact' or 'upper_bound'
bidder_cost = 5
topic_cost = 25
topic_utility = 100

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

# QIP parameters
QIP_parameters = {'log_output': False,
                  'time_limit': 60, # in seconds
                  'mip_relative_gap': 0.01,
                  'integrality_tol': None,
                  'feasibility_tol': None,
                  }
# %% QIP

#  BUILD QIP
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

# TRANSFORM QIP_instance.schedule to nice format
QIP_instance.create_schedule(filename = 'schedule',
                             paper_author_dict = paper_author_dict,
                             paper_title_dict = paper_title_dict,
                             paper_topic_dict =  paper_topic_dict,
                             )