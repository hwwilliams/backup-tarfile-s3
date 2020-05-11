import json
import os
import logging

from configure_upload.lookup import Lookup

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

    except json.JSONDecodeError:
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


def validate(backup_config):
    valid_source_types = ['tarfile', 'sqlite']

    backup_name = backup_config['Name']
    bucket_name = backup_config['BackupDestination']['BucketName']
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
        s3_lookup = Lookup(bucket_name)
        if not s3_lookup.bucket():
            invalid_configurations.append(json.dumps({
                "Issue": "BucketNameInvalid", "Name": bucket_name}))

    for source in backup_sources:
        if not os.path.exists(source['Path']):
            invalid_configurations.append(json.dumps({
                "Issue": "SourcePathNotFound", "Source": source}))

        for source_type in source['Type']:
            if source_type not in valid_source_types:
                invalid_configurations.append(json.dumps({
                    "Issue": "SourceTypeNotAllowed", "Source": source}))

    if len(invalid_configurations) > 0:
        for invalid_configuration in invalid_configurations:
            logger.error(
                f'Backup name: {backup_name}, Invalid backup configuration: {invalid_configuration}')

        raise InvalidBackupConfiguration

    elif len(invalid_configurations) == 0:
        logger.debug(
            f'Valid backup configuration: {json.dumps({"Name": backup_name})}')

        return backup_config


class BackupConfiguration:
    def __init__(self, backup_config):
        logger.debug('Attempting to import backup configuration.')

        (
            self.backups_config_dict,
            self.backups_config_json_path
        ) = get_backups_config(backup_config)

        logger.debug(
            'Successfully imported backup configuration.')

    def valid(self):
        logger.debug(
            'Attempting to validate backup configuration.')

        valid_backup_config = validate(self.backups_config_dict)

        logger.debug(
            'Successfully validated backup configuration.')

        return valid_backup_config
