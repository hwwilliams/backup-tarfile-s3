import boto3
import json
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Client():
    def __init__(self):
        logger.debug('Attempting to initialize S3 client.')

        self.exceptions = [
            'NoCredentialsError',
            'PartialCredentialsError',
            'CredentialRetrievalError'
        ]

        try:
            self.client = boto3.client('s3')

        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            if error_code in self.exceptions:
                logger.error(
                    f'Failed to initialize S3 client due to invalid or missing credentials: {json.dumps({"ErrorCode": error_code})}')

            logger.error(
                f'Failed to initialize S3 client: {json.dumps({"ErrorCode": error_code})}')

            raise error

        else:
            logger.debug('Successfully initialized S3 client.')
