import datetime
import json
import csv
import sys

import dateutil
import matplotlib
import matplotlib.pyplot as plt
import numpy
import pandas

from ConceptNode import emptyNode

CONFIGFILENAME = "gis_rs_v2_concept_id_name_export.csv"
LEARNINGPATHFILENAME = "learningPaths.json"

conceptNames = {}
learningpaths = {}
def init(fileName):
    with open(fileName) as f:
        lines = csv.reader(f, delimiter=";")
        for x, y in lines:
            conceptNames[x] = y

def datetime_parser(dct):
    for k, v in dct.items():
        try:
            dct[k] = dateutil.parser.parse(v)
        except:
            pass
    return dct

def listAdd(list,add):
    if len(list) == 0:
        list = add
        return add
    else:
        for i in range(len(list)):
            list[i] += add[i]
    return list


def hitsPerDay(nodes=None, nodeId=None,max_value=None):
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    if nodeId is None:
        nodeId = input("what is the id of the concept you would like to analise?\n")
    days = []
    conceptHitss = []
    userHitss = []

    for day in sorted(nodes[str(nodeId)]["hits per day"].keys()):
        days.append(day)
        conceptHitss.append(nodes[str(nodeId)]["hits per day"][day])
        userHitss.append(len(nodes[str(nodeId)]["users per day"][day]))
    n_groups = len(days)

    # create plot
    fig, ax = plt.subplots()
    index = numpy.arange(n_groups)
    bar_width = 0.42
    opacity = 0.9

    rects1 = plt.bar(index, conceptHitss, bar_width,
                     alpha=opacity,
                     color='b',
                     label='concept visits')

    rects2 = plt.bar(index + bar_width, userHitss, bar_width,
                     alpha=opacity,
                     color='r',
                     label='users')

    plt.xlabel('day')
    plt.ylabel('visits')
    plt.title('concept ' + str(nodeId) + ' visits per day')

    if max_value:
        axes = plt.gca()
        axes.set_ylim(0, max_value)
    plt.xticks(index + bar_width, days)
    plt.legend()

    plt.tight_layout()

    ax.grid(b=True, which='major', color='k', linewidth=0.5)
    plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')
    filename = "outputs/concept" + str(nodeId) + "Visits" + str(nodeId) + ".png"
    plt.savefig(filename)
    plt.close(fig)

# ToDo change these to data-exports for chart.js

def usersPerDayPerLearningPath(pathId=None, nodes=None, settings=None,
                              max_value=False, logarithmic_scale=False,
                              startDate=None, endDate=None, days=None):
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    if pathId is None:
        pathId = input("what is the id of the learning path you would like to analise?\n")
    if settings is None:
        settings = {}
        # with open("configurationFiles/learningPaths.json") as paths:
        #     settings['learningpaths'] = json.load(paths, object_hook=datetime_parser)
        settings['learningpaths'] = {}
    path = settings["learningpaths"][pathId]["list"]
    startOfPath = settings["learningpaths"][pathId]["starting time"]

    while startDate is None and days is None:
        try:
            startDate = dateutil.parser.parse(input("from which date would you like the graph to start?(yyyy-mm-dd)")).date()
        except:
            continue
    while endDate is None and days is None:
        try:
            endDate = dateutil.parser.parse(input("at which date would you like the graph to end?(yyyy-mm-dd)")).date()
        except:
            continue
    if days is None:
        pandaRange = pandas.date_range(startDate, endDate).tolist()
        days = [x.date() for x in pandaRange]
    else:
        days = days.copy()

    n_groups = len(days)
    fig, ax = plt.subplots()
    index = numpy.arange(n_groups)
    bar_width = 0.42
    opacity = 0.9

    data = []
    for i in range(3):
        data.append([])

    indexStart = 0
    increment = True
    overalUsers={}
    for day in days:
        dayUsers={}
        for conceptId in path:
            conceptId = str(conceptId)
            try:
                node = nodes[conceptId]
                dayUsers.update(node['users per day'][str(day)])
            except:
                continue
        oldUsers=len(list(filter(lambda element: element in overalUsers,dayUsers.keys())))
        data[0].append(oldUsers)
        data[1].append(len(dayUsers)-oldUsers)
        overalUsers.update(dayUsers)


        if day == startOfPath.date():
            data[2].append(2)
            increment = False
        else:
            data[2].append(0)
            indexStart += increment

    if indexStart < len(days): days[indexStart] = str(days[indexStart]) + " LP"

    p = []
    bottom = [0] * len(days)
    for i in range(2):
        p.append(plt.bar(index, data[i], bar_width, label=["old users","new users"][i], bottom=bottom))
        listAdd(bottom, data[i])
    p.append(plt.bar(index, data[2], bar_width, label="start of path", color="k", bottom=bottom))

    plt.xlabel('day')
    plt.ylabel('users')
    plt.title('path ' + str(pathId) + ': users per day')
    if logarithmic_scale:
        plt.yscale('log')

    if max_value:
        axes = plt.gca()
        axes.set_ylim(0, max_value)
    plt.xticks(index, days)

    # for i in range(len(days)):
    #     plt.text(x=i - 0.5, y=data[0][i] - 0.1, s=data[0][i], size=6)

    plt.legend()

    ax.grid(b=True, which='major', color='k', linewidth=0.45)
    plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')
    filename = "outputs/pathUsers" + str(pathId) + ".png"
    plt.savefig(filename)
    plt.close(fig)



def hitsPerDayPerLearningPath(pathId=None, nodes=None, settings=None,
                              max_value=False, logarithmic_scale=False,
                              startDate=None, endDate=None, days=None):
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    if pathId is None:
        pathId = input("what is the id of the learning path you would like to analise?\n")
    if settings is None:
        settings = {}
        # with open("configurationFiles/learningPaths.json") as paths:
        #     settings['learningpaths'] = json.load(paths, object_hook=datetime_parser)
        settings["learningpaths"] = {}
    path = settings["learningpaths"][pathId]["list"]
    startOfPath= settings["learningpaths"][pathId]["starting time"]

    if startDate is None:
        try:
            startDate = settings['period']['startDate']
            endDate = settings['period']['endDate']
        except:
            startDate = None
    while startDate is None:
        try:
            startDate = dateutil.parser.parse(input("from which date would you like the graph to start?(yyyy-mm-dd)")).date()
        except:
            continue
    while endDate is None:
        try:
            endDate = dateutil.parser.parse(input("at which date would you like the graph to end?(yyyy-mm-dd)")).date()
        except:
            continue
    if days is None:
        pandaRange = pandas.date_range(startDate, endDate).tolist()
        days = [x.date() for x in pandaRange]
    else:
        days = days.copy()

    n_groups = len(days)
    fig, ax = plt.subplots()
    index = numpy.arange(n_groups)
    bar_width = 0.42
    opacity = 0.9
    data = []
    for i in range (len(path)):
        data.append([])
    data.append([])  # this is for the start of learningpath marker
    indexStart=0
    increment=True
    for day in days:
        for i in range(len(path)):
            try:
                data[i].append(nodes[str(path[i])]["hits per day"][str(day)])
            except:
                data[i].append(0)
        if day == startOfPath.date():
            data[len(path)].append(5)
            increment=False
        else:
            data[len(path)].append(0)
            indexStart+=increment
    if indexStart < len(days) : days[indexStart]=str(days[indexStart]) + " LP"

    p = []
    bottom=[0]*len(days)
    for i in range(len(path)):
        p.append(plt.bar(index, data[i], bar_width, label=conceptNames[str(path[i])], bottom=bottom))
        listAdd(bottom,data[i])
    p.append(plt.bar(index, data[len(path)], bar_width, label="start of path", color="k", bottom=bottom))

    plt.xlabel('day')
    plt.ylabel('visits')
    plt.title('path ' + str(pathId) + ': visits per day')
    if logarithmic_scale:
        plt.yscale('log')

    if max_value:
        axes=plt.gca()
        axes.set_ylim(0,max_value)
    plt.xticks(index, days)

    # for i in range(len(days)):
    #     plt.text(x=i - 0.5, y=data[0][i] - 0.1, s=data[0][i], size=6)

    plt.legend()

    ax.grid(b=True, which='major', color='k', linewidth=0.45)
    plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')
    filename = "outputs/pathVisits" + str(pathId) + ".png"
    plt.savefig(filename)
    plt.close(fig)


def hitsPerDayPerUser(users, userId, nodes=None, settings=None,
                              max_value=False, logarithmic_scale=False,
                              startDate=None, endDate=None, days=None):  # based on hitsPerDayPerLearningpath
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    while userId is None:
        userId = input("what is the id of the user you would like to analise?\n")
    try:
        user = users[userId]
    except:
        print("user " + userId + " not found")

    if settings is None:
        settings = {}
        # with open("configurationFiles/learningPaths.json") as paths:
        #     settings['learningpaths'] = json.load(paths, object_hook=datetime_parser)
        settings["learningpaths"] = {}

    if startDate is None:
        try:
            startDate = settings['period']['startDate']
            endDate = settings['period']['endDate']
        except:
            startDate = None
    while startDate is None:
        try:
            startDate = dateutil.parser.parse(input("from which date would you like the graph to start?(yyyy-mm-dd)")).date()
        except:
            continue
    while endDate is None:
        try:
            endDate = dateutil.parser.parse(input("at which date would you like the graph to end?(yyyy-mm-dd)")).date()
        except:
            continue
    if days is None:
        pandaRange = pandas.date_range(startDate, endDate).tolist()
        days = [x.date() for x in pandaRange]
    else:
        days = days.copy()

    n_groups = len(days)
    fig, ax = plt.subplots()
    index = numpy.arange(n_groups)
    bar_width = 0.42
    opacity = 0.9
    data = []
    # We need to know how many total concepts were visited, so we can give all of them their own color
    concepts = {}
    dayConcepts={}
    try:
        (firstHit,_,_)=user["concepts"][len(user["concepts"])-1]
    except:
        firstHit = endDate
    for elem in user["concepts"]:
        ts, conId = elem['timestamp'], elem['conceptId']
        concepts[conId] = 0

        if ts.date() not in dayConcepts:
            dayConcepts[ts.date()] = {}

        if conId in dayConcepts[ts.date()]:
            dayConcepts[ts.date()][conId] += 1
        else:
            dayConcepts[ts.date()][conId] = 1
    conOrder = list(concepts.keys())

    for i in range(len(conOrder)):
        data.append([])

    # startOfPath = settings["period"]["endDate"]
    # indexStart = 0
    increment = True
    for day in days:
        for i in range(len(conOrder)):
            try:
                data[i].append(dayConcepts[day][conOrder[i]])
                concepts[conOrder[i]] += 1
            except:
                data[i].append(0)
    #     if day == startOfPath.date():
    #         data[len(conOrder)].append(5)
    #         increment=False
    #     else:
    #         data[len(conOrder)].append(0)
    #         indexStart+=increment
    # if indexStart < len(days) : days[indexStart]=str(days[indexStart]) + " LP"

    p = []
    bottom=[0]*len(days)

    for i in range(len(conOrder)):
        p.append(plt.bar(index, data[i], bar_width,
                         label=conceptNames[str(conOrder[i])] + str(concepts[conOrder[i]]), bottom=bottom))
        listAdd(bottom,data[i])
    # p.append(plt.bar(index, data[len(conOrder)], bar_width, label="start of path", color="k", bottom=bottom))

    plt.xlabel('day')
    plt.ylabel('visits')
    plt.title('user ' + str(userId) + ': visits per day')
    if logarithmic_scale:
        plt.yscale('log')

    if max_value:
        axes = plt.gca()
        axes.set_ylim(0,max_value)
    # plt.xticks(index, days)
    xtics=[]
    indices = []
    for x in range(0,len(days),10):
        xtics.append(days[x])
        indices.append(x)
    plt.xticks(indices,xtics)

    # for i in range(len(days)):
    #     plt.text(x=i - 0.5, y=data[0][i] - 0.1, s=data[0][i], size=6)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.grid(b=True, which='major', color='k', linewidth=0.45)
    # ax.text(3, 8, "first hit: " + str(firstHit), style='italic',
    #         bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')
    filename = "outputs/user" + str(userId) + "/hitsPerDay.png"
    plt.savefig(filename)
    filename = "outputs/hitsPerDay/" + str(userId) + ".png"
    plt.savefig(filename)
    plt.close(fig)
    print("done with user " + str(userId))
    return (firstHit,userId)



def generateSetOfPathVisits(pathId=None, nodes=None, settings=None,
                            max_value=False, logarithmic_scale=False,
                            startDate=None, endDate=None,metaData=None,users=False, debug=False, specificConcept=False):
    if metaData is None:
        try:
            with open("outputs/metaData.json", 'r') as metaFile:
                metaData = json.load(metaFile)
        except:
            if debug: print("no metaDataFile found, should be called metaData.json and should be in outputs")
    while pathId is None:
        try:
            pathId=[str(int(x)) for x in input("please enter the desired learning path(s), separated by ','\n").split(",")]
        except:
            continue
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    boolVal=(settings is not None) and 'period' in settings and 'startDate' in settings['period']
    startDate = settings['period']['startDate'].date() if boolVal else None
    endDate = settings['period']['endDate'].date() if boolVal else None
    while startDate is None:
        try:
            startDate = dateutil.parser.parse(input("from which date would you like the graphs to start?(yyyy-mm-dd)")).date()
        except:
            continue
    while endDate is None:
        try:
            endDate = dateutil.parser.parse(input("at which date would you like the graphs to end?(yyyy-mm-dd)")).date()
        except:
            continue
    pandaRange = pandas.date_range(startDate, endDate).tolist()
    days = [x.date() for x in pandaRange]
    if not max_value:
        if debug: print("calculating max_value")
        if not metaData is None:
            # we only want the relevant learningpaths
            if specificConcept:
                relevantDict = dict([(str(conceptId),nodes[str(conceptId)]['hits per day']) for conceptId in pathId])
            else:
                relevantDict=dict(filter(lambda given: given[0] in pathId, metaData["hitsPerLearningPathPerDay"].items()))
            # now we get the max value for each path
            if len(relevantDict) >0:
                maxes = [max(d.values()) for d in relevantDict.values()]
                # then we calculate the max over every path
                max_value=max(maxes)+10
            else: max_value=None

    if users:
        for path in pathId:
            usersPerDayPerLearningPath(path,nodes,settings,max_value,logarithmic_scale,startDate,endDate,days)

    else:
        if specificConcept:
            for concept in pathId:
                hitsPerDay(nodeId=concept, max_value=max_value)
        else:
            for path in pathId:
                hitsPerDayPerLearningPath(path,nodes,settings,max_value,logarithmic_scale,startDate,endDate,days)


def learningpathFlowthrough(learningpath, nodes=None, debug=False):
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    nodeCount = 1
    elements = []
    path = learningpath["list"]
    nodeIdConceptId={}
    for i in range(len(path)):
        concept = path[i]
        node = nodes[str(concept)] if str(concept) in nodes else {"id": 0, "nextNodes": {}, "hits":1}
        if str(concept) in nodeIdConceptId:
            placementNode = {"id": nodeIdConceptId[str(concept)], "visits": node["hits"], "isEmpty": False,
                             "name": conceptNames[str(concept)],
                             "lpIndex": i, "sizeOfNode": node["hits"]/100}
        else:
            placementNode = {"id": nodeCount, "visits": node["hits"],"isEmpty": False,
                             "name": conceptNames[str(concept)],
                             "lpIndex": i, "sizeOfNode": node["hits"]/100}
            nodeIdConceptId[str(concept)] = nodeCount
            nodeCount += 2
        templist = []
        nextNodes = dict(sorted(
            filter(lambda element: not element[0] in path, node["nextNodes"].items()),
            key=lambda element: element[1], reverse=True)[:5]
                         )
        for nextNode in nextNodes:
            if int(nextNode) in path:  # if we point to another node in the learning path, point to that original node
                if str(nextNode) not in nodeIdConceptId:
                    nodeIdConceptId[str(nextNode)] = nodeCount
                templist.append({
                    "target": nodeIdConceptId[str(nextNode)],
                    "relationName": str(node["nextNodes"][nextNode]),
                    "id": nodeCount + 1,
                    "conceptInPath": True
                })
                nodeCount += 2
            else:  # if we point to a random next node, we need to create that node as an empty, connectionless node.
                templist.append({
                    "target": nodeCount,
                    "relationName": str(node["nextNodes"][nextNode]),
                    "id": nodeCount+1
                })
                elements.append({
                    "numberOfLinks": 0,
                    "isEmpty": True,
                    "name": conceptNames[str(nextNode)],
                    "relations": [],
                    "id": nodeCount
                })
                nodeCount += 2
        if i < len(path)-1:
            if str(path[i+1]) not in nodeIdConceptId:
                nodeIdConceptId[str(path[i + 1])] = nodeCount
            templist.append({
                "target": nodeIdConceptId[str(path[i+1])],
                "relationName": str(node["nextNodes"][str(path[i+1])]) if str(path[i+1]) in node["nextNodes"] else 0,
                "id": nodeCount + 1
            })
            nodeCount += 2

        lengthList = len(templist)
        placementNode["relations"] = templist
        placementNode["numberOfLinks"] = lengthList
        elements.append(placementNode)

    if debug:
        print(learningpath["id"])

    with open("outputs/path"+str(learningpath["id"])+"Flowthrough.js", "w") as f:
        f.write("var jsonData=")
        json.dump(elements, f, default=str)
        f.write(";")


def allNodesFlowthrough(nodes=None, debug=False):
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)
    elements = {}
    nodeCount = 1

    for node in nodes:  # basic information on the node
        conceptNode = nodes[node]
        elementNode=None
        if str(node) in elements:
            elementNode = elements[node]
        else:
            elementNode = {"name": conceptNames[str(node)] if str(node) in conceptNames
            else "concept "+str(nextNode)+" name not found", "id": nodeCount}
            nodeCount+=1
        elementNode["isEmpty"] = False
        elementNode["sizeOfNode"] = conceptNode["hits"]/100
        elementNode["onPaths"] = list(conceptNode["on paths"].keys())
        elementNode["name"] += ("["+str(len(elementNode["onPaths"]))+")")
        elements[node] = elementNode

        # relations to the node
        topNextNodes = dict(  # we only care about the top 5 relations, the rest will be in the metaData of the element
            sorted(
                conceptNode["nextNodes"].items(),
                key=lambda element: element[1],
                reverse=True
            )[:5]
        )

        tempNexts = []
        for nextNode in topNextNodes:
            if str(nextNode) not in elements:
                elements[str(nextNode)] = {
                    "numberOfLinks": 0,
                    "isEmpty": True,
                    "name": conceptNames[str(nextNode)] if str(nextNode) in conceptNames else
                    "concept "+str(nextNode)+" name not found",
                    "relations":[],
                    "id": nodeCount
                }
                nodeCount += 1
            tempNexts.append({
                "target": elements[nextNode]["id"],
                "relationName": str(topNextNodes[nextNode]),
                "id": nodeCount
            })
            nodeCount += 1
        elementNode["relations"] = tempNexts
        elementNode["numberOfRelations"] = len(tempNexts)

    with open("outputs/Flowthrough.js", "w") as f:
        f.write("var jsonData=")
        json.dump(list(elements.values()), f)
        f.write(";")

def heatMapOfGivenNodes(nodes=None,givenNodes=None,
                        threshholdFlowthroughValue=0,threshholdHitsValue=0,colors="jet", filename=None,
                        debug=False):  # will have the notation: from x, to y
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=datetime_parser)

    if givenNodes is None:
        givenNodes=[x for (x,y) in list(filter(lambda element: element[1]["hits"] > threshholdHitsValue, nodes.items()))]
        if debug:
            print("following nodes were generated:" + str(givenNodes))

    outputMatrix=[]
    for conceptId in givenNodes:
        conceptId = str(conceptId)
        conceptRow=[]
        if conceptId not in nodes:
            continue
        currrentNode=nodes[conceptId]
        for nextId in givenNodes:
            nextId = str(nextId)
            hits = currrentNode["nextNodes"][nextId] if nextId in currrentNode["nextNodes"] else 0
            if hits >= threshholdFlowthroughValue and not nextId == conceptId:
                conceptRow.append(hits)
            else:
                conceptRow.append(0)

        outputMatrix.append(conceptRow)
    values = numpy.array(outputMatrix)

    fig, ax = plt.subplots()
    heatmapify(values, givenNodes, givenNodes, ax=ax, cbarLabel="hits [x->y]", cmap=colors)

    fig.tight_layout()
    if filename is None:
        filename = "outputs/heatmap.png"
    else:
        filename = "outputs/"+filename+".png"
    plt.savefig(filename)
    plt.close(fig)


def heatmapify(data, rowLables, columnLables=None, ax=None,
               cbar_kw={}, cbarLabel = "",
               textColors = ["black", "white"], **miscArgs):
    if isinstance(data,list):
        data = numpy.array(data)
    if columnLables is None:
        columnLables = rowLables[::]
    if ax is None:
        ax=plt.gca()

    if data.size > 0:
        im = ax.imshow(data, **miscArgs)
        cbar=ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarLabel, rotation=-45, va="bottom")

        ax.set_yticks(numpy.arange(data.shape[0]))
        ax.set_xticks(numpy.arange(data.shape[1]))

        ax.set_xticklabels(columnLables)
        ax.set_yticklabels(rowLables)

        # we want ticks and values on all sides to improved readibility
        ax.tick_params(top=False, bottom=True,
                       labeltop=False, labelbottom=True)

        plt.setp(ax.get_xticklabels(), rotation=90, ha="right")

        #create a white grid and turn spines off
        for edge, spine in ax.spines.items():
            spine.set_visible(False)

        ax.set_xticks(numpy.arange(data.shape[1] + 1) - .5, minor=True)
        ax.set_yticks(numpy.arange(data.shape[0] + 1) - .5, minor=True)
        ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
        ax.tick_params(which="minor", bottom=False, left=False)

        # annotate the heatmap
        threshold = im.norm(data.max())/2.
        kw = dict(horizontalalignment="center",
                  verticalalignment="center")

        texts = []
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                kw.update(color=textColors[int(im.norm(data[i, j]) > threshold)])
                text = im.axes.text(j, i, data[i, j])
                texts.append(text)

        return im, cbar, texts
    else:
        plt.text(0.1, 0.85,'no hits',horizontalalignment='center',verticalalignment='center',transform = ax.transAxes)


def hoursPerDayPerUser(users, userId, nodes=None, settings=None,
                              max_value=False, logarithmic_scale=False,
                              startDate=None, endDate=None, days=None, givenName=None):  # based on hitsPerDayPerLearningpath
    while userId is None:
        userId = input("what is the id of the user you would like to analise?\n")
    try:
        user = users[userId]
        print("great sucess")
    except:
        print("user " + str(userId) + " not found")
        print(users)
        return

    if settings is None:
        settings = {}
        settings["learningpaths"] = {}

    if startDate is None:
        try:
            startDate = settings['period']['startDate']
            endDate = settings['period']['endDate']
        except:
            startDate = None
    while startDate is None:
        try:
            startDate = dateutil.parser.parse(input("from which date would you like the graph to start?(yyyy-mm-dd)")).date()
        except:
            continue
    while endDate is None:
        try:
            endDate = dateutil.parser.parse(input("at which date would you like the graph to end?(yyyy-mm-dd)")).date()
        except:
            continue
    if days is None:
        pandaRange = pandas.date_range(startDate, endDate).tolist()
        days = [x.date() for x in pandaRange]
    else:
        days = days.copy()

    n_groups = len(days)
    fig, ax = plt.subplots()
    index = numpy.arange(n_groups)
    bar_width = 0.42
    opacity = 0.9
    data = []
    # We need to know how many total concepts were visited, so we can give all of them their own color
    concepts = {}
    dayConcepts={}
    for elem in user["concepts"]:
        ts, conId, timeSpentOnPage = elem['timestamp'], elem['conceptId'], elem['timeOnPage']
        concepts[conId] = 0

        if ts.date() not in dayConcepts:
            dayConcepts[ts.date()] = {}

        if conId in dayConcepts[ts.date()]:
            dayConcepts[ts.date()][conId] += timeSpentOnPage.seconds/3600 if timeSpentOnPage is not None \
                else 0.3
        else:
            dayConcepts[ts.date()][conId] = timeSpentOnPage.seconds/3600 if timeSpentOnPage is not None \
                else 0.3
    conOrder = list(concepts.keys())

    for i in range(len(conOrder)):
        data.append([])

    # startOfPath = settings["period"]["endDate"]
    # indexStart = 0
    increment = True
    for day in days:
        for i in range(len(conOrder)):
            try:
                data[i].append(dayConcepts[day][conOrder[i]])
                concepts[conOrder[i]] += 1
            except:
                data[i].append(0)
    #     if day == startOfPath.date():
    #         data[len(conOrder)].append(5)
    #         increment=False
    #     else:
    #         data[len(conOrder)].append(0)
    #         indexStart+=increment
    # if indexStart < len(days) : days[indexStart]=str(days[indexStart]) + " LP"

    p = []
    bottom = [0]*len(days)

    for i in range(len(conOrder)):
        p.append(plt.bar(index, data[i], bar_width,
                         label=conceptNames[str(conOrder[i])] + str(concepts[conOrder[i]]), bottom=bottom))
        listAdd(bottom,data[i])
    # p.append(plt.bar(index, data[len(conOrder)], bar_width, label="start of path", color="k", bottom=bottom))

    plt.xlabel('day')
    plt.ylabel('visits')
    plt.title('user ' + str(userId) + ': hours per day')
    if logarithmic_scale:
        plt.yscale('log')

    if max_value:
        axes = plt.gca()
        axes.set_ylim(0,max_value)
    # plt.xticks(index, days)
    xtics=[]
    indices = []
    for x in range(0,len(days),10):
        xtics.append(days[x])
        indices.append(x)
    plt.xticks(indices,xtics)

    # for i in range(len(days)):
    #     plt.text(x=i - 0.5, y=data[0][i] - 0.1, s=data[0][i], size=6)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.grid(b=True, which='major', color='k', linewidth=0.45)
    # ax.text(3, 8, "first hit: " + str(firstHit), style='italic',
    #         bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')
    filename = ("outputs/user" + str(userId) + "/hitsPerDay.png") if givenName is None else givenName
    plt.savefig(filename)
    filename = "outputs/hoursperday/" + str(userId) + ".png"
    plt.savefig(filename)
    plt.close(fig)
    print("done with user " + str(userId))

def hoursPerDayPerUserNoConcepts(users, userId, nodes=None, settings=None,
                              max_value=False, logarithmic_scale=False,
                              startDate=None, endDate=None, days=None, givenName=None):  # based on hitsPerDayPerLearningpath
    while userId is None:
        userId = input("what is the id of the user you would like to analise?\n")
    try:
        user = users[userId]
        print("great sucess")
    except:
        print("user " + str(userId) + " not found")
        print(users)
        return

    if settings is None:
        settings = {}
        settings["learningpaths"] = {}

    if startDate is None:
        try:
            startDate = settings['period']['startDate']
            endDate = settings['period']['endDate']
        except:
            startDate = None
    while startDate is None:
        try:
            startDate = dateutil.parser.parse(input("from which date would you like the graph to start?(yyyy-mm-dd)")).date()
        except:
            continue
    while endDate is None:
        try:
            endDate = dateutil.parser.parse(input("at which date would you like the graph to end?(yyyy-mm-dd)")).date()
        except:
            continue
    if days is None:
        pandaRange = pandas.date_range(startDate, endDate).tolist()
        days = [x.date() for x in pandaRange]
    else:
        days = days.copy()

    n_groups = len(days)
    fig, ax = plt.subplots()
    index = numpy.arange(n_groups)
    bar_width = 0.82
    opacity = 0.9
    data = [[],[]]
    # We need to know how many total concepts were visited, so we can give all of them their own color
    concepts = {}
    dayConcepts={}
    unKnownDays={}
    visitedDays={}
    for elem in user["concepts"]:
        ts, conId, timeSpentOnPage = elem['timestamp'], elem['conceptId'], elem['timeOnPage']
        concepts[conId] = 0

        if timeSpentOnPage is None:
            if ts.date() not in unKnownDays:
                unKnownDays[ts.date()] = 0.3
            else:
                unKnownDays[ts.date()] += 0.3
        else:
            if ts.date() not in visitedDays:
                visitedDays[ts.date()] = timeSpentOnPage.seconds/3600
            else:
                visitedDays[ts.date()]+= timeSpentOnPage.seconds/3600

    # startOfPath = settings["period"]["endDate"]
    # indexStart = 0
    increment = True
    for day in days:
        try:
            data[0].append(visitedDays[day])
        except:
            data[0].append(0)
        try:
            data[1].append(unKnownDays[day])
        except:
            data[1].append(0)


    p = []
    bottom = [0]*len(days)

    for i in [0, 1]:
        p.append(plt.bar(index, data[i], bar_width,
                         label=["hours spent","hours estimated"][i], bottom=bottom, color=["black", "grey"][i]))
        listAdd(bottom,data[i])
    # p.append(plt.bar(index, data[len(conOrder)], bar_width, label="start of path", color="k", bottom=bottom))

    plt.xlabel('day')
    plt.ylabel('hours')
    plt.title(str(userId) + ': hours per day')
    if logarithmic_scale:
        plt.yscale('log')

    if max_value:
        axes = plt.gca()
        axes.set_ylim(0,max_value)
    # plt.xticks(index, days)
    xtics=[]
    indices = []
    for x in range(0,len(days), 14):
        xtics.append(days[x])
        indices.append(x)
    plt.xticks(indices,xtics)

    # for i in range(len(days)):
    #     plt.text(x=i - 0.5, y=data[0][i] - 0.1, s=data[0][i], size=6)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.grid(b=True, which='major', color='k', linewidth=0.45)
    # ax.text(3, 8, "first hit: " + str(firstHit), style='italic',
    #         bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.setp(ax.get_xticklabels(), rotation=50, horizontalalignment='right')
    filename = ("outputs/user" + str(userId) + "/hitsPerDay.png") if givenName is None else givenName
    plt.savefig(filename)
    filename = "outputs/hoursperday/" + str(userId) + ".png"
    plt.savefig(filename)
    plt.close(fig)
    print("done with user " + str(userId))