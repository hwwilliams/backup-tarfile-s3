import botocore.exceptions
import boto3
import functools
import json
import logging
import os
import timeit

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

        return boto3.s3.transfer.TransferConfig(
            multipart_threshold=(MB_threshold * MB_binary),
            max_concurrency=10,
            multipart_chunksize=(MB_chunksize * MB_binary),
            use_threads=True
        )

    else:
        return boto3.s3.transfer.TransferConfig(
            max_concurrency=10,
            use_threads=True
        )


class Upload:
    def __init__(self, backup_config, upload_source, upload_size, s3_client):
        self.s3_client = s3_client
        self.source = upload_source
        self.size = upload_size

        self.config = get_transfer_config(self.size)

        self.backup_name = backup_config['Name']
        self.bucket_name = backup_config['Destination']['Bucket']
        self.bucket_file_prefix = backup_config['Destination']['FilePrefix']
        self.object_name = backup_config['TarOutputName']
        self.source_hash = backup_config['Checksum']

        self.object_path = os.path.join(
            self.bucket_file_prefix, self.object_name)

        if '\\' in self.object_path:
            self.object_path = self.object_path.replace('\\', '/')

        if backup_config['Destination']['UploadExtraArgs']:
            self.upload_extra_args = backup_config['Destination']['UploadExtraArgs']
            self.upload_extra_args['Metadata'] = {'SHA256': self.source_hash}

        else:
            self.upload_extra_args = {}
            self.upload_extra_args['Metadata'] = {'SHA256': self.source_hash}

    @upload_duration
    def transfer(self):
        try:
            self.s3_client.upload_file(self.source, self.bucket_name,
                                       self.object_path, ExtraArgs=self.upload_extra_args, Config=self.config)

        except botocore.exceptions.ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")

            logger.error(
                f'Failed to upload backup: {json.dumps({"ErrorCode": error_code})}')

            raise error
