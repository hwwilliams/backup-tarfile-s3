import json
import hurry.filesize
import logging
import os
import re
import tarfile

from hurry.filesize import size, verbose

logger = logging.getLogger(__name__)


def build_tarfile(backup_name, backup_output, backup_compression, backup_sources):
    with tarfile.open(backup_output, f'w:{backup_compression}') as tar:

        for source in backup_sources:
            source_path = source['Path']
            exclusions = '(?:% s)' % '|'. join(source['Exclude'])

            logger.debug(
                f'Attempting to add source to archive: {json.dumps({"Backup": backup_name, "Sources": source_path})}')

            try:
                tar.add(source_path, arcname=os.path.basename(
                    source_path), filter=lambda tarinfo: None if re.search(exclusions, tarinfo.name) else tarinfo)

            except IOError as error:
                if 'Permission denied' in error.strerror:
                    logger.error(
                        f'Failed to add source to archive. Permission Denied: {json.dumps({"Backup": backup_name, "Source": source})}')

                else:
                    logger.error(
                        f'Failed to add source to archive: {json.dumps({"Backup": backup_name, "Source": source})}')

                    raise error

            else:
                logger.debug(
                    f'Successfully added source to archive: {json.dumps({"Backup": backup_name, "Source": source_path})}')

                return True


class Archive():
    def __init__(self, backup_config):
        self.backup_name = backup_config['Name']
        self.compression = backup_config['TarCompression']
        self.sources = backup_config['Sources']

    def make(self, backup_output):
        logger.debug(
            f'Attempting to create archive: {json.dumps({"Backup": self.backup_name, "OutputDirectory": backup_output})}')

        build_result = build_tarfile(self.backup_name, backup_output,
                                     self.compression, self.sources)

        if build_result:
            self.size = os.path.getsize(backup_output)
            self.size_pretty = hurry.filesize.size(
                self.size, system=hurry.filesize.verbose)

            logger.debug(
                f'Successfully created archive: {json.dumps({"Output": backup_output, "Size": self.size_pretty})}')

        else:
            logger.error(
                f'Failed to create archive: {json.dumps({"Backup": self.backup_name, "OutputDirectory": backup_output})}')
