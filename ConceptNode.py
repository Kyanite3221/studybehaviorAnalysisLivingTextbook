import bisect
import datetime


class Node:
    def __init__(self, id, studyArea):
        self.id = id
        self.studyArea = studyArea
        self.onPaths={}
        self.nextNodes = {}
        self.pageHits = {}
        self.userHits = {}
        self.hits=0
        self.typeOfHits = {"general": 0, "conceptBrowser": 0, "learningPathBrowser": 0,
                           "undefined": 0, "other": 0, "external": 0}

    def addNextNode(self, nextNode):
        if nextNode in self.nextNodes:
            self.nextNodes[nextNode] += 1
        else:
            self.nextNodes[nextNode] = 1

    def addPath(self, pathId,index):
        if pathId in self.onPaths:
            self.onPaths[pathId].append(index)
        else:
            self.onPaths[pathId]=[index]

    def visitNode(self,userHash,date,typeOfVisit=None):
        date = str(datetime.date(date.year,date.month,date.day))
        self.hits += 1
        if date in self.pageHits:
            self.pageHits[date] +=1
            self.userHits[date][userHash] = True
        else:
            self.pageHits[date]=1
            self.userHits[date]={}
            self.userHits[date][userHash] = True

        if typeOfVisit not in ["general", "conceptBrowser", "learningPathBrowser", "external"]:
            if typeOfVisit is None:
                self.typeOfHits["undefined"] += 1
            else:
                self.typeOfHits["other"] += 1
        else:
            self.typeOfHits[typeOfVisit] +=1


class NodeMap:
    nodes = {}

    def __getitem__(self, id):
        try:
            return self.nodes[id] if id in self.nodes else self.nodes[str(id)]
        except KeyError:
            return None

    def add(self, node):
        if not node.id in self.nodes:
            self.nodes[node.id] = node

    def getNode(self, node):
        if node.id in self.nodes:
            return self.nodes[node.id]
        else:
            self.nodes[node.id] = node
            return node


def jsonify(nodemap):
    output = {}
    for i in nodemap.nodes:
        node = {}
        node['id'] = nodemap.nodes[i].id
        node['studyArea'] = nodemap.nodes[i].studyArea
        node['nextNodes'] = nodemap.nodes[i].nextNodes
        node["on paths"]=nodemap.nodes[i].onPaths
        node["hits per day"] = nodemap.nodes[i].pageHits
        node["users per day"] = nodemap.nodes[i].userHits
        node["hits"]=nodemap.nodes[i].hits
        node["typeOfHits"]=nodemap.nodes[i].typeOfHits
        output[i] = node
    return output

emptyNode=Node(0,0)