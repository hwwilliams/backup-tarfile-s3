import json
import logging
import os
import re

from backup_initialize.lookup import Lookup

logger = logging.getLogger(__name__)


class InvalidJsonBackupsConfigurationArray(Exception):
    # Custom exception raised when the backups configuration json array was not found
    def __init__(self):
        Exception.__init__(
            self, 'Failed to find valid backup configuration json array.')


class InvalidBackupConfiguration(Exception):
    # Custom exception raised when all backup configurations are invalid
    def __init__(self):
        Exception.__init__(
            self, 'Backup configuration is invalid or contains invalid settings.')


def get_backup_config(backup_config_path):
    backups_config_full_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'settings', 'backup_configs', backup_config_path))

    logger.debug(
        f'Attempting to load backup configuration: {json.dumps({"File": backups_config_full_path})}')

    try:
        with open(backups_config_full_path, 'r') as file:
            backups_config_dict = json.load(file)

    except json.JSONDecodeError as error:
        logger.error(
            f'No valid JSON data found when attempting to load backup configuration: {json.dumps({"File": backups_config_full_path})}')

        raise error

    except FileNotFoundError:
        logger.error(
            f'Backup configuration not found: {json.dumps({"File": backups_config_full_path})}')

        raise

    if 'BackupConfig' in backups_config_dict:
        logger.debug(
            f'Successfully loaded backup configuration: {json.dumps({"File": backups_config_full_path})}')

        return backups_config_dict['BackupConfig']

    else:
        logger.error(
            f'Backup configuration json array not found: {json.dumps({"File": backups_config_full_path})}')

        raise InvalidJsonBackupsConfigurationArray


def validate(backup_config, s3_client):
    backup_name = backup_config['Name']
    backup_health_check_url = backup_config['HealthCheckUrl']
    backup_compression = backup_config['TarCompression']
    backup_bucket_name = backup_config['Destination']['Bucket']
    backup_file_prefix = backup_config['Destination']['FilePrefix']
    backup_sources = backup_config['Sources']

    valid_tar_compression = ['gz', 'bz2', 'xz']

    invalid_configurations = []

    if not backup_name:
        invalid_configurations.append(json.dumps({
            "Issue": "NameEmpty", "Name": None}))

    if backup_compression not in valid_tar_compression:
        invalid_configurations.append(json.dumps({
            "Issue": "TarCompressionInvalid", "TarCompression": backup_compression, "ValidCompression": valid_tar_compression}))

    if not backup_health_check_url:
        invalid_configurations.append(json.dumps({
            "Issue": "HealthCheckUrlEmpty", "HealthCheckUrl": None}))

    if not backup_bucket_name:
        invalid_configurations.append(json.dumps({
            "Issue": "BucketNameEmpty", "Name": None}))

    elif backup_bucket_name:
        s3_lookup = Lookup(backup_config, s3_client)
        if not s3_lookup.bucket():
            invalid_configurations.append(json.dumps({
                "Issue": "BucketNameInvalid", "Name": backup_bucket_name}))

    if backup_file_prefix:
        prefix_end_slash = r"^[a-zA-Z0-9].*[a-zA-Z0-9]\/$"
        prefix_no_end_slash = r"^[a-zA-Z0-9].*[a-zA-Z0-9]$"

        if not bool(re.compile(prefix_end_slash).match(backup_file_prefix)):
            if not bool(re.compile(prefix_no_end_slash).match(backup_file_prefix)):
                invalid_configurations.append(json.dumps({
                    "Issue": "BucketFilePrefixInvalid", "Prefix": backup_file_prefix}))

    for source in backup_sources:
        if not os.path.exists(source['Path']):
            invalid_configurations.append(json.dumps({
                "Issue": "SourcePathNotFound", "Source": source}))

    if len(invalid_configurations) > 0:
        for invalid_configuration in invalid_configurations:
            logger.error(
                f'Backup name: {backup_name}, Invalid backup configuration: {invalid_configuration}')

        raise InvalidBackupConfiguration

    elif len(invalid_configurations) == 0:
        logger.debug(
            f'Validated backup configuration: {json.dumps({"Backup": backup_name})}')

        return backup_config


class ValidateBackupConfig:
    def __init__(self, s3_client):
        self.client = s3_client

    def check(self, backup_config_path):
        logger.debug('Attempting to validate backup configuration json data.')

        self.backups_config = get_backup_config(backup_config_path)

        logger.debug(
            'Successfully validated backup configuration json data.')

        logger.debug(
            'Attempting to validate backup configuration settings.')

        valid_backup_config = validate(
            self.backups_config, self.client)

        logger.debug(
            'Successfully validated backup configuration settings.')

        return valid_backup_config
