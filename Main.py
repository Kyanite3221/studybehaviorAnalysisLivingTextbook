import json
import os
import sys
import FilterData
import Annonymisation
import DataProcessing
import dateutil.parser
import Visualisation

USERIDINDEX=0
SESSIONIDINDEX=1
TIMESTAMPINDEX=2
ORIGININDEX=3
EVENTINDEX=3
PATHINDEX=4
CONCEPTINDEXEVENT=4
INTERNALROUTEINDEX=5
LEARNINGPATHINDEXEVENTS=5
STUDYAREAINDEX=6
LINKINDEX=6
CONCEPTINDEXPATH=7
LEARNINGPATHINDEXPATH=8


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


def main(nameFilename,debug=False,fileNames=None,learningPaths={},
         students=None, period=None, heatMapColor="jet", functions=None,
         filterQuickClicks=False, filesToSave={"metaData":True, "nodes":True}):
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

    if fileNames is None:
        fileNames = [x for x in input("which file would you like to use?(please enter the name of the excel file "
                                          "or files seperated by commas)\n").split(',')]

    data = FilterData.filterAndExtractData(fileNames, settings, debug=debug)
    if debug: print("done extracting data")

    Annonymisation.annonymiseExtracted(data)
    if debug: print("done making data anonymous")

    output = DataProcessing.processDataExtracted(data, settings['learningpaths'],filterQuickClicks,
                                                 filesToSave=filesToSave)
    # ToDo if visualisation's input is fixed, output['nodes'] can be used instead of loading nodes.json each time

    for path in settings['learningpaths']:
        Visualisation.learningpathFlowthrough(settings['learningpaths'][path])
        Visualisation.hitsPerDayPerLearningPath(pathId=path, settings=settings)
        Visualisation.heatMapOfGivenNodes(givenNodes=settings['learningpaths'][path]['list'],
                                          filename="heatmapPath"+str(path), colors=heatMapColor)
        if debug: print("done for path " + str(path))
    if debug: print(settings)
    DataProcessing.csvExports(nameFilename, learningPaths=settings['learningpaths'], functions=functions)

    if not functions is None:
        # ToDo run any of the unused visualisations
        if debug: print("not implemented")
        if "all" in functions or "totalHitsPerDayGraph" in functions:
            Visualisation.hitsPerDay()
        if "usersPerDayPerLearningPath" in functions: # not all, because if we want all, they should be on the same scale
            for path in settings['learningpaths']:
                Visualisation.usersPerDayPerLearningPath(path, settings=settings)
        if "all" in functions or "allUsersPerDayPerLearningPath" in functions:
            Visualisation.generateSetOfPathVisits(pathId=list(settings['learningpaths']), settings=settings,
                                                  debug=debug, users=True)
        if "all" in functions or "allHitsPerDayPerLearningPath" in functions:
            Visualisation.generateSetOfPathVisits(pathId=list(settings['learningpaths']),settings=settings, debug=debug)
        if "all" in functions or "allNodesFlowthrough" in functions:
            Visualisation.allNodesFlowthrough(debug=debug)  # ToDo there is currently no way to properly display this
        if ("all" in functions or "allNodesHeatMap" in functions) and 'heatmapParams' in functions:
            Visualisation.heatMapOfGivenNodes(**settings['heatmapParams'])

    # ToDo nodes.json could be saved in such a way that the same nodes.json is not generated twice for the same settings
    if "all" not in filesToSave: # remove any unwanted files
        if "metaData" not in filesToSave:
            os.remove("outputs/metaData.json")
        if "nodes" not in filesToSave:
            os.remove("outputs/nodes.json")

    # knownPaths=['8', '135', '136', '144', '143', '142', '141', '140', '148', '145', '137', '139', '138', '146']
    # Visualisation.generateSetOfPathVisits(knownPaths, metaData=output["metaData"])
    # Visualisation.learningpathFlowthrough(settings["learningpaths"]['8'])
    # DataProcessing.csvExports(metaData=output["metaData"], learningPaths=settings["learningpaths"])
    # for path in knownPaths:
    #     Visualisation.heatMapOfGivenNodes(givenNodes=settings['learningpaths'][path]['list'],
    #                                   threshholdFlowthroughValue=2, colors="jet",filename="heatmap" + str(path))




if __name__ == "__main__":
    if len(sys.argv) > 1:
        settingsFileName = sys.argv[1]
        with open(settingsFileName, 'r') as settingsFile:
            settings = json.load(settingsFile, object_hook=datetime_parser)
        learningpaths = settings['learningpaths'] if 'learningpaths' in settings else {}
        period = settings['period']
        fileNames = settings['dataFilename']
        nameFileName = settings['nameFilename']
        students=settings['students'] if 'students' in settings else None
        heatMapColor = settings['heatMapColor'] if 'heatMapColor' in settings else "jet"
        debug=settings['debug'] if 'debug' in settings else False
        functions = dict([(x,True) for x in settings['functions']]) if 'functions' in settings else None
        filesToSave = settings['filesToSave'] if 'filesToSave' in settings else {"metaData":True, "nodes": True}
    else:
        learningpaths = {"8":
                            {"starting time": "2019-09-03 08:45:00",
                              "list": [11941, 11894, 11833, 11800, 11832, 11801, 11853, 11799, 12070], "id": "8"},
                        "135":
                            {"starting time": "2019-09-03 09:30:00",
                             "list": [12021, 11927, 11835, 11926, 11866, 12038, 11958, 11777, 11980], "id": "135"},
                         }
        startDate=dateutil.parser.parse("2019-09-01")
        endDate=dateutil.parser.parse("2019-09-23")
        period = {"usePeriod": True, "startDate": startDate, "endDate": endDate}
        fileNames=["gis_rs_v2_tracking_export3_10_2019.xlsx"]
        nameFileName="configurationFiles/gis_rs_v2_names.csv"
        students=None
        heatMapColor = "jet"
        debug=False
        functions = None
        filesToSave = {"metaData":True, "nodes": True}
    main(debug=debug, nameFilename=nameFileName, students=students,
         learningPaths=learningpaths, period=period, fileNames=fileNames,
         heatMapColor=heatMapColor, functions=functions, filesToSave=filesToSave)
    # Visualisation.hitsPerDayPerLearningPath(max_value=500)
    # ToDo add another argument to the settings to see which additional functions should be run
    # metaData=None
    # with open("outputs/metaData.json", "r") as input:
    #     metaData=json.load(input, object_hook=datetime_parser)
    # Visualisation.generateSetOfPathVisits(metaData=metaData)
    # Visualisation.allNodesFlowthrough()
