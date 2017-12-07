#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
Created on Tue Oct 17 08:02:58 2017

@author: mac
"""

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import queue 

kindata = pd.DataFrame.from_csv('KIN_DATA.csv')
biogmain = pd.DataFrame.from_csv('BIOG_MAIN.csv')
kindatacode = pd.DataFrame.from_csv('KINSHIP_CODES.csv')
allkindatacode = set(kindatacode['c_kincode'])
#simplekindatacode = (set(kindatacode.loc[kindatacode['c_rank']<=30,'c_kincode'])-set(kindatacode.loc[kindatacode['c_rank']<=12,'c_kincode']))|set(kindatacode.loc[kindatacode['c_rank']<=8,'c_kincode'])
#simplekindatacode = simplekindatacode - set([136,159,162,381,382,438,150,151,170,341,342])
m = kindata.shape[0]
people = set(kindata['c_personid'])
n = len(people)
unvisited = people - set([0])
kindata.index=range(m)
graphs = []
pairs = []
crash = 0
gen = np.zeros(m+1,np.int8)-1000

while(len(unvisited)>0):
    k = min(unvisited)
    gen[k]=0
    MinGen=0
    G = nx.MultiDiGraph()
    Q = queue.Queue(maxsize=0)
    Q.put(k)
    Q0 = queue.Queue(maxsize=0)
    Q0.put(k)
    unvisited.remove(k)
    G.add_node(k)
    print("root:",k)
    last = len(unvisited)
    while(not Q.empty()):
        k = Q.get()
        if(last-len(unvisited)>1000):
            last = len(unvisited)
            print("current: ",len(unvisited))
        #kin_temp1 = kindata.loc[kindata['c_personid','c_kin_code'] in (k,simplekindatacode),('c_kin_id','c_kin_code')]
        kin_temp1 = kindata.loc[kindata['c_personid']==k,('c_kin_id','c_kin_code')]
        #kin_temp2 = kindata.loc[kindata['c_kin_id']==k,('c_person_id','c_kin_code')]
        #kin_temp1 = kin_temp1.loc[kin_temp1['c_kin_code'] in simplekindatacode,]
        for key,value in kin_temp1.iterrows():
            #if key in simplekindatacode:
            if value[1] in allkindatacode:
                if len(kindatacode.loc[value[1],'c_kinrel'])<=3:
                    if(value[0] in unvisited):
                        Q.put(value[0])
                        Q0.put(value[0])
                        if set("WMCHAP") & set(kindatacode.loc[value[1],'c_kinrel'])!=set():
                            gen[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                        else:
                            gen[value[0]]=0
                        unvisited.remove(value[0])
                        G.add_node(value[0])
                        G.add_edge(k,value[0])#,weight=value[1])
                    else:
                        if(not G.has_edge(value[0],k)):
                            G.add_edge(k,value[0])
                        if set("WMHCAP") & set(kindatacode.loc[value[1],'c_kinrel'])!=set():
                            if gen[value[0]]!=-1000:
                                if gen[k]+kindatacode.loc[value[1],"代差"]!=gen[value[0]]:
                                    print('冲突')
                                    crash = crash + 1
                                gen[value[0]]=max(gen[k]+kindatacode.loc[value[1],'代差'],gen[value[0]])
    while(not Q0.empty()):
        k = Q0.get()
        if (gen[k]<MinGen):
            MinGen = gen[k]
        Q.put(k)
    while(not Q.empty()):
        k=Q.get()
        gen[k]=gen[k]-MinGen
        #for key,value in kin_temp2.iterrows():
        #    if(value[0] in unvisited):
        #        Q.put(value[0])
        #        unvisited.remove(value[0])
        #        G.add_node(value[0])
        #        G.add_edge(value[0],k,weight=value[1])
        #    else:
        #        if(G.has_edge(k,value[0])):
        #            pairs.append((k,value[0]))
        #        else:
        #            G.add_edge(value[0],k,weight = value[1])
 
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