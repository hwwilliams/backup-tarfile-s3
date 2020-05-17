import json
import logging
import requests

logger = logging.getLogger(__name__)


class HealthCheck():
    def __init__(self, backup_config):
        self.backup_name = backup_config['Name']
        self.url = backup_config['HealthCheckUrl']

    def push(self, initialize=None, failure=None):
        logger.debug(
            f'Attempting to send health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url})}')

        retry_adapter = requests.adapters.HTTPAdapter(max_retries=3)

        session = requests.Session()
        session.mount('https://', retry_adapter)
        session.mount('http://', retry_adapter)

        try:
            if initialize:
                session.get(self.url + '/start')

            elif failure:
                session.get(self.url + '/fail')

            else:
                session.get(self.url)

        except requests.exceptions.ConnectionError as error:
            logger.error(
                f'Failed to send health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url})}')

            raise error

        else:
            logger.debug(
                f'Successfully sent health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url})}')
