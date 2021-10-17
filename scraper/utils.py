from typing import Union
from comohay import settings


def get_spider_name_by_source(external_source) -> Union[str, None]:
    """
    Returns a spider name by source according `settings.EXTERNAL_SOURCES`
    :param external_source: External source
    :type external_source: str
    :return: Spider name
    :rtype: str
    """
    for name, source in settings.EXTERNAL_SOURCES.items():
        if source == external_source:
            return name

    return None
