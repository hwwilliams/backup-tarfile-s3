import botocore.exceptions
import boto3
import json
import os
import logging

logger = logging.getLogger(__name__)


class Lookup():
    def __init__(self, backup_config, s3_client):
        self.backup_config = backup_config
        self.s3_client = s3_client

        self.bucket_name = self.backup_config['Destination']['Bucket']

    def bucket(self):
        logger.debug(
            f'Attempting to validate bucket: {json.dumps({"Bucket": self.bucket_name})}')

        try:
            head_bucket = self.s3_client.head_bucket(
                Bucket=self.bucket_name
            )

        except botocore.exceptions.ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            logger.error(
                f'Failed to lookup bucket: {json.dumps({"ErrorCode": error_code})}')

            raise error

        else:
            if head_bucket and head_bucket['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.debug(
                    f'Successfully validated bucket: {json.dumps({"Bucket": self.bucket_name})}')

                return True

            else:
                logger.error(
                    f'Failed to validate bucket. NoSuchBucket: {json.dumps({"Bucket": self.bucket_name})}')

                return False

    def bucket_object(self):
        self.backup_name = self.backup_config['Name']
        self.file_prefix = self.backup_config['Destination']['FilePrefix']
        self.output_name = self.backup_config['TarOutputName']

        self.name = os.path.join(self.file_prefix, self.output_name)
        if '\\' in self.name:
            self.name = self.name.replace('\\', '/')

        self.hash = self.backup_config['Checksum']

        logger.debug(
            f'Attempting to lookup backup object at destination: {json.dumps({"Backup": self.backup_name, "ObjectName": self.name})}')

        try:
            head_object = self.s3_client.head_object(
                Bucket=self.bucket_name, Key=self.name)

        except botocore.exceptions.ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            if error_code == '404':
                logger.debug(
                    f'Backup object not found at destination: {json.dumps({"Backup": self.backup_name, "ObjectName": self.name})}')

                return None

            else:
                logger.warning(
                    f'Failed to lookup backup object: {json.dumps({"ErrorCode": error_code})}')

                raise error

        else:
            logger.debug(
                f'Successfully looked up backup object at destination: {json.dumps({"Backup": self.backup_name, "ObjectName": self.name})}')

            if head_object['Metadata']['sha256'] == self.hash:
                logger.debug(
                    f'Successfully found matching object hash at destination: {json.dumps({"Backup": self.backup_name, "ObjectName": self.name})}')

                return True

            else:
                logger.debug(
                    f'Failed to find matching object hash at destination: {json.dumps({"Backup": self.backup_name, "ObjectName": self.name})}')

                return False
