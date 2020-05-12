import json
import logging
import shutil
import tempfile

logger = logging.getLogger(__name__)


class TemporaryDirectory(object):
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        logger.debug(
            f'Created temp directory: {json.dumps({"Directory": self.name})}')
        return self.name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.name)
        logger.debug(
            f'Destroyed temp directory: {json.dumps({"Directory": self.name})}')
