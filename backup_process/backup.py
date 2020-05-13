import functools
import json
import logging
import os
import tarfile
import timeit
import urllib.request

from backup_process.tempdir import TemporaryDirectory
from backup_process.upload import Upload
from hurry.filesize import size, verbose
from pretty_time_delta.calculate import PrettyTimeDelta
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)


def backup_duration(make_backup):
    @functools.wraps(make_backup)
    def wrapper_backup_duration(*args, **kwargs):

        begin = timeit.default_timer()
        make_backup(*args, **kwargs)
        end = timeit.default_timer()

        duration = PrettyTimeDelta(end - begin)

        return duration.format()

    return wrapper_backup_duration


def create_tarfile(name, output, sources):
    with tarfile.open(output, 'w:xz') as tar:
        for source in sources:
            source_path = source['Path']
            logger.debug(
                f'Attempting to add source to tar: {json.dumps({"Backup": name, "Sources": source_path})}')

            try:
                tar.add(source_path, arcname=os.path.basename(source_path))

            except IOError as error:
                if 'Permission denied' in error.strerror:
                    logger.error(
                        f'Failed to add source to tar. Permission Denied: {json.dumps({"Backup": name, "Source": source})}')

                else:
                    logger.error(
                        f'Failed to add source to tar: {json.dumps({"Backup": name, "Source": source})}')

                    raise error

            else:
                logger.debug(
                    f'Successfully added source to tar: {json.dumps({"Backup": name, "Source": source_path})}')


def handle_tarfile(name, sources, temp_dir):
    logger.debug(
        f'Building tar output: {json.dumps({"Backup": name, "OutputDirectory": temp_dir})}')

    name = str(name).lower().replace(' ', '-')
    tar_name = name + '.xz.tar'
    tar_output = os.path.join(temp_dir, tar_name)

    create_tarfile(name, tar_output, sources)

    tar_size = os.path.getsize(tar_output)
    tar_size_pretty = size(tar_size, system=verbose)

    logger.debug(
        f'Successfully created tar: {json.dumps({"Output": tar_output, "Size": tar_size_pretty})}')

    return(tar_output, tar_size, tar_size_pretty)


def handle_sources(name, sources, temp_dir):
    (
        tar_output,
        tar_size,
        tar_size_pretty
    ) = handle_tarfile(name, sources, temp_dir)

    return(tar_output, tar_size, tar_size_pretty)


def handle_health_check(backup_name, health_check_url):
    logger.debug(
        f'Attempting to send health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url})}')

    try:
        urllib.request.urlopen(health_check_url)

    except HTTPError as error:
        logger.error(
            f'Failed to send health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url, "ErrorCode": error.code})}')

        raise error

    except URLError as error:
        logger.error(
            f'Failed to send health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url, "ErrorCode": error.reason})}')

        raise error

    else:
        logger.debug(
            f'Successfully sent health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url})}')


class Backup:
    def __init__(self, backup_config):

        self.name = backup_config['Name']
        self.health_check_url = backup_config['HealthCheckUrl']
        self.backup_destination = backup_config['BackupDestination']
        self.sources = backup_config['BackupSources']

    @backup_duration
    def make(self, s3_client):
        with TemporaryDirectory() as temp_dir:

            (
                tar_output,
                tar_size,
                tar_size_pretty
            ) = handle_sources(self.name, self.sources, temp_dir)

            logger.info(
                f'Attempting to upload backup: {json.dumps({"Backup": self.name, "Size": tar_size_pretty})}')

            upload_duration = Upload(
                tar_output, tar_size, self.name, self.backup_destination, s3_client).transfer()

            handle_health_check(self.name, self.health_check_url)

            logger.info(
                f'Sucessfully uploaded backup: {json.dumps({"Backup": self.name, "Size": tar_size_pretty})}')
            logger.debug(
                f'Upload process took {upload_duration}.')
