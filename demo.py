import os
from azure.storage.blob import BlobServiceClient
import shutil

strong_connection_string = 'DefaultEndpointsProtocol=https;AccountName=cs41003200254e816d4;AccountKey=+fIuDGjtc3RqRYNfVM9qFKgR9opVMzMtaDMQsYDMKkferKuFXS/17cPdIkokd/IZaQaAvFdGYec3+AStKPQ4pw==;EndpointSuffix=core.windows.net'

dataset_connection = BlobServiceClient.from_connection_string(strong_connection_string)

# container_name='images'
# container_client = dataset_connection.create_container(container_name)

# print(dataset_connection)

# # file_folder='./Datasets/'
# # for file_name in os.listdir(file_folder):
# #     blob_obj=dataset_connection.get_blob_client(container='datasets',blob=file_name)
# #     print(blob_obj)
# #     if blob_obj.exists():
# #         # If blob exists, delete it
# #         print(f"Deleting existing blob: {file_name}")
# #         blob_obj.delete_blob()

# #     with open(os.path.join(file_folder,file_name),mode='rb') as file_data:
# #         blob_obj.upload_blob(file_data)

# container_name = 'datasets'
# blob_name = '123.jpg'

# # Get the blob client for the specified blob
# blob_client = dataset_connection.get_blob_client(container=container_name, blob=blob_name)

# # Download the blob's content

# if not os.path.exists('encoding'):
#     os.makedirs('encoding')
# with open('encoding/'+blob_name, "wb") as my_blob:
#     download_stream = blob_client.download_blob()
#     my_blob.write(download_stream.readall())

# if os.path.exists('encoding'):
#     shutil.rmtree('encoding')

# Define the container name
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