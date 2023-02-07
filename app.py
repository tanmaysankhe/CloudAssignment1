
#imports
import os
from azure.storage.blob import BlobServiceClient
from flask import Flask, request, redirect, render_template
import pandas as pd
import math


app = Flask(__name__)


#server config
connect_str = "DefaultEndpointsProtocol=https;AccountName=assignmentcloud;AccountKey=2vDkYVGId7/pMg4Xq0lT7eB5av6qX3HF1EhNH0zfKA3krX99WSZUFDfw89nfo96obk8IyjEtRy9H+ASt2X9lPw==;EndpointSuffix=core.windows.net" # retrieve the connection string from the environment variable
container_name = "assignment1" # container name in which images will be store in the storage account
images_list = []
already_downloaded = True
image_url = f"https://assignmentcloud.blob.core.windows.net/assignment1/"


#server connection
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)
try:
    container_client = blob_service_client.get_container_client(container=container_name) 
    container_client.get_container_properties()
except Exception as e:
    print(e)
    print("Creating container...")
    container_client = blob_service_client.create_container(container_name) 

blob_items = container_client.list_blobs()
for blob in blob_items:
    blob_client = container_client.get_blob_client(blob=blob.name) # get blob client to interact with the blob and get blob url
    images_list.append(blob_client.blob_name)


people_sas = f"https://assignmentcloud.blob.core.windows.net/assignment1/people.csv?sp=r&st=2023-02-06T15:25:05Z&se=2023-02-08T23:25:05Z&sv=2021-06-08&sr=b&sig=pzgKzrXvq7LCjHFcOWlDZw6KEo5TSOclPaPaEfuYZYk%3D"
all_data = pd.read_csv(people_sas)
all_data = all_data.fillna(" ")
username_filter = None
salary_filter = None
# x = data.query('Name == "Meena"')

print(all_data)
datalist = []
for i in all_data.values.tolist():
    x = {"name":None if i[0] == " "  else i[0], 
        "state":None if i[1] == " "  else i[1], 
        "salary": 0 if i[2] == " "  else int(i[2]), 
        "grade":None if i[3] == " "  else i[3], 
        "room":None if i[4] == " "  else i[4], 
        "telnum":None if i[5] == " "  else i[5], 
        "picture":None if i[6] == " "  else i[6], 
        "keywords":None if i[7] == " "  else i[7]}
    datalist.append(x)

print(datalist)

def filter(name=None, salary=None):

    print(name, salary)
    dis_data = datalist[:]
    if name: 
        dis_data = [x for x in dis_data if x['name'] == name]
    if salary:
        dis_data = [x for x in dis_data if x['salary'] >= int(salary)]

    print(dis_data)
    return(dis_data)


@app.route("/")
def view_photos():
    global username_filter, salary_filter
    img_html = "<div style='display: flex; justify-content: space-between; flex-wrap: wrap;'>"
    data = filter(username_filter, salary_filter)
    
    for d in data:
        image_src = image_url + "temp.png"
        if d["picture"] in images_list:
            image_src = image_url + d["picture"]
        
        img_html += "<div style='border: 1px solid black; margin:10px; padding:10px'><img src='{}' width='auto' height='200' style='margin: 0.5em 0;'/>".format(image_src)
        img_html += f"<div>Name : {d['name']}</br>Salary : {d['salary']}</br>Keywords:{d['keywords']}</br></div></div>"
   
    # return the html with the images
    return render_template("index.html",img_html = img_html)

#flask endpoint to upload a photo
@app.route("/upload-photos", methods=["POST"])
def upload_photos():
    filenames = ""

    for file in request.files.getlist("photos"):
        try:
            container_client.upload_blob(file.filename, file,overwrite=True) 
            filenames += file.filename + "<br /> "
        except Exception as e:
            print(e)
            print("Ignoring duplicate filenames") # ignore duplicate filenames       
    return redirect('/')



@app.route('/handle_data', methods=['POST'])
def handle_data():
    global username_filter, salary_filter
    username = request.form['username']
    l_salary = request.form['l_salary']
    # h_salary = request.form['h_salary']

    username_filter = username
    salary_filter = l_salary

    return redirect('/')

