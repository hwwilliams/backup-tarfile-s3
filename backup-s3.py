import argparse
import logging

# from systemd import journal
from backup_process.initialize import Process


def configure_logging():
    logging.getLogger(__name__)
    loggingformat = ' %(levelname)s :: %(name)s :: %(message)s'
    logging.basicConfig(level=logging.INFO, format=loggingformat)
    # journald_handler = journal.JournalHandler()
    # journald_handler.setFormatter(logging.Formatter(
    #     '[%(levelname)s] %(message)s'
    # ))
    # logger.addHandler(journald_handler)


def argument_parser():
    description_text = 'Test program text'
    parser = argparse.ArgumentParser(description=description_text)
    required_arguments = parser.add_argument_group('required arguments')
    required_arguments.add_argument(
        "-C", "--config", help="Give me backup config", required=True)
    return parser.parse_args()


def handle_arguments(arguments):
    if arguments.config:
        Process(arguments.config)


def main():
    configure_logging()
    arguments = argument_parser()
    handle_arguments(arguments)


if __name__ == "__main__":
    main()
