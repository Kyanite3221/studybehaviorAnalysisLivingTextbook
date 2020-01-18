import csv
import datetime
import json
import os
import sys
import FilterData
import Annonymisation
import DataProcessing
import dateutil.parser
import Visualisation

USERIDINDEX = 0
SESSIONIDINDEX = 1
TIMESTAMPINDEX = 2
ORIGININDEX = 3
EVENTINDEX = 3
PATHINDEX = 4
CONCEPTINDEXEVENT = 4
INTERNALROUTEINDEX = 5
LEARNINGPATHINDEXEVENTS = 5
STUDYAREAINDEX = 6
LINKINDEX = 6
CONCEPTINDEXPATH = 7
LEARNINGPATHINDEXPATH = 8


def datetime_parser(dct):
    for k, v in dct.items():
        try:
            if '/' in v or '-' in v:
                dct[k] = dateutil.parser.parse(v)
            else:
                pass
        except:
            pass
    return dct


def main(nameFilename, debug=False, dataFilename=None, learningPaths={},
         students=None, period=None, heatMapColor="jet", functions=None,
         filterQuickClicks=False, filesToSave={"metaData": True, "nodes": True},
         conceptHitsParams=None, heatMapParams=None, studentGroups=None, **restArgs):
    Visualisation.init(nameFilename)
    settings = {}
    settings['learningpaths'] = learningPaths
    settings['students'] = students if not students is None else {
        "whitelist": False,
        "list": []
    }
    settings['period'] = period if not period is None else {
        "usePeriod": False
    }

    if dataFilename is None:
        dataFilename = [x for x in input("which file would you like to use?(please enter the name of the excel file "
                                      "or files seperated by commas)\n").split(',')]

    sample = {'learningpaths': {}, 'students': {'whitelist': True,
                                                'list': [{'type': 'text', 'value': 'h.d.flynn@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'l.d.hermans@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'm.karacor@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'v.r.j.bensdorp@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'y.chen-13@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'f.guzzardo@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'm.d.kuiper@student.utwente.nl'},
                                                         {'type': 'text', 'value': 'y.b.tuzgel@student.utwente.nl'}]},
              'period': {'usePeriod': False, 'startDate': datetime.datetime(2019, 9, 1, 0, 0),
                         'endDate': datetime.datetime(2019, 12, 13, 0, 0)}}
    print(settings == sample)

    data = FilterData.filterAndExtractData(dataFilename, settings, debug=debug)
    if debug: print("done extracting data")

    # Annonymisation.annonymiseExtracted(data)
    # if debug: print("done making data anonymous")
    lookup = {}
    with open("inputFiles/studentsEncoded.csv",'r') as studsEncode:
        reader=csv.reader(studsEncode)
        for name, number in reader:
            lookup[name] = number
    Annonymisation.alternateAnonymiseExtracted(data, lookup)

    output = DataProcessing.processDataExtracted(data, settings['learningpaths'], filterQuickClicks,
                                                 filesToSave=filesToSave, timeOnPageCalc=True)
    # ToDo if visualisation's input is fixed, output['nodes'] can be used instead of loading nodes.json each time
    firstHit=[]
    try:
        os.mkdir("outputs/hitsperday")
    except:
        pass
    try:
        os.mkdir("outputs/hoursperday")
    except:
        pass
    # for user in output["users"]:
    #     print(user)
    #     try:
    #         os.mkdir("outputs/user" + user)
    #     except:
    #         pass
    #     firstHit.append(Visualisation.hitsPerDayPerUser(output["users"], user, output["nodes"], settings))
    #     Visualisation.hoursPerDayPerUser(output['users'], user, output['nodes'], settings)
    # print(max(firstHit))
    for studentGroup in studentGroups:
        print(studentGroup)
        try:
            os.mkdir("outputs/hoursPerDayPerStudent/")
        except:
            pass
        try:
            os.mkdir("outputs/hoursPerDayPerStudent/" + studentGroup)
        except:
            pass
        print(studentGroup)
        for student in studentGroups[studentGroup]:
            student = "student "+str(student)
            Visualisation.hoursPerDayPerUserNoConcepts(output['users'], student, output['nodes'], settings,
                                             givenName="outputs/hoursPerDayPerStudent/"+studentGroup+"/"+student)

    # for path in settings['learningpaths']:
    #     Visualisation.learningpathFlowthrough(settings['learningpaths'][path])
    #     Visualisation.hitsPerDayPerLearningPath(pathId=path, settings=settings)
    #     Visualisation.heatMapOfGivenNodes(givenNodes=settings['learningpaths'][path]['list'],
    #                                       filename="heatmapPath" + str(path), colors=heatMapColor)
    #     if debug: print("done for path " + str(path))
    if debug: print(settings)
    DataProcessing.csvExports(nameFilename, learningPaths=settings['learningpaths'], functions=functions)

    # if not functions is None:
    #     if ("all" in functions or "allHitsPerDayPerConceptGraph" in functions) and conceptHitsParams:
    #         if debug: print("HitsPerDayPerConceptGraph same scale")
    #         Visualisation.generateSetOfPathVisits(conceptHitsParams, settings=settings,
    #                                               debug=debug, users=False, specificConcept=True)
    #     if "HitsPerDayPerConceptGraph" in functions and conceptHitsParams:
    #         if debug: print("HitsPerDayPerConceptGraph varying scales")
    #         for conceptId in conceptHitsParams:
    #             Visualisation.hitsPerDay(nodeId=conceptId)
    #     if "usersPerDayPerLearningPath" in functions:  # not all, because if we want all, they should be on the same scale
    #         if debug: print("usersPerDayPerLearningPath varying scales")
    #         for path in settings['learningpaths']:
    #             Visualisation.usersPerDayPerLearningPath(path, settings=settings)
    #     if "all" in functions or "allUsersPerDayPerLearningPath" in functions:
    #         if debug: print("UsersPerDayPerLearningPath same scale")
    #         Visualisation.generateSetOfPathVisits(pathId=list(settings['learningpaths']), settings=settings,
    #                                               debug=debug, users=True)
    #     if "all" in functions or "allHitsPerDayPerLearningPath" in functions:
    #         if debug: print("HitsPerDayPerLearningPath same scale")
    #         Visualisation.generateSetOfPathVisits(pathId=list(settings['learningpaths']), settings=settings,
    #                                               debug=debug)
    #     if "all" in functions or "allNodesFlowthrough" in functions:
    #         if debug: print("allNodesFlowthrough")
    #         Visualisation.allNodesFlowthrough(debug=debug)  # ToDo there is currently no way to properly display this
    #     if ("all" in functions or "allNodesHeatMap" in functions) and heatMapParams:
    #         if debug: print("allNodesHeatmap")
    #         Visualisation.heatMapOfGivenNodes(**heatMapParams)




    # ToDo nodes.json could be saved in such a way that the same nodes.json is not generated twice for the same settings
    if "all" not in filesToSave:  # remove any unwanted files
        if "metaData" not in filesToSave:
            if debug: print("removing metadata.json")
            os.remove("outputs/metaData.json")
        if "nodes" not in filesToSave:
            if debug: print("removing nodes.json")
            os.remove("outputs/nodes.json")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        settingsFileName = sys.argv[1]
        with open(settingsFileName, 'r') as settingsFile:
            settings = json.load(settingsFile, object_hook=datetime_parser)
        settings["functions"] = dict([(x, True) for x in settings['functions']]) if 'functions' in settings else None
        totalSettings=settings
        # ToDo use kwargs for this
    else:
        totalSettings={}
        totalSettings["learningpaths"] = {"8":
                             {"starting time": "2019-09-03 08:45:00",
                              "list": [11941, 11894, 11833, 11800, 11832, 11801, 11853, 11799, 12070], "id": "8"},
                         "135":
                             {"starting time": "2019-09-03 09:30:00",
                              "list": [12021, 11927, 11835, 11926, 11866, 12038, 11958, 11777, 11980], "id": "135"},
                         }
        startDate = dateutil.parser.parse("2019-09-01")
        endDate = dateutil.parser.parse("2019-09-23")
        totalSettings["period"] = {"usePeriod": True, "startDate": startDate, "endDate": endDate}
        totalSettings["fileNames"] = ["inputFiles/gis_rs_v2_tracking_export3_10_2019.xlsx"]
        totalSettings["nameFileName"] = "configurationFiles/gis_rs_v2_names.csv"
    main(**totalSettings)
    # Visualisation.hitsPerDayPerLearningPath(max_value=500)
    # ToDo add another argument to the settings to see which additional functions should be run
    # metaData=None
    # with open("outputs/metaData.json", "r") as input:
    #     metaData=json.load(input, object_hook=datetime_parser)
    # Visualisation.generateSetOfPathVisits(metaData=metaData)
    # Visualisation.allNodesFlowthrough()
