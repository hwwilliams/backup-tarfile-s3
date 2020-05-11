import boto3

from configure_upload.client import S3


class Lookup():
    def __init__(self, bucket):
        self.client = S3().client

        self.search_bucket_name = str(bucket)

    def bucket(self):
        self.bucket_names = [bucket['Name']
                             for bucket in self.client.list_buckets()['Buckets']]

        if self.search_bucket_name in self.bucket_names:
            return True
        else:
            return False
