import json
import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)


def handle_health_check(backup_name, health_check_url, start_health_check=None, fail_health_check=None):
    logger.debug(
        f'Attempting to send health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url})}')

    try:
        if start_health_check:
            urllib.request.urlopen(health_check_url + '/start')

        elif fail_health_check:
            urllib.request.urlopen(health_check_url + '/fail')

        else:
            urllib.request.urlopen(health_check_url)

    except urllib.error.HTTPError as error:
        logger.error(
            f'Failed to send health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url, "ErrorCode": error.code})}')

        raise error

    except urllib.error.URLError as error:
        logger.error(
            f'Failed to send health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url, "ErrorCode": error.reason})}')

        raise error

    else:
        logger.debug(
            f'Successfully sent health check: {json.dumps({"BackupName": backup_name, "HealthCheckUrl": health_check_url})}')


class HealthCheck():
    def __init__(self, backup_config):
        self.backup_name = backup_config['Name']
        self.url = backup_config['HealthCheckUrl']

    def push(self, initialize=None, failure=None):
        logger.debug(
            f'Attempting to send health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url})}')

        try:
            if initialize:
                urllib.request.urlopen(self.url + '/start')

            elif failure:
                urllib.request.urlopen(self.url + '/fail')

            else:
                urllib.request.urlopen(self.url)

        except urllib.error.HTTPError as error:
            logger.error(
                f'Failed to send health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url, "ErrorCode": error.code})}')

            raise error

        except urllib.error.URLError as error:
            logger.error(
                f'Failed to send health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url, "ErrorCode": error.reason})}')

            raise error

        else:
            logger.debug(
                f'Successfully sent health check: {json.dumps({"BackupName": self.backup_name, "HealthCheckUrl": self.url})}')
