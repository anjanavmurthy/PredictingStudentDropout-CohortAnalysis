# PredictingStudentDropout-CohortAnalysis
The basic idea of the project is to identify the socio economic factors due to which students of government schools decide to discontinue their education and predict the students who are likely to dropout. By Identifying the students that are likely to dropout, suitable actions can be taken to retain them and continue their education.


-Command to execute the program when in directory of files and folders,
	python app.py

-Requirements:
    Python
    flask
    pandas
    numpy
    sklearn
    shutil
    glob
    pickle
    plotly
    werkzeug

-Files and Folders:

    Project_Code
    [__ app.py  -> File containing the Flask code to execute the app
    [__ cohorts.csv -> Cohort Groups for Urban Areas
    [__ rural_cohorts.csv -> Cohort Groups for Rural Areas
    [__ Random_Foresturb.pkl -> Random Forest Pickle file for Urban Areas
    [__ Random_Forest.pkl -> Random Forest Pickle file for Rural Areas
    [__ Urban_School.csv -> Sample School Students Dataset
    [__ static -> Folder where graph images are stored
    [__ templates -> Folder that Contains the HTML files
        [____ category.html -> HTML file for choosing group
        [____ statistics.html -> HTML file for graphs for an entire school
        [____ counter_measures.html -> HTML file for counter measures
        [____ dataframe.html -> HTML file displaying the results
        [____ home.html -> HTML file for choosing area
        [____ statistics_class.html -> HTML file for displaying a graph for a single class
        [____ upload.html -> HTML file to upload a file
    [__ uploads ->Folder that stores Uploaded files
