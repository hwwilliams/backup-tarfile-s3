import logging

botocore_auth_logger = logging.getLogger('botocore.auth')
botocore_auth_logger.setLevel(logging.WARNING)

botocore_awsrequest_logger = logging.getLogger('botocore.awsrequest')
botocore_awsrequest_logger.setLevel(logging.WARNING)

botocore_client_logger = logging.getLogger('botocore.client')
botocore_client_logger.setLevel(logging.WARNING)

botocore_credentials_logger = logging.getLogger('botocore.credentials')
botocore_credentials_logger.setLevel(logging.WARNING)

botocore_endpoint_logger = logging.getLogger('botocore.endpoint')
botocore_endpoint_logger.setLevel(logging.WARNING)

botocore_handlers_logger = logging.getLogger('botocore.handlers')
botocore_handlers_logger.setLevel(logging.WARNING)

botocore_hooks_logger = logging.getLogger('botocore.hooks')
botocore_hooks_logger.setLevel(logging.WARNING)

botocore_loaders_logger = logging.getLogger('botocore.loaders')
botocore_loaders_logger.setLevel(logging.WARNING)

botocore_parsers_logger = logging.getLogger('botocore.parsers')
botocore_parsers_logger.setLevel(logging.WARNING)

botocore_retryhandler_logger = logging.getLogger('botocore.retryhandler')
botocore_retryhandler_logger.setLevel(logging.WARNING)

botocore_utils_logger = logging.getLogger('botocore.utils')
botocore_utils_logger.setLevel(logging.WARNING)

s3transfer_futures_logger = logging.getLogger('s3transfer.futures')
s3transfer_futures_logger.setLevel(logging.WARNING)

s3transfer_tasks_logger = logging.getLogger('s3transfer.tasks')
s3transfer_tasks_logger.setLevel(logging.WARNING)

s3transfer_utils_logger = logging.getLogger('s3transfer.utils')
s3transfer_utils_logger.setLevel(logging.WARNING)

urllib3_connectionpool_logger = logging.getLogger('urllib3.connectionpool')
urllib3_connectionpool_logger.setLevel(logging.WARNING)
