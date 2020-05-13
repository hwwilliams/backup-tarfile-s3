import json
import logging
import os
import re

from backup_process.lookup import Lookup
from json import JSONDecodeError

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


def get_backups_config(backup_config):
    backups_config_json_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'settings', 'backup_configs', backup_config))

    logger.debug(
        f'Attempting to load backup configuration: {json.dumps({"File": backups_config_json_path})}')

    try:
        with open(backups_config_json_path, 'r') as file:
            backups_config_dict = json.load(file)

    except JSONDecodeError:
        logger.error(
            f'No valid JSON data found when attempting to load backup configuration: {json.dumps({"File": backups_config_json_path})}')
        raise

    except FileNotFoundError:
        logger.error(
            f'Backup configuration not found: {json.dumps({"File": backups_config_json_path})}')
        raise

    if 'BackupConfig' in backups_config_dict:
        logger.debug(
            f'Successfully loaded backup configuration: {json.dumps({"File": backups_config_json_path})}')
        return (backups_config_dict['BackupConfig'], backups_config_json_path)

    else:
        logger.error(
            f'Backup configuration json array not found: {json.dumps({"File": backups_config_json_path})}')
        raise InvalidJsonBackupsConfigurationArray


def validate(backup_config, s3_client):
    backup_name = backup_config['Name']
    bucket_name = backup_config['BackupDestination']['BucketName']
    bucket_file_prefix = backup_config['BackupDestination']['BucketFilePrefix']
    backup_sources = backup_config['BackupSources']
    backup_health_check_url = backup_config['HealthCheckUrl']

    invalid_configurations = []

    if not backup_name:
        invalid_configurations.append(json.dumps({
            "Issue": "NameEmpty", "Name": None}))

    if not backup_health_check_url:
        invalid_configurations.append(json.dumps({
            "Issue": "HealthCheckUrlEmpty", "HealthCheckUrl": None}))

    if not bucket_name:
        invalid_configurations.append(json.dumps({
            "Issue": "BucketNameEmpty", "Name": None}))

    elif bucket_name:
        s3_lookup = Lookup(bucket_name, s3_client)
        if not s3_lookup.bucket():
            invalid_configurations.append(json.dumps({
                "Issue": "BucketNameInvalid", "Name": bucket_name}))

    if bucket_file_prefix:
        prefix_end_slash = r"^[a-zA-Z0-9].*[a-zA-Z0-9]\/$"
        prefix_no_end_slash = r"^[a-zA-Z0-9].*[a-zA-Z0-9]$"

        if not bool(re.compile(prefix_end_slash).match(bucket_file_prefix)):
            if not bool(re.compile(prefix_no_end_slash).match(bucket_file_prefix)):
                invalid_configurations.append(json.dumps({
                    "Issue": "BucketFilePrefixInvalid", "Prefix": bucket_file_prefix}))

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


class ConfigureBackup:
    def __init__(self, backup_config):
        logger.debug('Attempting to validate backup configuration json data.')

        (
            self.backups_config_dict,
            self.backups_config_json_path
        ) = get_backups_config(backup_config)

        logger.debug(
            'Successfully validated backup configuration json data.')

    def valid(self, s3_client):
        logger.debug(
            'Attempting to validate backup configuration settings.')

        valid_backup_config = validate(
            self.backups_config_dict, s3_client)

        logger.debug(
            'Successfully validated backup configuration settings.')

        return valid_backup_config
