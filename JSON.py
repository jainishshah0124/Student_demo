import requests
import os


# Define the URL and headers
url = 'https://us-east-2.aws.neurelo.com/rest/employees/__one?select={"$scalars":true,"$related":true}'
headers = {
    'Content-Type': 'application/json',
    'X-API-KEY': os.getenv("NEURELO_API_KEY")
}


def sendJSONCALL(url,data,method):
    if method=='POST':
        response = requests.post(url, json=data, headers=headers)
        return response

def updateJSONCALL(url,data,method):
    if method=='PATCH':
        response = requests.patch(url, json=data, headers=headers)
        return response

def selectJSONCALL(url,data,method):
    if method=='GET':
        response = requests.get(url, json=data, headers=headers)
        return response
    
def deleteJSONCALL(url,data,method):
    if method=='DELETE':
        response = requests.delete(url, json=data, headers=headers)
        return response
