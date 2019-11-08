to run a test, execute the following command:
"python Main.py"
------------------------------------------------------------------------------------
dependancies:
------------------------------------------------------------------------------------
the program requires the following libaries:
	openpyxl
	dateutil(python-dateutil)
	matplotlib
	pandas
-------------------------------------------------------------------------------------
usage
-------------------------------------------------------------------------------------
to execute normally, run the file as following: python Main.py "settingsFileLocation"
The syntax of the settings file is a JSON file with the following parameters:
{
"nameFilename": name of the file which maps ID's to names

"dataFilename": [name of the excel data file, this can be an array of names or a single name]

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

"functions"(optional): (
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
			
			allHitsPerDayPerConceptGraph(requires conceptHitsParams),
			hitsPerDayPerConceptGraph(requires conceptHitsParams),
			usersPerDayPerLearningPath,
			allUsersPerDayPerLearningPath(same scale),
			allHitsPerDayPerLearningPath(same scale),
			allNodesFlowthrough,
			allNodesHeatMap(requires heatMapParams to be filled in, otherwise no output)
			
			(dashboardMetaDataCSV is executed by default, but can be left out by entering an empty array)
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
-----------------------------------------------------------------------------
description of input
-----------------------------------------------------------------------------
required input
	"learningpaths"
		these are the pre-determined learningpaths, the required information is:
		the internal ID(which can be found in the URL of the view learningpath page: https://ltb.itc.utwente.nl/page/[study area]/learningpath/show/[learningpathId]
		the lecture moment, when did the students start following the path
		a list of the concepts in the learningpath(can be found in the URL: https://ltb.itc.utwente.nl/page/[study area]/concept/[conceptId]
		
		This must at least be an empty dictionary, but that will mean that the standard output is virtually useless
	"period"
		this is the time period in which the data is to be examined.
		The usePeriod flag is used to indicate if the data provided in the tracking export needs to be limited to a time frame, or if we want lifetime information
		most graphs will be generated with a x-axis which describes time, the bounds for these graphs are given in the form of a startDate and an endDate.
		Even if the usePeriod flag is set to false, the graphs will have the date range from startDate to endDate. the only way to circumvent this would be finding out what the earliest and last days are and then setting startDate and endDate accordingly.
	"dataFileName"
		This is the name or names of the tracking export excel file.
		These files can be generated from the LTB under the data tab.
	"nameFilename"
		This is the name of the file containing the names of the concepts in the study area.
		This file can be downloaded under the data->export tab with the Concept(with id) export type
optional input (defaults are between brackets)
	"students" (empty blacklist)
		This is a method to filter data based on certain student groups.
		The filtering can be done either by whitelist or by blacklist, meaning that either everyone on the list is accepted and nobody else, or the other way around.
		The actual filtering is done through a list of arguments, each element in said list can be either of the "email" type or of the "regex" type.
		the "email" type means that an exact match will be the qualifier for deletion or addition, so if the value is "john@example.net" only entries with that exact userId are filtered.
		the "regex" type means that regex matching is used to filter, more information on this can be found here: https://www.w3schools.com/python/python_regex.asp . This can be used to filter all teachers for example, with the regex value: "[^@]*@utwente.nl$" this means that any userId ending in "@utwente.nl" will be filtered.
	"debug" (false)
		this is used to print information in the terminal for debugging purposes.
	"heatMapColor" (jet)
		a color for the heatmaps can be set here, this must be a matplotlib colormap, which can be found here: https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html
	"filterSuccessiveHits" (false)
		this filters rapid successive pagehits, meaning that if the same page is opened in 60 seconds, it is not counted as a new hit, or if 2 pages are opened in the span of a second, only the second one is registered.
	"filesToSave" (metaData and nodes)
		This allows the user to select which files are saved upon completion
		users
			The filtered data in a JSON format with additional information to make the graph generation simpler
			this could be usefull to more closely observe an individual user's browsing behaviour, although it is annonymous
		nodes
			This file is used for the graph generation and contains information on each of the concepts, how often they have been visited, which learningpaths it is in and more.
			The file can be used again for graph generation and is quite human readable with the use of http://jsonviewer.stack.hu/
		paths
			This file contains the paths that users took through the concepts and which learningpath they were visiting at the time, based on previous pages visited and links clicked.
			It is currently not used, but could be used to more closely examine user's browsing behaviour
		metaData
			This file contains a lot of information about the data, like the total amount of concepts visited, where users came from(page origins), hits per day and more
			quite usefull and readable through http://jsonviewer.stack.hu/
		all
			this retains all of the above
		
		If the list is empty, all files will be deleted after usage.
	"functions" (dashboardMetaDataCSV, heatmap per learningpath, flowthrough per learningpath and pathHitsPerDay)
		Common usage of the program only produces 1 file +3 per learningpath, but more files can be produced:
		files
			totalHitsPerDayCSV
				This produces a .csv file containing how many hits there were each day in the entire study area
			pathHitsPerDayCSV
				similar to totalHitsPerDayCSV, except with only the concepts which are in a learning path
				produces one file per given learningpath
			dailyOriginsCSV
				Produces originDataDay.csv which describes where every user came from:
					"general"
						general link click, this can be a link in another concept or a link in the concept list
					"external"
						external link click, this can be a link in a powerpoint or on another website, outside of the living textbook.
						due to limitations to the tracking system, this number might be greater than the actual number of people which came to the LTB though external links, this is due to the undeterministic nature of internet connections and delays.
					"conceptBrowser"
						Concept browser concept clicks, these are people who came to the concept by clicking on it in the concept browser
					"learningpathBrowser"
						Learningpath browser concept clicks, theser are people who came to the concept by clicking on it in the learningpath window
					"total"
						the sum of all the concept hits in a day
				This is usefull to see how students study and how it varies through the course.
			odDataCSV
				This creates an Origin Destination csv file, where you can see how many people went from concept A to concept B.
				Useful for creating one's own heatmaps or other visualisations
			totalOriginsJSON
				This updates metaData.json with information about where people come from
				Like dailyOriginsCSV, except in total
			dashboardMetaDataCSV
				This creates metaDataDashBoard.csv, which contains information that can be put on an analyst's dashboard
				contains a usercount and the total number of hits in a period per learningpath
			conceptOriginsCSV
				Produces originsPerConcept.csv, which describes how users come to each concept.
				Similar to dailyOriginsCSV, except ordered by concept instead of by day.
		graphs
			allHitsPerDayPerConceptGraph(requires conceptHitsParams)
				This generates a histogram for each concept specified in conceptHitsParams, detailing the number of hits per day and the number of users
				All of these graphs will have the same scale so they are easy to compare.
			hitsPerDayPerConceptGraph(requires conceptHitsParams)
				Same as allHitsPerDayPerConceptGraph, except each has its own scale, meaning they are easier to read, but not as comparable
			usersPerDayPerLearningPath
				Generates a histogram for each learningpath with information about how many users there were each day and how many of those are new.
				Useful to look into study behaviours
			allUsersPerDayPerLearningPath
				same as usersPerDayPerLearningPath, but with the same scale so they are easy to compare
			allHitsPerDayPerLearningPath
				Generates a histogram for each learningpath detailing how many hits each concept had in a day.
				These are different from the ones generated by default in that they have the same scale for easy comparison.
			allNodesFlowthrough
				Generates Flowthrough.js which functions as pathFlowthrough, except for all concepts.
				Currently not usable because the visualisation is not sufficient to make the data comprehensible.
			allNodesHeatMap(requires heatMapParams)
				Generates a heatmap of all concepts that fall within the specifications of heatMapParams.
				This will become unreadable very quickly, so be careful to specify the parameters to fit your needs as closely as posible.
			all
				this generates all files and graphs, picking the same scale version where availible.
	"conceptHitsParams"(no default)
		This is a list of all concepts for which a histogram should be generated
		Has no use if allHitsPerDayPerConceptGraph or hitsPerDayPerConceptGraph is not run
	"heatMapParams"(no default)
		of the following arguments, as few or as many as desired can be given:
		"givenNodes"
			A list of the concepts which should apear in the heatmap, can also be determined by threshholdHitsValue
		"threshholdFlowthroughValue" default 0
			If the number of hits from A to B has a value lower than the threshholdFlowthroughValue, it is rounded down to 0
		"threshholdHitsValue": default 0,
			This is used to determine which concepts should be used if givenNodes is left out
			The generated list of concepts will be every concept with a number of hits(page visits) equal to or greater than the threshholdHitsValue
		"colors" default "jet"
			name of the matplotlib colormap, defaults to
		"filename": default "outputs/heatmap.png"
			the name of the desired output file
		"debug" default false
			overwrites the global debug