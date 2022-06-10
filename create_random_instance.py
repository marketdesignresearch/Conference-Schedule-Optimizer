# -*- coding: utf-8 -*-
"""
Created on Tue May 24 10:33:14 2022

@author: jakob
"""

import pickle as pkl
import os
import random

def create_random_instance(seed,
                           save_data_path):

    # Paths
    os.makedirs(save_data_path, exist_ok=True)
    print('CREATE PREPARED DATA AND MAPPINGS:')
    print(''.join(['-']*50))
    print(f'SAVE PREPARED DATA IN: {save_data_path}')
    random.seed(seed)

    # Create session indices
    session_ids = list(range(1,3))
    # Create track indices
    track_ids = list(range(1,5))
    # Create author indices
    author_ids = list(range(1,21))
    # Create bidder indices
    bidder_ids = list(range(1,21))
    # Create topic indices
    topic_ids = list(range(1,11))
    # Create paper indices
    paper_ids = list(range(1,33))
    # Create paper-title dict
    paper_title_dict = {}
    for p in paper_ids:
        paper_title_dict[p] = f'Paper Title {p}'

    # Create Random U MAPPING:
    # U(b,p) = preference of bidder id:b for paper id:p scaled to [0,100]
    U = {}
    for b in bidder_ids:
        number_of_submitted_bids = random.randint(1,3)
        sampled_papers = sorted(random.sample(paper_ids,number_of_submitted_bids))
        for p in sampled_papers:
            U[(b,p)] = random.uniform(0, 100)

    # Create Random M MAPPING:
    # M(a,p)==1 iff author id: a is an author of paper id:p and author a has >= 2 papers
    M = {}
    for p in paper_ids:
        number_of_authors = random.randint(1,2)
        sampled_authors = sorted(random.sample(author_ids,number_of_authors))
        for a in sampled_authors:
            M[(a,p)] = 1

    # Create paper-author dict
    paper_author_dict = {}
    for key in M:
        if key[1] in paper_author_dict:
            paper_author_dict[key[1]].append(f'Author{key[0]}')
        else:
            paper_author_dict[key[1]] = [f'Author{key[0]}']

    # Remove from M mapping authors with less than two papers, since they are not constrained by session conflicts.
    paper_count = {}
    for key in M:
        if key[0] in paper_count:
            paper_count[key[0]] += 1
        else:
            paper_count[key[0]] = 1
    for a, c in paper_count.items():
        if c == 1:
            to_del = [key for key in M.keys() if key[0]==a]
            del M[to_del[0]]

    # T MAPPING: T(j,p)==1 iff paper id:p CANNOT be presented in session_id:j
    T = {(1,10):1,(2,20):1}

    # % Q MAPPING: Q(p,t)==1 iff paper id: p has topic id:t
    Q = {}
    for p in paper_ids:
        number_of_topics = random.randint(1,3)
        sampled_topics = sorted(random.sample(topic_ids,number_of_topics))
        for t in sampled_topics:
            Q[(p,t)] = 1

    # Create paper-topic dict
    paper_topic_dict = {}
    for key in Q:
        if key[0] in paper_topic_dict:
            paper_topic_dict[key[0]].append(f'Topic{key[1]}')
        else:
            paper_topic_dict[key[0]] = [f'Topic{key[1]}']

    # SAVE
    pkl.dump(U, open(os.path.join(save_data_path,'U.pkl'), 'wb'))
    pkl.dump(M, open(os.path.join(save_data_path,'M.pkl'), 'wb'))
    pkl.dump(T, open(os.path.join(save_data_path,'T.pkl'), 'wb'))
    pkl.dump(Q, open(os.path.join(save_data_path,'Q.pkl'), 'wb'))

    pkl.dump(session_ids, open(os.path.join(save_data_path,'session_ids.pkl'), 'wb'))
    pkl.dump(track_ids, open(os.path.join(save_data_path,'track_ids.pkl'), 'wb'))
    pkl.dump(bidder_ids, open(os.path.join(save_data_path,'bidder_ids.pkl'), 'wb'))
    pkl.dump(author_ids, open(os.path.join(save_data_path,'author_ids.pkl'), 'wb'))
    pkl.dump(paper_ids, open(os.path.join(save_data_path,'paper_ids.pkl'), 'wb'))
    pkl.dump(topic_ids, open(os.path.join(save_data_path,'topic_ids.pkl'), 'wb'))

    pkl.dump(paper_author_dict, open(os.path.join(save_data_path,'paper_author_dict.pkl'), 'wb'))
    pkl.dump(paper_title_dict, open(os.path.join(save_data_path,'paper_title_dict.pkl'), 'wb'))
    pkl.dump(paper_topic_dict, open(os.path.join(save_data_path,'paper_topic_dict.pkl'), 'wb'))

    print(f'Sessions:{session_ids}')
    print(f'Tracks:{track_ids}')

    print(f'#Papers:{len(paper_ids)}')
    print(f'#Authors:{len(author_ids)}')
    print(f'#Topics:{len(topic_ids)}')

    print(f'#Bids:{len(U)}')
    print(f'len(M):{len(M)}')
    print(f'len(T):{len(T)}')
    print(f'len(Q):{len(Q)}')
    print(f'len(paper_author_dict):{len(paper_author_dict)}')
    print(f'len(paper_title_dict):{len(paper_title_dict)}')
    print(f'len(paper_topic_dict):{len(paper_topic_dict)}')
    return