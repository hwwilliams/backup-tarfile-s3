import json
import logging

logger = logging.getLogger(__name__)


class CleanBackupConfig():
    def __init__(self, backup_config):
        self.config = backup_config

        self.name = self.config['Name']
        self.hc_url = self.config['HealthCheckUrl']
        self.compression = self.config['TarCompression']

        self.destination = self.config['Destination']
        self.bucket = self.destination['Bucket']
        self.file_prefix = self.destination['FilePrefix']
        self.extra_upload_args = self.destination['UploadExtraArgs']

        self.sources = self.config['Sources']

        clean_name = str(self.name).lower().replace(' ', '-')
        self.config['TarOutputName'] = f'{clean_name}.{self.compression}.tar'
