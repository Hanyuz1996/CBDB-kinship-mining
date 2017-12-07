#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 08:02:58 2017

@author: mac
"""

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import Queue 

kindata = pd.DataFrame.from_csv('/users/mac/Desktop/CBDB/kindata.csv')
biogmain = pd.DataFrame.from_csv('/users/mac/Desktop/CBDB/bio_main.csv')
kindatacode = pd.DataFrame.from_csv('/users/mac/Desktop/CBDB/kinship_codes.csv')
m = kindata.shape[0]
people = set(kindata['c_personid'])
n = len(people)
unvisited = people - set([0])
kindata.index=range(m)
graphs = []
pairs = []

while(len(unvisited)>0):
    k = min(unvisited)
    G = nx.MultiDiGraph()
    Q = Queue.Queue(maxsize=0.5)
    Q.put(k)
    unvisited.remove(k)
    G.add_node(k)
    print("root:",k)
    last = len(unvisited)
    while(not Q.empty()):
        k = Q.get()
        if(last-len(unvisited)>1000):
            last = len(unvisited)
            print("current: ",len(unvisited))
        kin_temp1 = kindata.loc[kindata['c_personid']==k,('c_kin_id','c_kin_code')]
        kin_temp2 = kindata.loc[kindata['c_kin_id']==k,('c_personid','c_kin_code')]
        for key,value in kin_temp1.iterrows():
            if(value[0] in unvisited):
                Q.put(value[0])
                unvisited.remove(value[0])
                G.add_node(value[0])
                G.add_edge(k,value[0],weight=value[1])
            else:
                if(not G.has_edge(value[0],k)):
                    G.add_edge(k,value[0])
        
        for key,value in kin_temp2.iterrows():
            if(value[0] in unvisited):
                Q.put(value[0])
                unvisited.remove(value[0])
                G.add_node(value[0])
                G.add_edge(value[0],k,weight=value[1])
            else:
                if(G.has_edge(k,value[0])):
                    pairs.append((k,value[0]))
                else:
                    G.add_edge(value[0],k,weight = value[1])
        
 
    print("New Graph")
    graphs.append(G)
'''         
nx.draw(G,pos=nx.shell_layout(G),arrows = False, with_labels=True,node_color='w',font_color='b')
plt.show()
'''
    
num_node = []
num_edge = []
for g in graphs:
    num_node.append(g.nodes())
    num_edge.append(g.edges())