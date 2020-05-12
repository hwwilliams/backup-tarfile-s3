import boto3
import json
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Lookup():
    def __init__(self, bucket, s3_client):
        self.s3_client = s3_client

        self.search_bucket_name = str(bucket)

    def bucket(self):
        logger.debug(
            f'Attempting to validate bucket existence: {json.dumps({"Bucket": self.search_bucket_name})}')

        try:
            self.bucket_names = [bucket['Name']
                                 for bucket in self.s3_client.list_buckets()['Buckets']]

        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            logger.error(
                f'Failed to lookup bucket: {json.dumps({"ErrorCode": error_code})}')

            raise error

        else:
            if self.search_bucket_name in self.bucket_names:
                logger.debug(
                    f'Successfully validated bucket existence: {json.dumps({"Bucket": self.search_bucket_name})}')

                return True

            else:
                logger.error(
                    f'Failed to validate bucket existence. NoSuchBucket: {json.dumps({"Bucket": self.search_bucket_name})}')

                return False
