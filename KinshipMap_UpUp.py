# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 13:29:43 2017 This is a copy for Python 3.x
@author: Jianqiu Lu, Hanyu Zhang
@email: lujq96@gmail.com,zhanghy1996@gmail.com
"""
import pandas as pd
import networkx as nx
import numpy as np
import queue
import codecs
import re


###############################################################################
# readData: input the file name of three data files: kindata, biogmain and 
# kincodefile and read them into the program and transform to pandas dataframe
def readData():
    KinDataFile = input("Filename of kindata(*.csv): ")
    BioMainFile = input("Filename of biography(*.csv): ")
    KinCodeFile = input("Filename of kindatacode(*.csv): ")
    kindata = pd.DataFrame.from_csv(KinDataFile)
    biogmain = pd.DataFrame.from_csv(BioMainFile)
    kindatacode = pd.DataFrame.from_csv(KinCodeFile)
    reslist = [kindata,biogmain,kindatacode]
    return(reslist)

###############################################################################
# preProcess: read the pandas dataframe file and do basis pre processing of the
# data
def preProcess(reslist):
    kindata = reslist[0]
    biogmain = reslist[1]
    kindatacode = reslist[2]
    allkindatacode = set(kindatacode['c_kincode'])-{0,-1}
    biogmain.index = biogmain["c_personid"].tolist()
    kindatacode.index = kindatacode["c_kincode"].tolist()
    people = set(kindata['c_personid']) & set(biogmain["c_personid"])
    n = len(people)
    kindata.index = kindata["c_kin_id"].tolist()
    m = max(kindata.index)
    datalist = [kindata,biogmain,kindatacode,allkindatacode,people,n,m]
    return datalist

###############################################################################
# readFile: read data from a txt file and construct the graphs list
def readFile(inGraphFile):
    if(not inGraphFile):
        inGraphFile = input('Input Graph File Name: ')
    with open(inGraphFile,'r') as f:
        lines = f.readlines()
    graphs = []
    for k in range(len(lines)/3):
        G = nx.MultiDiGraph()
        node = [int(x) for x in re.findall(r'\d+',lines[1+3*k])]
        G.add_nodes(node)
        edge = [int(x) for x in re.findall(r'\d+',lines[2+3*k])]
        for l in range(len(edge)/3):
            G.add_edge(edge[3*l],edge[3*l+1],weight = edge[3*l+2])
        graphs.append(G)
    return graphs
    
###############################################################################
# Divide: Transform the datafiles into compact components of the network. Using
# specific rules to divide large graphs to small graphs and save the result into
# a txt file named as OutPutFile.
def Divide():
    reslist = readData()
    datalist = preProcess(reslist)
    OutPutFile = input("Output Filename: ")
    kindata = datalist[0]
    biogmain = datalist[1]
    kindatacode = datalist[2]
    allkindatacode = datalist[3]
    people = datalist[4]
    n = datalist[5]
    unvisited = people - set([0])
    m = datalist[6]
    
    graphs = []
    pairs = []
    roots = []
    crash = 0
        
    status = np.zeros(m+1,np.int32)
    cnterrid = 0
    cnterrrel = 0
    badrel = 0
    Alphabet = set("QWERTYUIOPASDFGHJKLZXCVBNM")
    
    while(len(unvisited)>0):
        k = min(unvisited)
        while biogmain.loc[k,"c_female"] and len(unvisited)>0:
            unvisited.remove(k)
            k = min(unvisited)
        G = nx.MultiDiGraph()
        Q = queue.Queue(maxsize=0)
        Q.put(k)
        unvisited.remove(k)
        G.add_node(k)
        print("root:",k)
        roots.append(k)
        last = len(unvisited)
        while(not Q.empty()):
            k = Q.get()
            if (last-len(unvisited)>1000): #防止一个家族过大程序假死
                last = len(unvisited)
                print("current:",len(unvisited))
            kin4k = kindata.loc[kindata["c_personid"]==k,("c_kin_id","c_kin_code")]
            for key,value in kin4k.iterrows():
                if value[0]==k:
                    continue;
                if (value[0] not in biogmain.index): #人物实际没有出现
                    cnterrid += 1
                    continue;
                if value[1] not in allkindatacode: #关系代码找不到
                    cnterrrel += 1
                    continue;
                if abs(kindatacode.loc[value[1],'代差'])>=90:
                    badrel += 1
                    continue
                '''
                k为男/女性时的亲属加入
                '''
                if (not biogmain.loc[k,'c_female']):
                    if not biogmain.loc[value[0],'c_female']: #亲属同样为男性
                        if set("WMCHAPZ") & set(kindatacode.loc[value[1],'c_kinrel'])!=set(): 
                            continue #二者间的关系不存在联姻
                        if kindatacode.loc[value[1],'c_kinrel'][0]=='D' and  kindatacode.loc[value[1],'代差']<-1:
                            continue #女儿的后代不应计入家谱
                        if (value[0] in unvisited): #未访问过的节点
                            Q.put(value[0])
                            unvisited.remove(value[0])
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                        else: #已访问/出现过的节点
                            if not G.has_edge(k,value[0]):
                                G.add_edge(k,value[0],weight=value[1])
                    else: #女性亲属的情况
                        UsefulRel = Alphabet & set(kindatacode.loc[value[1],'c_kinrel'])
                        if len(UsefulRel)>1:
                            continue
                        if UsefulRel.difference(set("MWCDZ"))==set():#仅考虑五种简单关系之一
                            if status[value[0]]==0:
                                Q.put(value[0])
                            if UsefulRel.difference(set("MWC"))==set():#婆家
                                if status[value[0]]!=2:
                                    status[value[0]]=status[value[0]]+2
                            else: #娘家
                                if status[value[0]]!=1:
                                    status[value[0]]=status[value[0]]+1
                            if status[value[0]]==3:
                                Q.put(value[0])
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                            if value[0] in unvisited:
                                unvisited.remove(value[0])
                else: 
                    if status[k]==1:
                        ForbidList={"H","S","D","P","A","G-","W"} #娘家里不宜引入的关系，过于严格
                    elif status[k]==2:
                        ForbidList={"B","Z","G+","F","M","K","P"}
                    else:
                        ForbidList={"P"} #同时属于婆家和娘家的情形
                    if ForbidList & set(kindatacode.loc[value[1],'c_kinrel'])!=set():
                        continue
                    if not biogmain.loc[value[0],'c_female']: #加入男性亲属
                        if set("WMCHAPZ") & set(kindatacode.loc[value[1],'c_kinrel'])!=set(): 
                            continue #二者间的关系不存在联姻
                        if kindatacode.loc[value[1],'c_kinrel'][0]=='D' and  kindatacode.loc[value[1],'代差']<-1:
                            continue #女儿的后代不应计入家谱
                        if (value[0] in unvisited): #未访问过的节点
                            Q.put(value[0])
                            unvisited.remove(value[0])
                            G.add_node(value[0])
                            G.add_edge(k,value[0],weight=value[1])
                        else: #已访问/出现过的节点
                            if not G.has_edge(k,value[0]):
                                G.add_edge(k,value[0],weight=value[1])
                    else: #女性亲属的情况
                        UsefulRel = Alphabet & set(kindatacode.loc[value[1],'c_kinrel'])
                        if len(UsefulRel)>1:
                            continue
                        if UsefulRel.difference(set("MDZ"))==set():#仅考虑五种简单关系之一
                            if status[value[0]]==0:
                                Q.put(value[0])
                            if UsefulRel.difference(set("M"))==set():#婆家
                                if status[value[0]]!=2:
                                    status[value[0]]=status[value[0]]+2
                            else: #娘家
                                if status[value[0]]!=1:
                                    status[value[0]]=status[value[0]]+1
                            if status[value[0]]==3:
                                Q.put(value[0])
                            if not G.has_node(value[0]):
                                G.add_node(value[0])
                                G.add_edge(k,value[0],weight=value[1])
                            elif not G.has_edge(k,value[0]):
                                G.add_edge(k,value[0],weight=value[1])
                            if value[0] in unvisited:
                                unvisited.remove(value[0])
        for k in G.nodes():
            status[k]=0
        #print("New Graph")
        #print(G.edges())
        graphs.append(G)
    
    # save the results
    f = codecs.open(OutPutFile+".cut","w",encoding="utf8")
    for g in range(len(graphs)):
        f.write("Family%d\n"%g)
        f.write(str(graphs[g].nodes()))
        f.write("\n")
        Edge = []
        for k in graphs[g].nodes():
            for t in graphs[g][k]:
                Edge.append(str((k,t,graphs[g][k][t][0]['weight'])))
        for s in Edge:
            f.write(s)
            f.write(" ")
        f.write("\n")
    f.write("#")
    f.close()
    graphs = Combine(graphs,m,biogmain)
    return graphs

###############################################################################
# Merge: given two graphs list file and merge them into one single larger graph
# list
def Merge():
    BioMainFile = input("Filename of biography(*.csv): ")
    biogmain = pd.DataFrame.from_csv(BioMainFile) 
    graphs1 = readFile()
    graphs2 = readFile()
    
    m1 = 0
    m2 = 0
    for g in graphs2:
        graphs1.append(g)
        mt = max(g.nodes())
        if mt > m2:
            m2 = mt
    graphs = graphs1
    for g in graphs1:
        mt = max(g.nodes())
        if mt > m1:
            m1 = mt
    m = max([m1,m2])
    graphs = Combine(graphs,m,biogmain)
    return graphs

###############################################################################
# Combine: given a graphs file and the corresponding parameter m (largest index
# of nodes in all graphs) and eliminate repetition of same male family members 
# in different families aka different connected components
def Combine(graphs,m,biogmain):
    first = np.zeros(m+1,np.int32)-1
    f = codecs.open("Result1.txt","w",encoding="utf8")
    cnt = 0
    for g in range(len(graphs)):
        comb = []
        for k in graphs[g].nodes():
            if not biogmain.loc[k,'c_female']:
                if first[k]!=-1:
                    comb.append(first[k])
                else:
                    first[k]=cnt
        if comb!=[]:
            comb.append(cnt)
            combto = min(comb)
            G = nx.MultiDiGraph()
            for k in comb:
                for n1 in graphs[k].nodes():
                    for n2 in graphs[k][n1]:
                        if not G.has_edge(n1,n2):
                            G.add_edge(n1,n2,weight=graphs[k][n1][n2][0]['weight'])
                graphs[k]=nx.MultiDiGraph()
            graphs[combto]=G
            for n in G.nodes():
                first[n]=combto
        cnt += 1
    return graphs

###############################################################################
# ForbidList: generate the forbidlist for different status of female members
def ForbidList(k):
    if k==1:
        return {"H","S","D","P","A","G-","W"}
    if k==2:
        return {"B","Z","G+","F","M","K","P"}
    return {"P"}

###############################################################################
# Generate: function to calculate generations of a family member, deal with crashes
# and generate graphViz code to visualize family size.
def Generate():
    reslist = readData()
    datalist = preProcess(reslist)
    kindata = datalist[0]
    biogmain = datalist[1]
    kindatacode = datalist[2]
    allkindatacode = datalist[3]
    people = datalist[4]
    n = datalist[5]
    m = datalist[6]
    graphs = pickle.load('graphs.pk','')
    
    not0 = 0
    num_node = []
    num_edge = []
    for g in graphs:
        num_node.append(g.nodes())
        Edge = []
        for k in g.nodes():
            for t in g[k]:
                Edge.append((k,t,g[k][t][0]['weight']))
        num_edge.append(Edge)
        if len(g.nodes())>9000:
            TMZ = g
        if len(g.nodes())>0:
            not0+=1
            
    gen = np.zeros(m+1,np.int32)-1000
    gen_pj = np.zeros(m+1,np.int32)-1000
    status = np.zeros(m+1,np.int32)
    PjFlag = np.zeros(m+1,np.int32)
    Nodes = TMZ.nodes()
    gen[min(Nodes)]=0
    gen_pj[min(Nodes)]=0
    unvisited = set(Nodes)-{min(Nodes)}
    cnt = 0
    Q = queue.Queue(maxsize=0)
    Q.put(min(Nodes))
    while(not Q.empty()):
        k = Q.get()
        if (not biogmain.loc[k,'c_female']):
            for val in TMZ[k]:
                if val in unvisited:
                    Q.put(val)
                    unvisited.remove(val)
                if (not biogmain.loc[val,'c_female']):
                    gen[val] = gen[k]+ kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                else:
                    UsefulRel = set(kindatacode.loc[TMZ[k][val][0]['weight'],'c_kinrel']) & Alphabet
                    if UsefulRel.difference(set("MWC"))==set():
                        gen_pj[val] = gen[k]+ kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                        if status[val]!=2:
                            status[val]=status[val]+2
                    else:
                        gen[val] = gen[k]+ kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                        if status[val]!=1:
                            status[val]=status[val]+1
            for val in TMZ.in_edges(k):
                if (not biogmain.loc[val[0],'c_female']):
                    gen[val[0]] = gen[k] - kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                else:
                    UsefulRel = set(kindatacode.loc[TMZ[val[0]][k][0]['weight'],'c_kinrel']) & Alphabet
                    if UsefulRel.difference(set("DSH"))==set():
                        gen_pj[val[0]] = gen[k]- kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                        if status[val[0]]!=2:
                            status[val[0]]=status[val[0]]+2
                    else:
                        gen[val[0]] = gen[k]- kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                        if status[val[0]]!=1:
                            status[val[0]]=status[val[0]]+1
                if val[0] in unvisited:
                    Q.put(val[0])
                    unvisited.remove(val[0])
        else:
            Flag = False
            Flag2 = False
            if status[k]==1:
                gk=gen[k]
            elif status[k]==2:
                gk=gen_pj[k]
            else:
                Flag2 = True
            for val in TMZ[k]:
                if ForbidList(status[k]) & set(kindatacode.loc[TMZ[k][val][0]['weight'],'c_kinrel'])!=set():
                    Flag = True
                    continue
                if (val in unvisited): #未访问过的节点
                    Q.put(val)
                    unvisited.remove(val)
                if not biogmain.loc[val,'c_female']: #加入男性亲属
                    if not Flag2:
                        gen[val] = gk + kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                    else:
                        if ForbidList(1) & set(kindatacode.loc[TMZ[k][val][0]['weight'],'c_kinrel'])!=set():
                            gen[val] = gen[k] + kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                        else:
                            gen[val] = gen_pj[k] + kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                else: #女性亲属的情况
                    UsefulRel = set(kindatacode.loc[TMZ[k][val][0]['weight'],'c_kinrel']) & Alphabet
                    if UsefulRel==set("M"):
                        gen_pj[val] = gen[k]+ kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                        if status[val]!=2:
                            status[val]=status[val]+2
                    elif UsefulRel==set("D"):
                        gen[val] = gen_pj[k] + kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                        if status[val]!=1:
                            status[val]=status[val]+1
                    else:
                        gen[val] = gen[k] + kindatacode.loc[TMZ[k][val][0]['weight'],'代差']
                        if status[val]!=1:
                            status[val]=status[val]+1
            for val in TMZ.in_edges(k):
                UsefulRel = set(kindatacode.loc[TMZ[val[0]][k][0]['weight'],'c_kinrel']) & Alphabet
                if not biogmain.loc[val[0],'c_female']: #加入男性亲属
                    if UsefulRel.difference(set("MWC"))==set():
                        if status[k]==1:
                            Flag = True
                            continue
                        else:
                            gen[val[0]] = gen_pj[k] - kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                    else:
                        if status[k]==2:
                            Flag = True
                            continue
                        else:
                            gen[val[0]] = gen[k] - kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                else: #女性亲属的情况
                    if UsefulRel==set("M"):
                        if status[k]==1:
                            Flag = True
                            continue
                        gen[val[0]] = gen_pj[k]- kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                        if status[val[0]]!=1:
                            status[val[0]]=status[val[0]]+1
                    elif status[k]==2:
                        Flag = True
                        continue
                    elif UsefulRel==set("D"):
                        gen_pj[val[0]] = gen[k] - kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                        if status[val[0]]!=2:
                            status[val[0]]=status[val[0]]+2
                    else:
                        gen[val[0]] = gen[k] - kindatacode.loc[TMZ[val[0]][k][0]['weight'],'代差']
                        if status[val[0]]!=1:
                            status[val[0]]=status[val[0]]+1
                if (val[0] in unvisited): #未访问过的节点
                    Q.put(val[0])
                    unvisited.remove(val[0])
            #if Flag:
                #Q.put(k)
                #print(biogmain.loc[k,"c_name_chn"])
                #input("")
        
    gen0 = gen
    def genn(i):
        return gen0[i]
    def gennn(i):
        return gen0[i[0]]
    
    GraphVizPrint = ["digraph TMZ{",'rankdir="LR";','ranksep="3 equally"', 'node [shape=record,fontname="Fangsong"];','edge[fontname="Fangsong"]']
    Nodes = TMZ.nodes()
    for node in Nodes:
        gen0[node]=max(gen_pj[node],gen[node])
    maxdepth = max(gen0[Nodes])
    mindepth = min(gen0[Nodes])
    Nodes = sorted(Nodes,key=genn,reverse=True)
    i = 0
    for j in sorted(range(mindepth,maxdepth+1),reverse=True):
        GraphVizPrint.append("{")
        GraphVizPrint.append('rank="same";')
        i0=i
        while gen0[Nodes[i]]==j:
            if biogmain.loc[Nodes[i],"c_female"]:
                GraphVizPrint.append('%d[label="(%s)%d",style="filled", fillcolor="red"];'% (Nodes[i],biogmain.loc[Nodes[i],"c_name_chn"],gen0[Nodes[i]]))
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
    f = codecs.open("map1203.dot","w",encoding="utf8")
    for sentense in GraphVizPrint:
        f.write(sentense)
        f.write("\n")
    f.close()


print("CBDB To Kinship Map\n")
print("1. Divide\n")
print("2. Merge two graphs files\n")
print("3. Generate Graphviz Code\n")
print("0. exit\n")
while True:
    S = input("Please Choose: ")
    if S=="1":
        Divide()
    elif S=="2":
        Merge()
    elif S=="3":
        Generate()
    elif S=="0":
        break
    else:
        input("Wrong Input! Please Choose:")