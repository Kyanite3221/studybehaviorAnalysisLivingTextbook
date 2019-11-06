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
		"startPeriod": "yyyy-mm-dd hh:MM:ss",
		"endPeriod": "yyyy-mm-dd hh:MM:ss"
	}

"learningpaths"(optional):
	{
		id: {
			"starting time": "yyyy-mm-dd hh:MM:ss",
			"list": [ concept id ]
			}
	}

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
			conceptOriginsCSV
			
			dashboardMetaDataCSV is executed by default, but can be left out by entering an empty array)
	],

"filterSuccessiveHits": bool,

"filesToSave": 
	[
		fileName(any out of:
			all,
			users,
			nodes,
			paths,
			metaData
			
			nodes and metaData are always generated, but if they are not in the array, they are removed after execution)
	]
}