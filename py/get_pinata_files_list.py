import requests
import os
import pandas as pd

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


def get_nft_count(bearer_token):
    print("stark1")
    offset = 0
    total_nfts = offset
    has_more = True
    count = 1
    limit = 1000
    result=pd.DataFrame()

    while has_more:
        try:
            response = requests.get(
                f"https://api.pinata.cloud/data/pinList?status=pinned&pageLimit={limit}&pageOffset={offset}",
                headers={
                    "Authorization": f"Bearer {bearer_token}"
                }
            )
            data = response.json()
            total_nfts += len(data["rows"])
            offset += 1000
            print(data)
            
            df = pd.json_normalize(data['rows'])

            # If you want to extract the nested 'regions' field as separate columns
            regions = pd.json_normalize(data['rows'], record_path='regions', meta='id')
            df = df.merge(regions, on='id', how='left')

            result = pd.concat([result, df]).reset_index(drop=True)
            result.to_csv("pinata_data.csv")
            has_more = offset < data["count"]
            print("loops:", count, "\t nfs so far", total_nfts)
            count += 1
        except Exception as e:
            print("Error fetching data from Pinata:", e)
            result.to_csv("e_pinata_data.csv")
            break

    return total_nfts

if __name__ == "__main__":
    bearer_token = os.getenv("PINATA_JWT")
    
    try:
        nft_count = get_nft_count(bearer_token)
        print(f"There are {nft_count} NFTs stored on Pinata.")
    except Exception as err:
        print(err)
