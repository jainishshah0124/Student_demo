from flask import Flask, render_template,request,g,redirect,url_for,jsonify,session,Response
from azure.storage.blob import BlobServiceClient
import JSON
import base64
from datetime import date
import json
import os
import asyncio
import websockets
import threading
import os
import uuid
import base64
import io
from PIL import Image
import face_recognition
import cv2
import numpy as np
import JSON
import json


app = Flask(__name__,template_folder=os.getcwd()+'/Templates')
app.secret_key = '12345'

@app.route('/')
def index():
    path=os.getcwd()+'/Templates'
    print(path)
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('registration.html')

@app.route('/fill_class')
def fill_class():
    data=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/?select={"enrollment_link_ref":true,"first_name":true,"last_name":true,"employee_id":true}',"",'GET').text)["data"]
    filtered_data = [record for record in data]
    freshData=[]
    for each in filtered_data:
        temp=[]
        temp.append(each['first_name'])
        temp.append(each['last_name'])
        temp.append(each['employee_id'])
        freshData.append(temp)

    classes=list_classes()
    listclass=[]
    listTime=[]
    i=0
    for each in classes:
        if i%2==0:
            listclass.append(each)
        else:
            listTime.append(each)
        i=i+1
    #print(freshData)
    localStorage_data = {
        "classes": listclass,
        "colors": '{}',
        "debug": "honey:core-sdk:*",
        "students": json.dumps(retrive_data(list_classes())),
        "toAssignstud" : freshData,
        "listTime":json.dumps(listTime)
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
    strong_connection_string = 'DefaultEndpointsProtocol=https;AccountName=cs41003200254e816d4;AccountKey=+fIuDGjtc3RqRYNfVM9qFKgR9opVMzMtaDMQsYDMKkferKuFXS/17cPdIkokd/IZaQaAvFdGYec3+AStKPQ4pw==;EndpointSuffix=core.windows.net'

    dataset_connection = BlobServiceClient.from_connection_string(strong_connection_string)
    # Save the image to a file
    with open(f'{path}.jpg', 'wb') as f:
        f.write(decoded_data)
    file_folder='./Datasets/'
    file_name=employee_id+'.jpg'
    blob_obj=dataset_connection.get_blob_client(container='datasets',blob=file_name)
    if blob_obj.exists():
        # If blob exists, delete it
        print(f"Deleting existing blob: {file_name}")
        blob_obj.delete_blob()
    with open(os.path.join(file_folder,file_name),mode='rb') as file_data:
        blob_obj.upload_blob(file_data)
    
    print(JSON.updateJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/'+employee_id,{"photo_path":path+".jpg","is_dataset_avaliable": "Y"},'PATCH').text)
    return redirect('/attendance')

def list_classes():
    class_dtl=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/class_details/',"",'GET').text)["data"]
    
    classes=[]
    for dtl in class_dtl:
        classes.append(dtl["subject_code"])
        classes.append(dtl["start_time"])
    return classes

@app.route('/attendance')
def attendance():
    if 'username' not in session:
            error_message = "Please Login"
            return render_template('login.html', error_message=error_message)
    
    #retrive Data
    strong_connection_string = 'DefaultEndpointsProtocol=https;AccountName=cs41003200254e816d4;AccountKey=+fIuDGjtc3RqRYNfVM9qFKgR9opVMzMtaDMQsYDMKkferKuFXS/17cPdIkokd/IZaQaAvFdGYec3+AStKPQ4pw==;EndpointSuffix=core.windows.net'

    dataset_connection = BlobServiceClient.from_connection_string(strong_connection_string)
    container_name = 'datasets'

    # Get the container client
    container_client = dataset_connection.get_container_client(container_name)

    # Define the local folder to save the downloaded images
    local_folder = './Datasets/'

    # Create the local folder if it doesn't exist
    os.makedirs(local_folder, exist_ok=True)

    # Iterate over blobs in the container
    for blob in container_client.list_blobs():
        # Construct blob client for the blob
        blob_client = dataset_connection.get_blob_client(container=container_name, blob=blob.name)
        
        # Define the local file path to save the downloaded blob
        local_file_path = os.path.join(local_folder, blob.name)
        
        # Check if the file already exists locally
        if os.path.exists(local_file_path):
            print(f"File '{blob.name}' already exists locally. Replacing...")
            os.remove(local_file_path)  # Remove the existing file
        
        # Download the blob to the local file system
        print(f"Downloading file: {blob.name}")
        with open(local_file_path, "wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())

    print("All files downloaded and replaced successfully.")
    classes=list_classes()
    listclass=[]
    listTime=[]
    i=0
    for each in classes:
        if i%2==0:
            listclass.append(each)
        else:
            listTime.append(each)
        i=i+1
    localStorage_data = {
        "attendanceData": '[]',
        "classes": json.dumps(listclass),
        "colors": '{}',
        "debug": "honey:core-sdk:*",
        "students": json.dumps(retrive_data(listclass)),
        "listTime":json.dumps(listTime)
    }

    return render_template('attendance.html',localStorage_data=localStorage_data)

#retrive each students according to subject
def retrive_data(classes):
    students_data = {}
    for each in classes:
        student=json.loads(JSON.selectJSONCALL(f'https://us-east-2.aws.neurelo.com/rest/enrollment_link?filter={{"class_id":{{"contains":"{each}"}}}}',"",'GET').text)["data"]
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
    response = JSON.sendJSONCALL('https://us-east-2.aws.neurelo.com/rest/enrollment_link',data,'POST')
    
    temp=[]
    for each in rollList:
        if each not in checked_students and each != '':
            temp.append(int(each))
    
    data={
        "class_id":class_selected[0],
        "employee_id" : {"in":temp}
    }
    print(json.dumps(data))
    responsedel = JSON.deleteJSONCALL(f'https://us-east-2.aws.neurelo.com/rest/enrollment_link?filter={json.dumps(data)}','','DELETE')
    if(str(response.status_code)=='201' and str(responsedel.status_code)=='201'):
        return redirect(url_for('attendance'))
    return 'Some error occured'

@app.route('/login',methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'admin' and password == 'admin':
        session['username'] = username
        return redirect('/attendance')
    else:
        error_message = "Invalid username or password. Please try again."
        return render_template('login.html', error_message=error_message)
    
@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page
    return redirect('/')
    

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

def delAttendance(subject_code,attendance_data,todayDate):
    list_enrollment=[]
    for item in attendance_data:
        each=int(item['rollNumber'])
        filter_json = json.dumps({"class_id":subject_code,"employee_id":each})
        url = f'https://us-east-2.aws.neurelo.com/rest/enrollment_link?select={{"auto_id":true}}&filter={filter_json}'
        print(url)
        response=json.loads(JSON.selectJSONCALL(url,"",'GET').text)["data"]
        if response:
            enrollment_id=response[0]["auto_id"]
            list_enrollment.append(enrollment_id)
            item["enrollment_id"]=enrollment_id
    #{{URL}}/rest/attendance?filter={"date":"2024-03-30","employee_id":{"in":[12,13]}}
    data={
        "date":todayDate,
        "employee_id" : {"in":list_enrollment}
    }
    responsedel = JSON.deleteJSONCALL(f'https://us-east-2.aws.neurelo.com/rest/attendance?filter={json.dumps(data)}','','DELETE')
    if str(responsedel.status_code)=='201':
        print('Records Deleted')
    print(attendance_data)
    return attendance_data

@app.route('/submitAttendance',methods=['POST'])
def submitAttendance():
    data = request.json
    attendance_data = data.get('attendanceData')
    subject_code = data.get('attendanceClass')
    todayDate = data.get('todayDate')
    print(todayDate)
    #Clear the old data with same date & same enrollment
    attendance_data=delAttendance(subject_code,attendance_data,todayDate)
    # Process the attendance data as needed
    data=[]
    for item in attendance_data:
        temp={
            "date":todayDate,
            "employee_id": item['enrollment_id']
        }
        if(item['status']=='present'):
            temp["status"] = "Present"
        elif(item['status']=='leave'):
            temp["status"] = "Late"
        else:
            temp["status"] = "Absent"
        data.append(temp)
    print(data)
    response = JSON.sendJSONCALL('https://us-east-2.aws.neurelo.com/rest/attendance',data,'POST')
    print(response.text)
    return jsonify({'message': 'Data received successfully'}), 200

@app.route('/calendar')
def calendar():
    if 'username' not in session:
            error_message = "Please Login"
            return render_template('login.html', error_message=error_message)
    return render_template('cal.html')

@app.route('/favicon.ico')
def favicon():
    # Return an empty response with status code 204 (No Content)
    return Response(status=204)


@app.route('/retriveAttendanceSummary',methods=['POST'])
def retriveAttendanceSummary():
    data = request.json
    subject=str(data.get('subject_code'))
    data=json.loads(JSON.selectJSONCALL(f'https://us-east-2.aws.neurelo.com/custom/attendance_count_summary?subject_code="{subject}"',"",'GET').text)["data"]
    
    print(data)
    return data

@app.route('/handle_frameData',methods=['POST'])
def handle_frameData():
    print('start')
    data = request.json
    image_data = data.get('image_data')
    # Create arrays of known face encodings and their names
    known_face_encodings = []
    known_face_names = []

    #retrive Data
    data=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/',"",'GET').text)["data"]
    for dtl in data:
        if(dtl["photo_path"]==''):
            continue
        img = face_recognition.load_image_file(dtl["photo_path"])
        face_encoding = face_recognition.face_encodings(img)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(str(dtl["employee_id"]))
    
    print('error')
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    # Receive frame data from client
    frame_data = image_data
    # Decode base64-encoded image data
    #image_data = base64.b64decode(frame_data.split(",")[1])
    _, encoded_data = frame_data.split(',', 1)
    decoded_data = base64.b64decode(encoded_data)
    
    # Convert decoded data to a NumPy array
    nparr = np.frombuffer(decoded_data, np.uint8)

    # Decode the NumPy array into an image
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

    # Only process every other frame of video to save time
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    name = "Unknown"
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        print(name)
        face_names.append(name)
    return name

async def handle_websocket(websocket, path):
    print('start')
    # Create arrays of known face encodings and their names
    known_face_encodings = []
    known_face_names = []
    
    #retrive Data
    strong_connection_string = 'DefaultEndpointsProtocol=https;AccountName=cs41003200254e816d4;AccountKey=+fIuDGjtc3RqRYNfVM9qFKgR9opVMzMtaDMQsYDMKkferKuFXS/17cPdIkokd/IZaQaAvFdGYec3+AStKPQ4pw==;EndpointSuffix=core.windows.net'

    dataset_connection = BlobServiceClient.from_connection_string(strong_connection_string)
    container_name = 'datasets'

    # Get the container client
    container_client = dataset_connection.get_container_client(container_name)

    # Define the local folder to save the downloaded images
    local_folder = './Datasets/'

    # Create the local folder if it doesn't exist
    os.makedirs(local_folder, exist_ok=True)

    # Iterate over blobs in the container
    for blob in container_client.list_blobs():
        # Construct blob client for the blob
        blob_client = dataset_connection.get_blob_client(container=container_name, blob=blob.name)
        
        # Define the local file path to save the downloaded blob
        local_file_path = os.path.join(local_folder, blob.name)
        
        # Check if the file already exists locally
        if os.path.exists(local_file_path):
            print(f"File '{blob.name}' already exists locally. Replacing...")
            os.remove(local_file_path)  # Remove the existing file
        
        # Download the blob to the local file system
        print(f"Downloading file: {blob.name}")
        with open(local_file_path, "wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())

    print("All files downloaded and replaced successfully.")


    data=json.loads(JSON.selectJSONCALL('https://us-east-2.aws.neurelo.com/rest/employees/',"",'GET').text)["data"]
    for dtl in data:
        if(dtl["photo_path"]==''):
            continue
        img = face_recognition.load_image_file(dtl["photo_path"])
        face_encoding = face_recognition.face_encodings(img)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(str(dtl["employee_id"]))
    

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    while True:
        # Receive frame data from client
        frame_data = await websocket.recv()
        # Decode base64-encoded image data
        #image_data = base64.b64decode(frame_data.split(",")[1])
        _, encoded_data = frame_data.split(',', 1)
        decoded_data = base64.b64decode(encoded_data)
        
        # Convert decoded data to a NumPy array
        nparr = np.frombuffer(decoded_data, np.uint8)

        # Decode the NumPy array into an image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        # Only process every other frame of video to save time
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            print(name)
            face_names.append(name)
            await websocket.send(name)
            name="Unknown"

def start_websocket_server():
    # Start WebSocket server
    asyncio.set_event_loop(asyncio.new_event_loop())
    start_server = websockets.serve(handle_websocket, "rollcallsystem.bluebush-887dce0f.eastus2.azurecontainerapps.io", 8767)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


@app.route('/api',methods=['POST','GET'])
def api():

    return ''

if __name__ == '__main__':
    app.run(debug=True)