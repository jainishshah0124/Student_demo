import requests


# Define the URL and headers
url = 'https://us-east-2.aws.neurelo.com/rest/employees/__one?select={"$scalars":true,"$related":true}'
headers = {
    'Content-Type': 'application/json',
    'X-API-KEY': 'neurelo_9wKFBp874Z5xFw6ZCfvhXdrIxbYidUfYmprDJks1tK7y+CdPciG0qgAl1exw69RQYdQYxvqcRG1GgVajqZknUzwW3VIC3xEqNyynTa2l6w7oNlrUhKRqRwBMMl8+7AZa47Yep4FXq3GDsvF4EEl8V0KoyaErzYwNp/1UgzVKPIIJ0g4CU0FZ7DttiyrVmTey_QQJSGjZU26OLFcPkkURgzkUzltgQryhI0R5NRDB76x4='
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
