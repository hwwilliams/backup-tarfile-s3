import boto3
import functools
import json
import logging
import os
import timeit

from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from pretty_time_delta.calculate import PrettyTimeDelta

logger = logging.getLogger(__name__)


def upload_duration(upload_backup):
    @functools.wraps(upload_backup)
    def wrapper_upload_duration(*args, **kwargs):

        begin = timeit.default_timer()
        upload_backup(*args, **kwargs)
        end = timeit.default_timer()

        duration = PrettyTimeDelta(end - begin)

        return duration.format()

    return wrapper_upload_duration


def bucket_object_name(file_prefix, source):
    file_prefix = str(file_prefix)

    if file_prefix:
        if file_prefix.endswith('/'):
            object_name = file_prefix + os.path.basename(source)

        else:
            object_name = f'{file_prefix}/{os.path.basename(source)}'

    else:
        object_name = os.path.basename(source)

    logger.debug(
        f'Upload Process: {json.dumps({"BucketObjectName": object_name})}')

    return object_name


def calc_chunksize(backup_size, MB_binary, MB_threshold):
    if backup_size <= 2.5 * (MB_binary * MB_threshold):
        MB_chunksize = 16

    elif backup_size <= 4.5 * (MB_binary * MB_threshold):
        MB_chunksize = 32

    elif backup_size <= 10 * (MB_binary * MB_threshold):
        MB_chunksize = 64

    elif backup_size > 10 * (MB_binary * MB_threshold):
        MB_chunksize = 256

    logger.debug(
        f'Upload Process: {json.dumps({"UploadChunksize": MB_chunksize})}')

    return MB_chunksize


def get_transfer_config(backup_size):
    MB_binary = 1048576
    MB_threshold = 100

    if backup_size >= (MB_threshold * MB_binary):
        MB_chunksize = calc_chunksize(backup_size, MB_binary, MB_threshold)

        return TransferConfig(
            multipart_threshold=(MB_threshold * MB_binary),
            max_concurrency=10,
            multipart_chunksize=(MB_chunksize * MB_binary),
            use_threads=True
        )

    else:
        return TransferConfig(
            max_concurrency=10,
            use_threads=True
        )


class Upload:
    def __init__(self, backup_source, backup_size, backup_name, backup_destination, s3_client):
        self.s3_client = s3_client

        self.backup_name = backup_name
        self.backup_source = backup_source
        self.backup_size = backup_size
        self.bucket_name = backup_destination['BucketName']
        self.bucket_file_prefix = backup_destination['BucketFilePrefix']
        self.upload_extra_args = backup_destination['BucketUploadExtraArgs']

        self.bucket_object_name = bucket_object_name(
            self.bucket_file_prefix, self.backup_source)

        self.config = get_transfer_config(self.backup_size)

    @upload_duration
    def transfer(self):
        try:
            self.s3_client.upload_file(self.backup_source, self.bucket_name,
                                       self.bucket_object_name, ExtraArgs=self.upload_extra_args, Config=self.config)

        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            logger.error(
                f'Failed to upload backup: {json.dumps({"ErrorCode": error_code})}')

            raise error
