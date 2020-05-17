import functools
import json
import logging
import os
import timeit

from backup_process.archive import Archive
from backup_process.tempdir import TemporaryDirectory
from backup_process.upload import Upload
from pretty_time_delta.calculate import PrettyTimeDelta

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


class Backup:
    def __init__(self, backup_config, s3_client):
        self.s3_client = s3_client
        self.config = backup_config

        self.name = self.config['Name']
        self.output_name = self.config['TarOutputName']
        self.sources = self.config['Sources']

    @backup_duration
    def make(self):
        with TemporaryDirectory() as temp_dir:
            try:
                self.output_path = os.path.join(temp_dir, self.output_name)

                archive = Archive(self.config)
                archive.make(self.output_path)

                logger.info(
                    f'Attempting to upload backup: {json.dumps({"Backup": self.name, "Size": archive.size_pretty})}')

                upload = Upload(self.config, self.output_path,
                                archive.size, self.s3_client)
                upload_duration = upload.transfer()

            except Exception as error:
                logger.error(
                    f'Failed backup: {json.dumps({"Backup": self.name})}')

                raise error

            else:
                logger.info(
                    f'Sucessfully uploaded backup: {json.dumps({"Backup": self.name, "Size": archive.size_pretty})}')

                logger.debug(
                    f'Upload process took {upload_duration}.')
