# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 21:50:53 2017

@author: SONY
"""


import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import Queue 
import codecs

kindata = pd.DataFrame.from_csv('kindata.csv')
biogmain = pd.DataFrame.from_csv('bio_main.csv')
kindatacode = pd.DataFrame.from_csv('kinship_codes.csv')
allkindatacode = set(kindatacode['c_kincode'])
#simplekindatacode = (set(kindatacode.loc[kindatacode['c_rank']<=30,'c_kincode'])-set(kindatacode.loc[kindatacode['c_rank']<=12,'c_kincode']))|set(kindatacode.loc[kindatacode['c_rank']<=8,'c_kincode'])
#simplekindatacode = simplekindatacode - set([136,159,162,381,382,438,150,151,170,341,342])
m = kindata.shape[0]
biogmain.index = biogmain["c_personid"].tolist()
kindatacode.index = kindatacode["c_kincode"].tolist()
people = set(kindata['c_personid']) & set(biogmain["c_personid"])
n = len(people)
unvisited = people - set([0])
kindata.index=range(m)
graphs = []
pairs = []
crash = 0
gen = np.zeros(m+1,np.int8)-1000
gen_pojia = np.zeros(m+1,np.int8)-1000
FemalePojia = np.zeros(m+1,np.int8)
status = np.zeros(m+1,np.int8)
cntwrongrel = 0
Alphabet = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

while(len(unvisited)>0):
    k = min(unvisited)
    gen[k]=0
    MinGen=0
    G = nx.MultiDiGraph()
    Q = Queue.Queue(maxsize=0)
    Q.put(k)
    Q0 = Queue.Queue(maxsize=0)
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
        if not biogmain.loc[k,'c_female']:
            for key,value in kin_temp1.iterrows():
                if (value[0] not in biogmain.index):
                    cntwrongrel += 1
                    continue;
                #if key in simplekindatacode:
                if value[1] in allkindatacode:
                    #if len(kindatacode.loc[value[1],'c_kinrel'])<=10:#这种情况下，发生了30197次crash,最大代数为608
                    if not biogmain.loc[value[0],'c_female']:
                        if(value[0] in unvisited):
                            if set("WMCHAP") & set(kindatacode.loc[value[1],'c_kinrel'])==set():
                                gen[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                            else:
                                continue
                            Q.put(value[0])
                            Q0.put(value[0])
                            unvisited.remove(value[0])
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])#,weight=value[1])
                        else:
                            if set("WMHCAP") & set(kindatacode.loc[value[1],'c_kinrel'])==set():
                                if(not G.has_edge(k,value[0])):
                                    G.add_edge(k,value[0],weight=value[1])
                                if gen[value[0]]!=-1000:
                                    if gen[k]+kindatacode.loc[value[1],"代差"]!=gen[value[0]]:
                                        print('冲突')
                                        crash = crash + 1
                                    p=gen[k]+kindatacode.loc[value[1],'代差']
                                    gen[value[0]]=max(p,gen[value[0]])
                    else:
                        if (Alphabet & set(kindatacode.loc[value[1],'c_kinrel'])).difference(set("MWC"))==set():
                            gen_pojia[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                            FemalePojia[value[0]]=k
                            status[value[0]]=status[value[0]]+2
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                            if value[0] in unvisited:
                                unvisited.remove(value[0])
                                Q0.put(value[0])
                            if status[value[0]]==2:
                                Q.put(value[0])
                        if (Alphabet & set(kindatacode.loc[value[1],'c_kinrel'])).difference(set("DZ"))==set():
                            gen[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                            status[value[0]]=status[value[0]]+1
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                            if value[0] in unvisited:
                                unvisited.remove(value[0])
                                Q0.put(value[0])
                            if status[value[0]]==2:
                                Q.put(value[0])
        else:
            if status[k]<=1:
                ForbidList={"H","S","D","P","A","G-","W"}
            elif status[k]==2:
                ForbidList={"B","Z","G-","F","M","K","P"}
                tmp=gen[k]
                gen[k]=gen_pojia[k]
            else:
                ForbidList={"P"}
            for key,value in kin_temp1.iterrows():
                if value[0]==k:
                    continue
                if value[0] not in biogmain.index:
                    cntwrongrel+=1
                    continue
                #if key in simplekindatacode:
                if value[1] in allkindatacode:
                    if not biogmain.loc[value[0],'c_female']:
                        if(value[0] in unvisited):
                            if ForbidList & set(kindatacode.loc[value[1],'c_kinrel'])==set():
                                gen[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                            else:
                                continue
                            Q.put(value[0])
                            Q0.put(value[0])
                            unvisited.remove(value[0])
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])#,weight=value[1])
                        else:
                            if ForbidList & set(kindatacode.loc[value[1],'c_kinrel'])==set():
                                if(not G.has_edge(k,value[0])):
                                    G.add_edge(k,value[0],weight=value[1])
                                if gen[value[0]]!=-1000:
                                    if gen[k]+kindatacode.loc[value[1],"代差"]!=gen[value[0]]:
                                        print('冲突')
                                        crash = crash + 1
                                    p=gen[k]+kindatacode.loc[value[1],'代差']
                                    gen[value[0]]=max(p,gen[value[0]])
                    else:
                        if (Alphabet & set(kindatacode.loc[value[1],'c_kinrel'])).difference(set("MWC"))==set():
                            gen_pojia[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                            FemalePojia[value[0]]=k
                            status[value[0]]=status[value[0]]+2
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                            if value[0] in unvisited:
                                unvisited.remove(value[0])
                                Q0.put(value[0])
                            if status[value[0]]==2:
                                Q.put(value[0])
                        if (Alphabet & set(kindatacode.loc[value[1],'c_kinrel'])).difference(set("DZ"))==set():
                            gen[value[0]]=gen[k]+kindatacode.loc[value[1],'代差']
                            status[value[0]]=status[value[0]]+1
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                            if value[0] in unvisited:
                                unvisited.remove(value[0])
                                Q0.put(value[0])
                            if status[value[0]]==1:
                                Q.put(value[0])
            if status[k]==2:
                gen_pojia[k]=gen[k]
                gen[k]=tmp
            status[k]==0
    for k in G.nodes():
        if G.has_edge(FemalePojia[k],k):
            tmp=gen[k]
            gen[k]=gen_pojia[k]
            gen_pojia[k]=tmp
    while(not Q0.empty()):
        k = Q0.get()
        if (gen[k]<MinGen):
            MinGen = gen[k]
        Q.put(k)
    while(not Q.empty()):
        k=Q.get()
        gen[k]=gen[k]-MinGen
    for k in G.nodes():
        if G.has_edge(FemalePojia[k],k):
            tmp=gen[k]
            gen[k]=gen_pojia[k]
            gen_pojia[k]=tmp
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
    print(G.edges())
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
    if 29239 in g.nodes():
        TMZ = g

gen0 = gen
def genn(i):
    return gen0[i]
def gennn(i):
    return gen0[i[0]]
kindatacode.index = kindatacode["c_kincode"].tolist()

GraphVizPrint = ["digraph TMZ{",'node [shape=record,fontname="Fangsong"];','edge[fontname="Fangsong"]']
maxdepth = max(gen[TMZ.nodes()])
Nodes = TMZ.nodes()
for node in Nodes:
    if TMZ.has_edge(FemalePojia[node],node):
        gen0[node]=gen_pojia[node]
Nodes = sorted(Nodes,key=genn)
i = 0
for j in range(0,maxdepth+1):
    GraphVizPrint.append("{")
    GraphVizPrint.append('rank="same";')
    i0=i
    while gen[Nodes[i]]==j:
        if biogmain.loc[Nodes[i],"c_female"]:
            GraphVizPrint.append('%d[label="(%s)%d",shape=circle];'% (Nodes[i],biogmain.loc[Nodes[i],"c_name_chn"],gen0[Nodes[i]]))
        else:
            GraphVizPrint.append('%d[label="(%s)%d"];'% (Nodes[i],biogmain.loc[Nodes[i],"c_name_chn"],gen0[Nodes[i]]))
        i = i + 1
        if i==len(Nodes):
            break
    if i0==i:
        GraphVizPrint.pop()
        GraphVizPrint.pop()
    else:
        GraphVizPrint.append("}")
    #print(biogmain.loc[name,"c_name_chn"])
    #if biogmain.loc[name,"c_female"]:
    #    GraphVizPrint.append('%s [shape="circle"]'% biogmain.loc[name,"c_name_chn"])
    #else:
    #    GraphVizPrint.append(biogmain.loc[name,"c_name"])
Edges = sorted(TMZ.edges(),key=gennn,reverse=True)
for edge in Edges:
    while Edges.count((edge[1],edge[0]))>0:
        Edges.remove((edge[1],edge[0]))
    GraphVizPrint.append('%d -> %d[label="%s"];'% (edge[0],edge[1],kindatacode.loc[TMZ[edge[0]][edge[1]][0]['weight'],"c_kinrel_chn"]))
GraphVizPrint.append("}")
f = codecs.open("map108.dot","w",encoding="utf8")
for sentense in GraphVizPrint:
    f.write(sentense)
    f.write("\n")
f.close()
        