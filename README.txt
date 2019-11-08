to run a test, execute the following command:
"python Main.py"

the program requires the following libaries:
	openpyxl
	dateutil(python-dateutil)
	matplotlib
	pandas

to execute normally, use the following parameters: (Not yet fully implemented)
{
"nameFilename": name of the file which maps ID's to names

"dataFilename": [name of the excel data file, this can be an array of names]

"period":
	{
		"usePeriod": bool,
		"startDate": "yyyy-mm-dd hh:MM:ss",
		"endDate": "yyyy-mm-dd hh:MM:ss"
	}

"learningpaths"(optional):
	{
		id: {
			"starting time": "yyyy-mm-dd hh:MM:ss",
			"list": [ concept id ]
			}
	} if multiple learningpaths are given, the graphs that are generated have the same scale, if this is not desired, hitsPerDayPerLearningPath can be added to the functions list, this will overwrite the same scale versions

"students"(optional):
	{
	"whitelist": bool,
	"list": 
		[
			{
				"type": "email" or "regex",
				"value": string
			}
		]}

"functions"(optional):
	[
		functionName(any out of:
			all,
			totalHitsPerDayCSV,
			pathHitsPerDayCSV,
			dailyOriginsCSV,
			odDataCSV,
			totalOriginsJSON,
			dashboardMetaDataCSV,
			conceptOriginsCSV,
			
			allHitsPerDayPerConceptGraph(requires conceptHitsParams,
			hitsPerDayPerConceptGraph(requires conceptHitsParams,
			usersPerDayPerLearningPath,
			allUsersPerDayPerLearningPath(same scale),
			allHitsPerDayPerLearningPath(same scale),
			allNodesFlowthrough,
			allNodesHeatMap(requires heatmapParams to be filled in, otherwise no output)
			
			dashboardMetaDataCSV is executed by default, but can be left out by entering an empty array)
	],

"filterSuccessiveHits"(optional): bool,

"filesToSave"(optional): 
	[
		fileName(any out of:
			all,
			users,
			nodes,
			paths,
			metaData
			
			nodes and metaData are always generated, but if they are not in the array, they are removed after execution)
	],
"heatMapColor"(optional): name of the matplotlib colormap, defaults to jet
"conceptHitsParams"(optional):[conceptIds],
"heatMapParams"(optional):
	{
		"givenNodes"(optional): [conceptIds],
		"threshholdFlowthroughValue": int default 0,
		"threshholdHitsValue": int default 0, important if you want to map more than just one learningpath,
		"colors": name of the matplotlib colormap, defaults to jet,
		"filename": nameOfFile, defaults to "outputs/heatmap.png"
		"debug": bool
	}
}