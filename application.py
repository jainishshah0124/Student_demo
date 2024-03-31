from flask import Flask, render_template,request,g,redirect,url_for
import requests
import JSON
import os
import cv2
import numpy
import shutil
import pyttsx3
import argparse
import threading
import face_recognition
from imutils import paths
from playsound import playsound
import base64
from datetime import date
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('registration.html')

@app.route('/fill_class')
def fill_class():
    print(list_classes())
    print(retrive_data(list_classes()))
    data=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/?select={"enrollment_ref":true,"first_name":true,"last_name":true,"employee_id":true}',"",'GET').text)["data"]
    filtered_data = [record for record in data]
    freshData=[]
    for each in filtered_data:
        temp=[]
        temp.append(each['first_name'])
        temp.append(each['last_name'])
        temp.append(each['employee_id'])
        freshData.append(temp)

    #print(freshData)
    localStorage_data = {
        "classes": list_classes(),
        "colors": '{}',
        "debug": "honey:core-sdk:*",
        "students": json.dumps(retrive_data(list_classes())),
        "toAssignstud" : freshData
    }
    print(localStorage_data)
    return render_template('fill_class.html',localStorage_data=localStorage_data)

@app.route('/add_class',methods=['POST'])
def add_class():
    data={
        "start_time" : request.form['Time'],
        "subject_code" : request.form['newClassName']
    }
    response = JSON.sendJSONCALL('https://us-east-2.aws.neurelo.com/rest/class_details/__one',data,'POST')
    return redirect(url_for('attendance'))

@app.route('/imageCapture',methods=['POST'])
def imageCapture():
    url = 'https://us-east-2.aws.neurelo.com/rest/employees/__one?select={"$scalars":true,"$related":true}'

    # Define the request body
    data = {
        "employee_id": int(request.form['employee_id']),
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "address": request.form['address'],
        "email": request.form['email'],
        "dob": request.form['dob'],
        "gender": request.form['gender'],
        "is_dataset_avaliable": "N",
        "is_model_avaliable": "N",
        "phone": request.form['phone'],
        "photo_path": "",
        "datasets_ref": {
            "create": {
                "created_date": date.today().strftime("%Y-%m-%d"),
                "number_of_images": request.form['number_of_images'],
                "full_name": request.form['first_name'] + " " + request.form['last_name']
            }
        }
    }

    # Make the POST request
    response = JSON.sendJSONCALL(url,data,'POST')
    print(data)
    # Print the response
    print('response status code : ' + str(response.status_code))
    if(response.status_code==201):
        return render_template('capture.html',employee_id=request.form['employee_id'])
    else:
        return render_template('registration.html',error=response.text)

@app.route('/save_image',methods=['POST','GET'])
def save_image():
    folder_name="Datasets"
    image_data = request.form['imageData']
    employee_id = request.form['employee_id']
    print(employee_id)
    path="Datasets/"+employee_id
    # Extract base64-encoded image data
    _, encoded_data = image_data.split(',', 1)
    decoded_data = base64.b64decode(encoded_data)

    # Save the image to a file
    with open(f'{path}.jpg', 'wb') as f:
        f.write(decoded_data)
    print(JSON.updateJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/'+employee_id,{"photo_path":path+".jpg","is_dataset_avaliable": "Y"},'PATCH').text)
    return redirect(url_for('attendance'))

def list_classes():
    class_dtl=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/class_details/',"",'GET').text)["data"]
    
    classes=[]
    for dtl in class_dtl:
        classes.append(dtl["subject_code"])
    return classes

@app.route('/attendance')
def attendance():
    
    localStorage_data = {
        "attendanceData": '[]',
        "classes": json.dumps(list_classes()),
        "colors": '{}',
        "debug": "honey:core-sdk:*",
        "students": json.dumps(retrive_data(list_classes()))
    }

    return render_template('attendance.html',localStorage_data=localStorage_data)

#retrive each students according to subject
def retrive_data(classes):
    students_data = {}
    for each in classes:
        student=json.loads(JSON.selectJSONCALL(f'https://us-east-2.aws.neurelo.com/rest/enrollment?filter={{"class_id":{{"contains":"{each}"}}}}',"",'GET').text)["data"]
        students_data[each] = []
        for eachstud in student:
            data=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/'+str(eachstud["employee_id"]),"",'GET').text)["data"]
            employee = {
                "name" : data["first_name"] + " " +data["last_name"],
                "rollNumber":data["employee_id"]
            }
            students_data[each].append(employee)
        employee=[]
    return students_data

@app.route('/submit_fill_class',methods=['POST','GET'])
def submit_fill_class():
    class_selected=request.form.getlist('classSelector')
    checked_students = request.form.getlist('students')
    rollList = request.form.getlist('localStorageData')[0].split(',')
    print(rollList)
    print(checked_students)
    data=[]
    for each in checked_students:
        if each not in rollList:
            temp={
            "class_id":class_selected[0],
            "employee_id":int(each)
            }
            data.append(temp)
    print(data)
    response = JSON.sendJSONCALL('https://us-east-2.aws.neurelo.com/rest/enrollment',data,'POST')
    
    temp=[]
    for each in rollList:
        if each not in checked_students:
            temp.append(int(each))
    
    data={
        "class_id":class_selected[0],
        "employee_id" : {"in":temp}
    }
    responsedel = JSON.deleteJSONCALL(f'https://us-east-2.aws.neurelo.com/rest/enrollment?filter={json.dumps(data)}','','DELETE')
    if(str(response.status_code)=='201' and str(responsedel.status_code)=='201'):
        return redirect(url_for('attendance'))
    return 'Some error occured'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/start_attendance')
def start_attendance():
    data=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/',"",'GET').text)["data"]
    class_dtl=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/class_details/',"",'GET').text)["data"]
    
    classes=[]
    for dtl in class_dtl:
        classes.append(dtl["subject_code"])
    student=retrive_data(classes)
    
    localStorage_data = {
        "attendanceData": '[]',
        "classes": json.dumps(classes),
        "colors": '{}',
        "debug": "honey:core-sdk:*",
        "students": json.dumps(student)
    }
    return render_template('start_attendance.html',localStorage_data=localStorage_data)

if __name__ == '__main__':
    app.run(debug=True,port=5001)
