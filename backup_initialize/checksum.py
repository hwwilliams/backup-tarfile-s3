import hashlib
import json
import os
import logging
import re

logger = logging.getLogger(__name__)


def get_hash(backup_name, backup_sources):
    sha256_hash = hashlib.sha256()

    for source in backup_sources:
        source_path = source['Path']
        exclusions = '(?:% s)' % '|'. join(source['Exclude'])

        try:
            for root, dirs, files in os.walk(source_path):

                for name in files:
                    filepath = os.path.join(root, name)

                    if not re.search(exclusions, filepath):
                        logger.debug(
                            f'Calculating checksum: {json.dumps({"File": filepath})}')

                        file_object = open(filepath, 'rb')

                        sha256_hash.update(file_object.read(8192))

                        file_object.close()

        except IOError as error:
            if file_object:
                file_object.close()

            if 'Permission denied' in error.strerror:
                logger.error(
                    f'Failed to calculate checksum. Permission Denied: {json.dumps({"Backup": backup_name, "Source": source})}')

            raise error

    return sha256_hash.hexdigest()


class CalculateChecksum():
    def __init__(self, backup_config):
        self.name = backup_config['Name']
        self.sources = backup_config['Sources']

        logger.debug(
            f'Attempting to calculate checksum of backup: {json.dumps({"Backup": self.name})}')

        self.hash = get_hash(self.name, self.sources)

        logger.debug(
            f'Successfully calculated checksum of backup: {json.dumps({"Backup": self.name, "Checksum": self.hash})}')
