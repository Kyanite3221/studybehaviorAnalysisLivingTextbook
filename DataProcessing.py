import csv
import os
import re
import json
import Main
from ConceptNode import *


def appendOrCreateUser(given_map, user_hash, value, page=True):
    if not (user_hash in given_map):
        given_map[user_hash] = {'pages': [], 'events': [],
                                'learningTimestamps': [], 'concepts': [], 'conceptEvents': {}}
    if page:
        given_map[user_hash]['pages'].append(value)
    else:
        given_map[user_hash]['events'].append(value)


def processDataExtracted(data, learningPaths, filterHitsByTime=True):

    # load the workbook


    users = {}
    nodeMap = NodeMap()

    metaData={"hitsPerLearningPathPerDay":{}, "hitsPerDay": {}}

    wb = data
    events = wb['Events']
    extractLearningPathTimestampsAndTypeOfHits(events, users)
    # we now have a list of when a user started with a learning path,until the first timestamp,
    # the user is in an undefined learning path, afterwards,
    # they are assumed to be in the last learningpath they activated.
    # This is not currently being used for the output

    pageLoads = wb['Page loads']
    # extractConceptsThroughEvents(nodeMap, events, users,filterHitsByTime)
    metaData['typeOfHitsPerDay'] = extractConceptsWithOrigin(nodeMap, pageLoads, users, False)
    # we now want to know in which paths each concept was
    # ToDo add the visits to the extraction
    for path in learningPaths:
        for i in range(len(learningPaths[path]["list"])):
            concept = learningPaths[path]["list"][i]
            node = nodeMap[concept]
            if node is not None:
                node.addPath(path, i)


    userPaths = {}
    for user in users:  # ToDo can be sped up by removing stuff that isn't used(like the learningpath following)
        userPaths[user] = []
        hasPath = True
        hasNextPath = True
        curPathIndex = 0
        if len(users[user]['learningTimestamps']) > 1:
            curPathTimestamp = users[user]['learningTimestamps'][curPathIndex][0]
            nextPathTimestamp = users[user]['learningTimestamps'][curPathIndex + 1][0]
            curPath = users[user]['learningTimestamps'][curPathIndex][1]
        elif len(users[user]['learningTimestamps']) > 0:
            hasNextPath = False
            curPath = users[user]['learningTimestamps'][curPathIndex][1]
            curPathTimestamp = users[user]['learningTimestamps'][curPathIndex][0]
        else:
            hasPath = False
            hasNextPath = False
            curPath = None
        lastConcept=None
        # we now know if a user was following a path at this point

        for concept in users[user]['concepts']:

            if str(concept[0].date()) in metaData["hitsPerDay"]:
                metaData["hitsPerDay"][str(concept[0].date())]+=1
            else:
                metaData["hitsPerDay"][str(concept[0].date())]=1

            if lastConcept is not None:
                nodeMap[lastConcept[1]].addNextNode(concept[1])
            if hasPath:
                if hasNextPath:
                    # check if timestamp between current path and next path is,
                    # otherwise move one and check if there are more paths
                    if concept[0] < curPathTimestamp:  # the timestamp of this concept was before a path was chosen
                        userPaths[user].append({'concept': concept[1], 'on path': None, 'timestamp': concept[0]})
                    elif curPathTimestamp <= concept[0]\
                            < nextPathTimestamp:  # the timestamp of the concept was between one path and the next
                        if str(curPath) in learningPaths:
                            path = learningPaths[str(curPath)]
                            userPaths[user].append({'concept': concept[1], "following path": {curPath: path},
                                                    "in path": concept[1] in path["list"], "timestamp": concept[0]})
                        else:
                            userPaths[user].append({"concept": concept[1], "following path" : str(curPath)+"(not pre-programmed)",
                                                    "in path": False, "timestamp": concept[0]})
                    else:  # the timestamp of this concept was after the next concept

                        while concept[0] >= nextPathTimestamp and hasNextPath:
                            curPathIndex += 1
                            if curPathIndex+1 < len(users[user]['learningTimestamps']):
                                nextPathTimestamp = users[user]['learningTimestamps'][curPathIndex + 1][0]
                            hasNextPath = curPathIndex+1 < len(users[user]['learningTimestamps'])
                        curPathTimestamp = users[user]['learningTimestamps'][curPathIndex][0]
                        curPath = users[user]['learningTimestamps'][curPathIndex][1]
                        if str(curPath) in learningPaths:
                            path = learningPaths[str(curPath)]
                            userPaths[user].append({'concept': concept[1], "following path": {curPath:path},
                                                    "in path": concept[1] in path["list"], "timestamp": concept[0]})
                        else:
                            userPaths[user].append({"concept": concept[1], "following path" : str(curPath)+"(not pre-programmed)",
                                                    "in path": False, "timestamp" : concept[0]})
                else:
                    if concept[0] > curPathTimestamp:
                        if str(curPath) in learningPaths:
                            path = learningPaths[str(curPath)]
                            userPaths[user].append({'concept': concept[1], "following path": {curPath:path},
                                                    "in path": concept[1] in path["list"], "timestamp": concept[0]})
                        else:
                            userPaths[user].append({"concept": concept[1], "following path" : str(curPath)+"(not pre-programmed)",
                                                    "in path": False, "timestamp" : concept[0]})
                    else:
                        userPaths[user].append({'concept': concept[1], 'on path': None, 'timestamp': concept[0]})
            else:
                userPaths[user].append(concept)

            for learningPath in nodeMap[concept[1]].onPaths:
                if not str(learningPath) in metaData["hitsPerLearningPathPerDay"]:
                    metaData["hitsPerLearningPathPerDay"][str(learningPath)]={}
                pathHits = metaData["hitsPerLearningPathPerDay"][str(learningPath)]
                if str(concept[0].date()) in pathHits:
                    pathHits[str(concept[0].date())] += 1
                else:
                    pathHits[str(concept[0].date())] = 1
            lastConcept = concept

    saveExportFiles(metaData, nodeMap, userPaths, users)
    return {"users": users, "nodes": jsonify(nodeMap), "userPaths": userPaths, "metaData": metaData}


def saveExportFiles(metaData, nodeMap, userPaths, users):
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    metaData["totalUsersInPeriod"] = len(users)
    with open('outputs/users.json', 'w+') as output:
        json.dump(users, output, default=str)
    with open('outputs/nodes.json', 'w+') as output:
        json.dump(jsonify(nodeMap), output, default=str)
    with open('outputs/paths.json', 'w+') as output:
        json.dump(userPaths, output, default=str)
    with open('outputs/metaData.json', 'w+') as output:
        json.dump(metaData, output, default=str)


def extractLearningPathTimestampsAndTypeOfHits(events, users):  # determine when a user started with a learningpath
    patern = re.compile("/[\d]*/concept/(\d+)*$")
    for row in events:
        appendOrCreateUser(users, row[0].value, {'event': row[3].value, 'link': row[6].value, 'concept': row[4].value,
                                                 'learning path': row[5].value, 'timestamp': row[2].value,
                                                 'session ID': row[1].value}, False)
        # in this event a learning path is selected
        if not (row[Main.LEARNINGPATHINDEXEVENTS].value is None):
            bisect.insort(users[row[Main.USERIDINDEX].value]['learningTimestamps'],
                          (row[Main.TIMESTAMPINDEX].value, row[Main.LEARNINGPATHINDEXEVENTS].value))

        timestamp = row[2].value  # there.
        matcher = re.match(patern, str(row[6].value))
        if row[3].value == "general_link_click" and matcher:
            users[row[0].value]['conceptEvents'][str(timestamp.strftime("%Y-%m-%d %H:%M:%S"))] = (str(matcher.group(1)), "general")
        elif row[3].value == "learning_path_browser_open_concept":
            users[row[0].value]['conceptEvents'][str(timestamp.strftime("%Y-%m-%d %H:%M:%S"))] = (str(row[4].value), "learningPathBrowser")
        elif row[3].value == "concept_browser_open_concept":
            users[row[0].value]['conceptEvents'][str(timestamp.strftime("%Y-%m-%d %H:%M:%S"))] = (str(row[4].value), "conceptBrowser")


def extractConcepts(nodeMap, pageLoads, users):  # outdated, replaced by extractConceptsLimited
    for row in pageLoads:
        studyArea = row[6].value
        concept = row[7].value
        timestamp = row[2].value
        origin = row[3].value
        appendOrCreateUser(users, row[0].value, {'path': row[4].value, 'study area': studyArea, 'concept': concept,
                                                 'timestamp': timestamp, 'session ID': row[1].value,
                                                 'origin': origin,
                                                 'learning path': row[8].value})
        # the order in which we investigate the type of page it was is not relevant as it can be only one
        if concept is not None:
            bisect.insort(users[row[0].value]['concepts'], (timestamp, concept))
            nodeMap.add(Node(concept, studyArea))
            nodeMap[concept].visitNode(row[0].value, timestamp)

        p = re.compile("/[\d]*/learningpath/show/(\d+)*$")  # regex for the learning path so we can capture its number
        m = re.match(p, row[Main.PATHINDEX].value)
        if m:
            bisect.insort(users[row[Main.USERIDINDEX].value]['learningTimestamps'],
                          (row[Main.TIMESTAMPINDEX].value, m.group(1)))


def extractConceptsLimited(nodeMap, pageLoads, users):  # outdated, replaced by extractConceptsThroughEvents
    for row in pageLoads:                               # this version added the requirement that a page load was only
        studyArea = row[6].value                        # used if it was at leas a second after the previous one.
        concept = row[7].value
        timestamp = row[2].value
        origin = row[3].value
        userHash=row[0].value
        appendOrCreateUser(users, userHash, {'path': row[4].value, 'study area': studyArea, 'concept': concept,
                                                 'timestamp': timestamp, 'session ID': row[1].value,
                                                 'origin': origin,
                                                 'learning path': row[8].value})
        # the order in which we investigate the type of page it was is not relevant as it can be only one
        if concept is not None:
            bisect.insort(users[userHash]['concepts'], (timestamp, concept, studyArea))

        p = re.compile("/[\d]*/learningpath/show/(\d+)*$")  # regex for the learning path so we can capture its number
        m = re.match(p, row[Main.PATHINDEX].value)
        if m:
            bisect.insort(users[row[Main.USERIDINDEX].value]['learningTimestamps'],
                          (row[Main.TIMESTAMPINDEX].value, m.group(1)))

    for userHash in users:
        user = users[userHash]
        templist = []
        nextTimestamp=datetime.datetime.now()
        nextConcept=None
        for (timestamp,concept,studyArea) in reversed(user['concepts']):
            if (nextTimestamp-timestamp).total_seconds() < 1:  # the concept was less than one second before the next
                continue  # we can assume it was a misclick or part of navigation, thus we skip it
            # If the next concept is a different one or more than 60 seconds have passed, we assume the hit was useful
            if (not concept == nextConcept) or (nextTimestamp-timestamp).total_seconds() > 60:
                templist.append((timestamp, concept, studyArea))  # add the node in reverse order
                nextTimestamp = timestamp
                nextConcept = concept
                nodeMap.add(Node(concept, studyArea))
                nodeMap[concept].visitNode(userHash, timestamp)
        user['concepts'] = templist[::-1]


def extractConceptsThroughEvents(nodeMap, events, users, filterHits=True,
                                 debug=False):  # replaced by extractConceptsWithOrigin
    patern = re.compile("/[\d]*/concept/(\d+)*$")
    for event in events:                                   # in which order for each user, and to determine how they got
        timestamp = event[2].value                         # there.
        matcher = re.match(patern, str(event[6].value))
        if event[3].value == "general_link_click" and matcher:
            bisect.insort(users[event[0].value]['concepts'], (timestamp, str(matcher.group(1)), "general"))
        elif event[3].value == "learning_path_browser_open_concept":
            bisect.insort(users[event[0].value]['concepts'], (timestamp, str(event[4].value), "learningPathBrowser"))
        elif event[3].value == "concept_browser_open_concept":
            bisect.insort(users[event[0].value]['concepts'], (timestamp, str(event[4].value), "conceptBrowser"))

    dumpedValues = 0
    dumpers={"general":0,"learningPathBrowser":0,"conceptBrowser":0}
    for userHash in users:
        user = users[userHash]
        nextConcept=None
        nextTimestamp = datetime.datetime.now()
        templist=[]
        for (timestamp, concept, typeOfVisit) in reversed(user['concepts']):
            if filterHits:
                if (nextTimestamp - timestamp).total_seconds() < 1:  # the concept was less than one second before the next
                    dumpedValues += 1
                    dumpers[typeOfVisit] += 1
                    continue  # we can assume it was a misclick or part of navigation, thus we skip it
                # If the next concept is a different one or more than 60 seconds have passed, we assume the hit was useful
                elif (not concept == nextConcept) or (nextTimestamp - timestamp).total_seconds() > 60:
                    templist.append((timestamp, concept, 0))  # add the node in reverse order
                    nextTimestamp = timestamp
                    nextConcept = concept
                    nodeMap.add(Node(concept, 0))
                    nodeMap[concept].visitNode(userHash, timestamp,typeOfVisit)
            else:
                templist.append((timestamp, concept, 0))  # add the node in reverse order
                nodeMap.add(Node(concept, 0))
                nodeMap[concept].visitNode(userHash, timestamp, typeOfVisit)
        user['concepts'] = templist[::-1]
    if debug: print("dumped " + str(dumpedValues) + " values," + str(dumpers))


def extractConceptsWithOrigin(nodeMap, pageLoads, users, filterHits=True):
    patern = re.compile("/[\d]*/learningpath/show/(\d+)*$")  # regex for the learning path so we can capture its number
    hitTypesPerDay={}

    for row in pageLoads:
        studyArea = row[6].value
        concept = row[7].value
        timestamp = row[2].value
        origin = row[3].value
        userHash=row[0].value
        appendOrCreateUser(users, userHash, {'path': row[4].value, 'study area': studyArea, 'concept': concept,
                                                 'timestamp': timestamp, 'session ID': row[1].value,
                                                 'origin': origin,
                                                 'learning path': row[8].value})
        # the order in which we investigate the type of page it was is not relevant as it can be only one
        if concept is not None:
            bisect.insort(users[userHash]['concepts'], (timestamp, concept, studyArea))

        matcher = re.match(patern, row[Main.PATHINDEX].value)
        if matcher:
            bisect.insort(users[row[Main.USERIDINDEX].value]['learningTimestamps'],
                          (row[Main.TIMESTAMPINDEX].value, matcher.group(1)))

    for userHash in users:
        user = users[userHash]
        templist = []
        nextTimestamp=datetime.datetime.now()
        nextConcept=None
        for (timestamp, concept, studyArea) in reversed(user['concepts']):
            if filterHits:
                if (nextTimestamp-timestamp).total_seconds() < 1:  # the concept was less than one second before the next
                    continue  # we can assume it was a misclick or part of navigation, thus we skip it
                # If the next concept is a different one or more than 60 seconds have passed, we assume the hit was useful
                if (not concept == nextConcept) or (nextTimestamp-timestamp).total_seconds() > 60:
                    templist.append((timestamp, concept, studyArea))  # add the node in reverse order
                    nextTimestamp = timestamp
                    nextConcept = concept
                    nodeMap.add(Node(concept, studyArea))
                    typeOfHit = determineHitType(user, timestamp, concept)
                    nodeMap[concept].visitNode(userHash, timestamp, typeOfHit)

                    if str(timestamp.date()) in hitTypesPerDay:
                        hitTypesPerDay[str(timestamp.date())][typeOfHit] += 1
                    else:
                        hitTypesPerDay[str(timestamp.date())]={}
                        for hitType in ["general", "conceptBrowser", "learningPathBrowser", "external"]:
                            hitTypesPerDay[str(timestamp.date())][hitType] = 0
                        hitTypesPerDay[str(timestamp.date())][typeOfHit] += 1

            else:
                templist.append((timestamp, concept, 0))  # add the node in reverse order
                nodeMap.add(Node(concept, 0))
                typeOfHit = determineHitType(user, timestamp, concept)
                nodeMap[concept].visitNode(userHash, timestamp, typeOfHit)

                if str(timestamp.date()) in hitTypesPerDay:
                    hitTypesPerDay[str(timestamp.date())][typeOfHit] += 1
                else:
                    hitTypesPerDay[str(timestamp.date())] = {}
                    for hitType in ["general", "conceptBrowser", "learningPathBrowser", "external"]:
                        hitTypesPerDay[str(timestamp.date())][hitType] = 0
                    hitTypesPerDay[str(timestamp.date())][typeOfHit] += 1
        user['concepts'] = templist[::-1]
    return hitTypesPerDay

def determineHitType(user, timestamp, concept, EVENTPAGELOADDELAY=1):
    if str(timestamp.strftime("%Y-%m-%d %H:%M:%S")) in user['conceptEvents'] and str(user['conceptEvents'][str(timestamp.strftime("%Y-%m-%d %H:%M:%S"))][0]) == str(concept):
        return user['conceptEvents'][str(timestamp.strftime("%Y-%m-%d %H:%M:%S"))][1]
    else:
        return "external"




def csvExports(nameFilename, metaData=None,nodes=None, learningPaths=None, debug=False, functions=None):  # ToDo split this into other functions
    if metaData is None:
        with open("outputs/metaData.json", "r") as f:
            metaData = json.load(f, object_hook=Main.datetime_parser)
    if nodes is None:
        with open("outputs/nodes.json", "r") as f:
            nodes = json.load(f, object_hook=Main.datetime_parser)
    # if learningPaths is None:
    #     with open("configurationFiles/learningPaths.json") as f:
    #         learningPaths = json.load(f, object_hook=Main.datetime_parser)
    conceptNames = {}
    with open(nameFilename) as f:
        lines = csv.reader(f, delimiter=";")
        for x, y in lines:
            conceptNames[x] = y

    hitsPerDay=[]
    for day in metaData["hitsPerDay"]:
        bisect.insort(hitsPerDay, (day, metaData["hitsPerDay"][day]))

    if functions is None:
        saveMetaDataForDashboard(metaData)
    else:

        if "all" in functions or "totalHitsPerDay" in functions: saveHitsPerDay(hitsPerDay)

        if "all" in functions or "pathHitsPerDay" in functions: saveHitsPerDayInPath(metaData)

        if "all" in functions or "dailyOrigins" in functions: saveDailyOrigins(metaData)

        if "all" in functions or "odData" in functions: saveOriginDestinationData(debug, learningPaths, nodes)

        if "all" in functions or "totalOrigins" in functions: calculateTotalOriginHits(metaData, nodes)

        if "all" in functions or "dashboardMetaData" in functions: saveMetaDataForDashboard(metaData)

        if "all" in functions or "conceptOrigins" in functions: saveConceptOrigins(conceptNames, nodes)


def saveConceptOrigins(conceptNames, nodes):
    with open("outputs/originsPerConcept.csv", "w", newline='') as originOutput:
        writer = csv.writer(originOutput, 'excel')
        writer.writerow(["concept(conceptId)", "total hits", "general link clicks", "Concept browser hits",
                         "learning path hits", "external link clicks"])
        for id in nodes:
            node = nodes[id]
            writer.writerow([conceptNames[id] + "(" + str(id) + ")" if id in conceptNames else id, node['hits'],
                             node['typeOfHits']['general'],
                             node['typeOfHits']['conceptBrowser'], node['typeOfHits']['learningPathBrowser'],
                             node['typeOfHits']['external']])


def saveMetaDataForDashboard(metaData):
    with open("outputs/metaDataDashBoard.csv", "w", newline='') as metaOutputPrime:
        totalUsers = metaData["totalUsersInPeriod"]
        totalHitsPerPath = [(x, sum(y.values())) for (x, y) in metaData["hitsPerLearningPathPerDay"].items()]
        writer = csv.writer(metaOutputPrime)
        writer.writerow(["total users in period", totalUsers])
        writer.writerow(["total hits per learningpath", totalHitsPerPath])


def calculateTotalOriginHits(metaData, nodes):
    with open("outputs/metaData.json", "w") as metaOutput:
        mostVisited = []
        totalHits = 0
        generalHits = 0
        conceptHitps = 0
        learningPathHits = 0
        externalPathHits = 0
        for node in nodes:
            bisect.insort(mostVisited, (nodes[node]["hits"], node))
            mostVisited = mostVisited[-25:]
            totalHits += nodes[node]["hits"]
            types = nodes[node]["typeOfHits"]
            generalHits += types["general"]
            conceptHitps += types["conceptBrowser"]
            learningPathHits += types["learningPathBrowser"]
            externalPathHits += types["external"]
        metaData["mostVisited"] = mostVisited
        metaData["totalHits"] = totalHits
        metaData["generalLinkConceptHits"] = (generalHits, generalHits / totalHits if totalHits > 0 else 0)
        metaData["conceptBrowserConceptHits"] = (conceptHitps, conceptHitps / totalHits if totalHits > 0 else 0)
        metaData["learningPathBrowserConceptHits"] = (
        learningPathHits, learningPathHits / totalHits if totalHits > 0 else 0)
        metaData["externalHits"] = (externalPathHits, externalPathHits / totalHits if totalHits > 0 else 0)

        json.dump(metaData, metaOutput, default=str)


def saveOriginDestinationData(debug, learningPaths, nodes):
    with open("outputs/odData.csv", "w", newline='') as odOutput:
        writer = csv.writer(odOutput)
        writer.writerow(["origin", "destination", "frequency"])
        concepts = []
        maxTrans = (0, 0, 0)
        for path in learningPaths:
            for concept in learningPaths[path]["list"]:
                concepts.append(str(concept))

        for node in concepts:
            node = str(node)
            if node in nodes:
                for conceptP in concepts:
                    conceptP = str(conceptP)
                    if conceptP in nodes[node]["nextNodes"]:
                        writer.writerow([node, conceptP, nodes[node]["nextNodes"][conceptP]])
                        maxTrans = max(maxTrans, (nodes[node]["nextNodes"][conceptP], node, conceptP))
                    # else:
                    #     writer.writerow([node, conceptP, 0])
            else:
                for conceptP in concepts:
                    writer.writerow([node, conceptP, 0])
        if debug: print("most common transition was:" + str(maxTrans))


def saveDailyOrigins(metaData):
    with open("outputs/originDataDay.csv", 'w', newline='') as dayoutput:
        writer = csv.writer(dayoutput)
        types = ["general", "external", "conceptBrowser", "learningPathBrowser"]
        writer.writerow(["day"] + types + ["total"])
        for day in sorted(metaData['typeOfHitsPerDay']):
            total = 0
            row = [str(day)]
            for type in types:
                row.append(metaData['typeOfHitsPerDay'][day][type])
                total += metaData['typeOfHitsPerDay'][day][type]
            row.append(total)
            writer.writerow(row)


def saveHitsPerDayInPath(metaData):
    for path in metaData["hitsPerLearningPathPerDay"]:
        hitsPerDay = []
        for day in metaData["hitsPerLearningPathPerDay"][path]:
            bisect.insort(hitsPerDay, (day, metaData["hitsPerLearningPathPerDay"][path][day]))

        with open("outputs/hitsPerDayPath" + path + ".csv", "w", newline='') as hitsOutput:
            writer = csv.writer(hitsOutput)
            writer.writerow(["days", "hits", "path" + path])
            for day in hitsPerDay:
                writer.writerow(day)


def saveHitsPerDay(hitsPerDay):
    with open("outputs/hitsPerDay.csv", "w", newline='') as hitsOutput:
        writer = csv.writer(hitsOutput)

        writer.writerow(["days", "hits"])
        for day in hitsPerDay:
            writer.writerow(day)