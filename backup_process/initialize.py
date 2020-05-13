import logging

from backup_process.client import S3Client
from backup_process.config import ConfigureBackup
from backup_process.backup import Backup
from twilio_notifications.messenger import TwilioNotification

logger = logging.getLogger(__name__)


def clients():
    twilio = TwilioNotification()
    s3 = S3Client(twilio)

    return(s3.client)


class Process():
    def __init__(self, config):
        (
            s3_client
        ) = clients()

        self.backup_config = ConfigureBackup(config).valid(s3_client)

        logger.info('Initializing backup.')
        backup_duration = Backup(self.backup_config).make(s3_client)
        logger.info(
            f'Completed backup. Backup process took {backup_duration}.')
