import botocore.exceptions
import boto3
import json
import logging

logger = logging.getLogger(__name__)


class S3Client():
    def __init__(self):
        logger.debug('Attempting to initialize S3 client.')

        credential_exceptions = [
            'NoCredentialsError',
            'PartialCredentialsError',
            'CredentialRetrievalError'
        ]

        try:
            self.client = boto3.client('s3')

        except botocore.exceptions.ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            if error_code in credential_exceptions:
                logger.error(
                    f'Failed to initialize S3 client due to invalid or missing credentials: {json.dumps({"ErrorCode": error_code})}')

                # twilio.process_messasge(
                #     f'Failed to initialize S3 client due to invalid or missing credentials: {json.dumps({"ErrorCode": error_code})}')

            logger.error(
                f'Failed to initialize S3 client: {json.dumps({"ErrorCode": error_code})}')

            # twilio.process_messasge(
            #     f'Failed to initialize S3 client: {json.dumps({"ErrorCode": error_code})}')

            raise error

        else:
            logger.debug('Successfully initialized S3 client.')
