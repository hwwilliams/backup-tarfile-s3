import json
import logging

from backup_initialize.checksum import CalculateChecksum
from backup_initialize.client import S3Client
from backup_initialize.config import CleanBackupConfig
from backup_initialize.lookup import Lookup
from backup_initialize.validate import ValidateBackupConfig
from backup_process.backup import Backup
from backup_finalize.healthcheck import HealthCheck
# from twilio_notifications.messenger import TwilioNotification

logger = logging.getLogger(__name__)


def clients():
    # twilio = TwilioNotification()
    s3 = S3Client()

    return(s3.client)


class InitializeProcess():
    def __init__(self, backup_config_path):
        (
            s3_client
        ) = clients()

        logger.info('Initializing backup.')

        validate_backup = ValidateBackupConfig(s3_client)
        backup_config = validate_backup.check(backup_config_path)

        backup_config['Checksum'] = (
            CalculateChecksum(backup_config)).hash

        backup_config = (CleanBackupConfig(backup_config)).config

        s3_lookup = Lookup(backup_config, s3_client)
        lookup_bucket_object = s3_lookup.bucket_object()

        health_check = HealthCheck(backup_config)

        if lookup_bucket_object:
            health_check.push()

            backup_name = backup_config['Name']
            logger.info(
                f'Backup content identical to destination. Backup process canceled: {json.dumps({"Backup": backup_name})}')

        elif not lookup_bucket_object or lookup_bucket_object == None:
            try:
                health_check.push(initialize=True)

                backup_duration = Backup(backup_config, s3_client).make()

            except Exception as error:
                health_check.push(failure=True)

                raise error

            else:
                health_check.push()

                logger.info(
                    f'Completed backup. Backup process took {backup_duration}.')
