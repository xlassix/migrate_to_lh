import requests
import os
import io
import json
import concurrent.futures
import pandas as pd

# from lighthouseweb3 import Lighthouse
# storage_provider = Lighthouse(os.getenv('LIGHTHOUSE_TOKEN'))

folder_path = './backup/'


# Check if the folder structure exists
if not os.path.exists(folder_path):
    try:
        # Create the folder structure
        os.makedirs(folder_path)
        print("Folder structure created successfully.")
    except OSError as e:
        print(f"Error creating folder structure: {str(e)}")
else:
    print("Folder structure already exists.")

def is_valid_json(b_string):
    try:
        json.loads(b_string.decode())
        return True
    except (ValueError, TypeError):
        return False

# Load environment variables
limit= 1000
offset = 0

def parse_env(env_file=".env"):
    """parse .env file"""
    try:
        with open(env_file, "r") as f:
            for line in f.readlines():
                if line.startswith("#"):
                    continue
                key, value = line.split("=")
                os.environ[key] = value.strip()
    except FileNotFoundError:
        print("No .env file found")
        print("Defaulting to preset environment variables...")

parse_env()


def download_from_ipfs(ipfs_hash,filename):
    gateway_urls = [
        "https://gateway.pinata.cloud/ipfs/",
        'https://ipfs.io/ipfs/',
    ]

    if os.path.isfile("./backup/"+ipfs_hash+".json"):
        return
    for url in gateway_urls:
        try:
            response = requests.get(url + ipfs_hash)
            if response.status_code == 200:
                if (is_valid_json(response.content)):
                    data=json.loads(response.content.decode())
                    image_hash=data["image"].split("//")[-1]
                    if os.path.isfile("./backup/"+image_hash+".png"):
                        pass
                    else:
                        download_from_ipfs(image_hash,image_hash+".png")
                    filename=ipfs_hash+".json"
                    if os.path.isfile("./backup/"+filename):
                        print("Json exists")
                        continue
                with open("./backup/"+filename, 'wb') as file:
                    file.write(response.content)
                # storage_provider.uploadBlob(io.BytesIO(response.content), filename, filename)
                return response.content,filename
        except requests.exceptions.RequestException:
            continue

    return None

def get_nft_count(offset,bearer_token):
    print('stark1')
    total_nfts = 0
    end_at=1850000
    has_more = True
    count=0
    result=pd.DataFrame()

    while has_more:
        try:
            response = requests.get(f'https://api.pinata.cloud/data/pinList?status=pinned&pageLimit={limit}&pageOffset={offset}', headers={
                'Authorization': f'Bearer {bearer_token}'
            })
            response_data = response.json()
            total_nfts += len(response_data['rows'])
            # Using 100 threads (adjust as necessary)
            cids= [i["ipfs_pin_hash"] for i in response_data['rows']]
            filenames= [i["metadata"]["name"] for i in response_data['rows']]
            with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
                executor.map(download_from_ipfs, cids, filenames)

            df = pd.json_normalize(response_data['rows'])

            # If you want to extract the nested 'regions' field as separate columns
            regions = pd.json_normalize(response_data['rows'], record_path='regions', meta='id')
            df = df.merge(regions, on='id', how='left')

            result = pd.concat([result, df]).reset_index(drop=True)
            result.to_csv("pinata_data.csv")
            offset += limit
            has_more = offset < response_data['count']
            print(f"Pointer At {offset+count}")
        except Exception as error:
            print(f"stopped At {offset+count}")
            print('Error fetching data from Pinata:', error)
            break

    return total_nfts

bearer_token = os.getenv('PINATA_JWT')

nft_count = get_nft_count(offset,bearer_token)
print(f'There are {nft_count} NFTs stored on Pinata.')
