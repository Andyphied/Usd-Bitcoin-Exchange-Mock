import logging.config
import yaml

from core.middleware import get_request_id, get_correlation_id


class AppFilter(object):
    def filter(self, record):

        record.correlation_id = get_correlation_id()
        record.request_id = get_request_id()
        return True


def setup_logging():
    with open('logging.yaml') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    logging.config.logging.config.dictConfig(conf)