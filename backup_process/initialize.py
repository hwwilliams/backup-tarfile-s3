import logging

from backup_process.client import S3Client
from backup_process.config import ConfigureBackup
from backup_process.backup import Backup
# from twilio_notifications.client import TwilioClient

logger = logging.getLogger(__name__)


def clients():
    s3 = S3Client()
    # twilio = TwilioClient()

    # return(s3.client, twilio.client)
    return(s3.client)


class Process():
    def __init__(self, config):
        (
            s3_client
        ) = clients()

        self.backup_config = ConfigureBackup(config).valid(s3_client)

        logger.debug('Initializing backup.')
        backup_duration = Backup(self.backup_config).make(s3_client)
        logger.debug(
            f'Completed backup. Backup process took {backup_duration}.')
