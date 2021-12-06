from __future__ import print_function
from flask import Flask, render_template, request, redirect, url_for, abort, session, Response
from werkzeug.utils import secure_filename
import os
import pandas as pd
import pickle
import sklearn
from flask import send_file
import io
import multiprocessing
import plotly.express as px
import numpy
import plotly.graph_objs as go
from plotly.offline import iplot
import shutil
import glob
import sys
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.csv', '.xlsx']
app.config['UPLOAD_PATH'] = 'uploads'
class student:
    def __init__(self,area=2,group=1):
        self.area=area
        self.group=group
stu=student()
@app.route("/", methods=['GET', 'POST'])
def home():
    global stu
    if request.method == 'POST':
        if request.form.get('action1') == 'Rural':
            stu.area=1
            return render_template("category.html")
        if  request.form.get('action2') == 'Urban':
            stu.area=2
            return render_template("category.html")
    return render_template("home.html")
@app.route("/groups", methods=['GET', 'POST'])
def groups():
    global stu
    if request.method == 'POST':
        if request.form.get('action1') == 'School':
            stu.groups=1
            return render_template("upload.html")
        if  request.form.get('action2') == 'Class':
            stu.groups=2
            return render_template("upload.html")
    return render_template("home.html")
@app.route('/upload', methods=(["POST"]))
def upload_files():
    folder_path = (r'uploads/')
    test = os.listdir(folder_path)
    for images in test:
        if images.endswith(".csv") or images.endswith(".xlsx"):
            os.remove(os.path.join(folder_path, images))
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('html_table'))

@app.route("/filter" , methods=['GET', 'POST'])
def filter():
    df=pd.read_excel("Results.xlsx")
    attribute = request.form.get('attributes')
    category = request.form.get('attribute-cat')
    df = df.iloc[: , 1:]
    if attribute == "SID":
        category = request.form.get('SID_val')
        res=df.loc[df[attribute] == int(category)]
    elif attribute == "Class":
        attribute="Current Class"
        res=df.loc[df[attribute] == int(category)]
    elif attribute=="All":
        return render_template("dataframe.html", column_names=df.columns.values, row_data=list(df.values.tolist()),zip=zip)
    else:
        res=df.loc[df[attribute] == category]
    return render_template("dataframe.html", column_names=res.columns.values, row_data=list(res.values.tolist()),zip=zip)

@app.route('/get_res', methods=("POST","GET"))
def html_table():
    mypath='uploads'
    p=list()
    for filename in os.listdir(mypath):
        p.append(os.path.join(mypath, filename))
    df=pd.read_csv(p[0])
    #df=pd.read_csv(r'C:/Users/Sarvesh/app/uploads/Dataset_Rural_Enc.csv')
    res=get_cohorts_dataframe(df)
    res_df=pd.DataFrame.from_dict(res,orient='index').transpose()
    global r_df
    r_df=res_df.head(len(df))
    if os.path.exists('C:/Users/Sarvesh/Desktop/app/apps/Results.xlsx'):
        os.remove('C:/Users/Sarvesh/Desktop/app/apps/Results.xlsx')
    r_df.to_excel("Results.xlsx")
    return render_template("dataframe.html", column_names=r_df.columns.values, row_data=list(r_df.values.tolist()),zip=zip)
def get_results(features):
    global stu
    if stu.area==2:
        cohorts=pd.read_csv(r"cohorts.csv")
        filename="DT_model_2.pkl"
    if stu.area==1:
        cohorts=pd.read_csv(r"rural_cohorts.csv")
        filename="Random_Forestrur.pkl"
    loaded_model = pickle.load(open(filename, 'rb'))
    result=loaded_model.predict([features])
    cg=cohorts.loc[cohorts["CID"]==result[0]]
    return cg["CID"],cg["Reason"],cg["Dropout Rate"]
def get_cohorts_dataframe(data):
    result={"SID":list(),"Gender":list(),"Current Class":list(),"Current Year Rate":list(),"2nd year Rate":list(),"3rd year Rate":list(),"Risk":list(),"Class Drop":list(),"Reason":list()}
    for i in range(len(data)):
        X=data.drop(["SID","CID"],axis=1)
        f=list(X.iloc[i])
        grade=list(f)[4]
        result["SID"].append(data["SID"][i])
        result["Current Class"].append(grade)
        if data["GENDER"][i]==0:
            result["Gender"].append("Female")
        else:
            result["Gender"].append("Male")
        global stu
        if stu.area==2:
            res=get_cohorts_urb(f,result)
        if stu.area==1:
            res=get_cohorts_rur(f,result)
    return res
def get_cohorts_urb(f,result):
    grade=f[4]
    clsdrop=dict()
    if(int(grade)==7):
        l=get_results(f)
        for j in range(len(l)):
            x=list(l[j])[0]
            if j==0:
                cid=x
            if j==1:
                result["Reason"].append(x)
            if j==2:
                x=float(x)
                result["Current Year Rate"].append(x)
        clsdrop["7"]=x
        cdrp=max(clsdrop, key=clsdrop.get)
        if clsdrop[cdrp] >=0.065:
            risk="High Risk"
        elif clsdrop[cdrp] <= 0.04:
            risk="Low Risk"
        else:
            risk="Medium Risk"
        result["Risk"].append(risk)
        result["Class Drop"].append(int(cdrp))
        result["2nd year Rate"].append('NA')
        result["3rd year Rate"].append('NA')
    elif(int(f[4])==6):
        c=6
        for i in range(2):
            f[4]=c
            l=get_results(f)
            for j in range(len(l)):
                x=list(l[j])[0]
                if j==0:
                    cid=x
                if j==1:
                    result["Reason"].append(x)
                if j==2:
                    x=float(x)
                    if i == 0:
                        result["Current Year Rate"].append(float(x))
                        clsdrop[c]=x
                    else:
                        result["2nd year Rate"].append(float(x))
                        clsdrop[c]=x
                    result["3rd year Rate"].append('NA')
            c=c+1
        cdrp=max(clsdrop, key=clsdrop.get)
        if clsdrop[cdrp] >=0.065:
            risk="High Risk"
        elif clsdrop[cdrp] <= 0.04:
            risk="Low Risk"
        else:
            risk="Medium Risk"
        result["Risk"].append(risk)
        result["Class Drop"].append(int(cdrp))
    else:
        c=int(f[4])
        for i in range(3):
            f[4]=c
            l=get_results(f)
            for j in range(len(l)):
                x=list(l[j])[0]
                if j==0:
                    cid=x
                if j==1:
                    result["Reason"].append(x)
                if j==2:
                    x=float(x)
                    if i == 0:
                        result["Current Year Rate"].append(float(x))
                        clsdrop[c]=x
                    elif i == 1:
                        result["2nd year Rate"].append(float(x))
                        clsdrop[c]=x
                    else:
                        result["3rd year Rate"].append(float(x))
                        clsdrop[c]=x
            c=c+1
            cdrp=max(clsdrop, key=clsdrop.get)
        if clsdrop[cdrp] >=0.065:
            risk="High Risk"
        elif clsdrop[cdrp] <= 0.04:
            risk="Low Risk"
        else:
            risk="Medium Risk"
        result["Risk"].append(risk)
        result["Class Drop"].append(int(cdrp))
    #r = raw string literal
    return result
def get_cohorts_rur(f,result):
    grade=f[4]
    clsdrop=dict()
    if(int(grade)==7):
        l=get_results(f)
        for j in range(len(l)):
            x=list(l[j])[0]
            if j==0:
                cid=x
            if j==1:
                result["Reason"].append(x)
            if j==2:
                x=float(x)
                result["Current Year Rate"].append(x)
        clsdrop["7"]=x
        cdrp=max(clsdrop, key=clsdrop.get)
        if clsdrop[cdrp] >=0.7:
            risk="High Risk"
        elif clsdrop[cdrp] <=0.4:
            risk="Low Risk"
        else:
            risk="Medium Risk"
        result["Risk"].append(risk)
        result["Class Drop"].append(int(cdrp))
        result["2nd year Rate"].append('NA')
        result["3rd year Rate"].append('NA')
    elif(int(f[4])==6):
        c=6
        for i in range(2):
            f[4]=c
            l=get_results(f)
            for j in range(len(l)):
                x=list(l[j])[0]
                if j==0:
                    cid=x
                if j==1:
                    result["Reason"].append(x)
                if j==2:
                    x=float(x)
                    if i == 0:
                        result["Current Year Rate"].append(float(x))
                        clsdrop[c]=x
                    else:
                        result["2nd year Rate"].append(float(x))
                        clsdrop[c]=x
                    result["3rd year Rate"].append('NA')
            c=c+1
        cdrp=max(clsdrop, key=clsdrop.get)
        if clsdrop[cdrp] >=0.7:
            risk="High Risk"
        elif clsdrop[cdrp] <=0.4:
            risk="Low Risk"
        else:
            risk="Medium Risk"
        result["Risk"].append(risk)
        result["Class Drop"].append(int(cdrp))
    else:
        c=int(f[4])
        for i in range(3):
            f[4]=c
            l=get_results(f)
            for j in range(len(l)):
                x=list(l[j])[0]
                if j==0:
                    cid=x
                if j==1:
                    result["Reason"].append(x)
                if j==2:
                    x=float(x)
                    if i == 0:
                        result["Current Year Rate"].append(float(x))
                        clsdrop[c]=x
                    elif i == 1:
                        result["2nd year Rate"].append(float(x))
                        clsdrop[c]=x
                    else:
                        result["3rd year Rate"].append(float(x))
                        clsdrop[c]=x
            c=c+1
            cdrp=max(clsdrop, key=clsdrop.get)
        if clsdrop[cdrp] >=0.7:
            risk="High Risk"
        elif clsdrop[cdrp] <=0.4:
            risk="Low Risk"
        else:
            risk="Medium Risk"
        result["Risk"].append(risk)
        result["Class Drop"].append(int(cdrp))
    #r = raw string literal
    return result
@app.route('/get_stats', methods=["POST"])
def get_stats():
    global stu
    #source-path to your app.py file 
    source = r'C:/Users/Sarvesh/Desktop/app/apps/' 
    #destination-path to your static folder
    destination = r'C:/Users/Sarvesh/Desktop/app/apps/static/'
    folder_path = (r'C:/Users/Sarvesh/Desktop/app/apps/static/')
    test = os.listdir(folder_path)
    #To remove images in static folder
    for images in test:
        if images.endswith(".png"):
            os.remove(os.path.join(folder_path, images))
    r_df=pd.read_excel("Results.xlsx")
    if stu.group==1:
        #Filtering Very High Risk Students
        hr=r_df.loc[r_df['Risk'] == "High Risk"]
        #Reason Count- Reason Distribution for Very High Risk
        reason_count = dict(hr["Reason"].value_counts())
        #Risk Distribution
        ri = dict(r_df["Risk"].value_counts())
        #Gender Distribution
        r = dict(hr["Gender"].value_counts())
        #pie chart for gender
        fig = px.pie(values=r.values(), names=r.keys())
        #fig.show()
        fig.write_image("pie_gender.png")
        #move image from current directory to static folder
        dest = shutil.move(str(source)+str("pie_gender.png"), destination)
        fig = px.pie(values=reason_count.values(), names=reason_count.keys())
        #fig.show()
        fig.write_image("pie_reason.png")
        dest = shutil.move(str(source)+str("pie_reason.png"), destination)
        risk = list(ri.keys())
        riskf = list(ri.values())
        data = [go.Bar(
        x = risk,
        y = riskf
        )]
        fig = go.Figure(data=data)
        fig.write_image("bar_risk.png")
        dest = shutil.move(str(source)+str('bar_risk.png'), destination)
        cdrop=dict(r_df["Class Drop"].value_counts())
        d = [go.Bar(
        x = list(cdrop.keys()),
        y = list(cdrop.values()),
        marker_color='yellow'
        )]
        fig = go.Figure(data=d)
        fig.write_image("bar_drop.png")
        dest = shutil.move(str(source)+str("bar_drop.png"), destination)
        return render_template("statistics.html")
    if stu.group==2:
        #Filtering Very High Risk Students
        hr=r_df.loc[r_df['Risk'] == "High Risk"]
        #Reason Count- Reason Distribution for Very High Risk
        reason_count = dict(hr["Reason"].value_counts())
        #Risk Distribution
        ri = dict(r_df["Risk"].value_counts())
        #Gender Distribution
        r = dict(hr["Gender"].value_counts())
        #pie chart for gender
        fig = px.pie(values=r.values(), names=r.keys())
        #fig.show()
        fig.write_image("pie_gender.png")
        #move image from current directory to static folder
        dest = shutil.move(str(source)+str("pie_gender.png"), destination)
        fig = px.pie(values=reason_count.values(), names=reason_count.keys())
        #fig.show()
        fig.write_image("pie_reason.png")
        dest = shutil.move(str(source)+str("pie_reason.png"), destination)
        risk = list(ri.keys())
        riskf = list(ri.values())
        data = [go.Bar(
        x = risk,
        y = riskf
        )]
        fig = go.Figure(data=data)
        fig.write_image("bar_risk.png")
        dest = shutil.move(str(source)+str('bar_risk.png'), destination)
        return render_template("statistics_rur.html")
@app.route('/get_cm', methods=["POST"])
def get_cm():
    return render_template("counter_measures.html")
@app.route('/get_df', methods=["POST"])
def get_df():
    return redirect(url_for('html_table'))
if __name__ == "__main__":
    try:
        app.run(debug=True)
    except:
        app.run(debug=True)