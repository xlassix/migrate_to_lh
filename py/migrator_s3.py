import boto3
import io
import botocore
from lighthouseweb3 import Lighthouse
import os

# Load environment variables

def parse_env():
    """parse .env file"""
    try:
        with open(".env", "r") as f:
            for line in f.readlines():
                if line.startswith("#"):
                    continue
                key, value = line.split("=")
                os.environ[key] = value.strip()
    except FileNotFoundError:
        print("No .env file found")
        print("Defaulting to preset environment variables...")

parse_env()


# Decorator to check if connection is established
def check_connection(func):
    def wrapper(self, *args, **kwargs):
        # Raise exception if not connected
        if not self.connected:
            raise Exception(
                "S3 not initialized, kindly call the method `connect_db` and try again")
        return func(self, *args, **kwargs)
    return wrapper


class Migrator:
    _connected = False  # "Private" attribute to track connection status

    def __init__(self, token: str = ""):
        # Retrieve the token from environment variable if not provided
        _token = token or os.environ.get("LIGHTHOUSE_TOKEN", "")
        if not _token:
            raise Exception(
                "No token provided: Please provide a token or set the LIGHTHOUSE_TOKEN environment variable"
            )

        self.storage_provider = Lighthouse(_token)
        # Initialize S3 resource and bucket
        self._s3 = boto3.resource('s3')
        self.bucket_name = ""
        self._bucket=self._s3.Bucket(bucket_name)

    @property
    def connected(self):
        # Getter for connected attribute
        return self._connected

    @connected.setter
    def connected(self, value):
        # Prevent modification of connected attribute
        raise AttributeError("You cannot modify this attribute.")

    @classmethod
    def connect_db(self,  bucket_name: str, key_id: str, secret: str):
        # Initialize S3 with provided credentials and bucket
        if bucket_name == '' or key_id == '' or secret == '':
            raise Exception(
                "No token provided: Please provide a token or set the LIGHTHOUSE_TOKEN environment variable"
            )
        if bucket_name != '' and key_id != '' and secret != '':
            self._s3 = boto3.resource('s3',
                                      aws_access_key_id=key_id,
                                      aws_secret_access_key=secret,
                                      )
            self._bucket = self._s3.Bucket(bucket_name)
            self.bucket_name = bucket_name
            try:
                # Check if bucket exists
                self._s3.meta.client.head_bucket(Bucket=bucket_name)
                self._connected = True

            except botocore.exceptions.ClientError as e:
                # If a client error is thrown, then check that it was a 404 error.
                # If it was a 404 error, then the bucket does not exist.
                error_code = int(e.response['Error']['Code'])
                if error_code == 404:
                    raise Exception("Bucket does not exist.")
                else:
                    print(e.response['Error'])
                    raise Exception("You do not have access to the bucket.")

    @check_connection
    def copy_all_files_from_s3_to_lighthouse(self, startAt: str = ""):
        # Copy all files from S3 to Lighthouse starting at a given marker

        # Initialize an empty list to store the migrated objects
        migrated = []

        # Iterate through all objects in the bucket starting at the marker
        for _object in self._bucket.objects.filter(Marker=startAt):

            # Get the object's metadata and data from the S3 bucket
            obj = self._s3.Object(self._bucket.name, _object.key).get()

            # Print a message to indicate the object is being uploaded
            print("uploading: ", _object.key)

            # Upload the object to the storage provider and append the result to the migrated list
            migrated.append(self.storage_provider.uploadBlob(
                obj["Body"], _object.key, _object.key))

            # Print a message to indicate the object has been uploaded
            print("uploaded : ", _object.key)

        # Return the list of migrated objects
        return migrated


if __name__ == "__main__":
    bucket_name = 'poda'

    migrator = Migrator()
    migrator.connect_db(
        bucket_name, os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])

    # # push all data
    files = migrator.copy_all_files_from_s3_to_lighthouse()

    # push with offset
    # files = migrator.copy_all_files_from_s3_to_lighthouse(
    #     "sample_text_file.txt")

    # Example usage: Read the content of the first buffer
    if files:
        print(files)
