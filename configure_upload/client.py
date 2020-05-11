import boto3


class S3():
    def __init__(self):
        self.client = boto3.client('s3')
