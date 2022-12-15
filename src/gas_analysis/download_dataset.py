import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv

load_dotenv()
dirname = os.path.dirname(__file__)
local_path_noleak = os.path.join(dirname, "../../videos/results")
if not os.path.exists(local_path_noleak):
    os.makedirs(local_path_noleak)

files_leak = ["MOV_1650.mp4", "MOV_1669.mp4", "MOV_1544.mp4", "MOV_1616.mp4", "MOV_1546.mp4"]
local_path_leak = os.path.join(dirname, "../../videos/leak")
if not os.path.exists(local_path_leak):
    os.makedirs(local_path_leak)

files_noleak = ["MOV_1662.mp4", "MOV_1541.mp4", "MOV_1543.mp4"]
local_path_noleak = os.path.join(dirname, "../../videos/noleak")
if not os.path.exists(local_path_noleak):
    os.makedirs(local_path_noleak)

connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_client_leak = ContainerClient.from_connection_string(
    connect_str, "mongstad-nov-2022-leak"
)
container_client_noleak = ContainerClient.from_connection_string(
    connect_str, "mongstad-nov-2022-noleak"
)

for f in files_leak:
    download_file_path = os.path.join(local_path_leak, f)
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client_leak.download_blob(f).readall())

for f in files_noleak:
    download_file_path = os.path.join(local_path_noleak, f)
    print("\nDownloading blob to \n\t" + download_file_path)
    with open(file=download_file_path, mode="wb") as download_file:
        download_file.write(container_client_noleak.download_blob(f).readall())
