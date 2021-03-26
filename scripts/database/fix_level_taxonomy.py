import logging
from copy import deepcopy
from urllib.parse import urlparse

from sqlalchemy import create_engine, MetaData, update

logger = logging.getLogger("fix_valid_error")
formatter = logging.Formatter(
    '%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def run():
    engine = create_engine('postgresql+psycopg2://oarepo:oarepo@localhost/oarepo')

    META_DATA = MetaData(bind=engine, reflect=True)

    records_metadata = META_DATA.tables['records_metadata']

    s = records_metadata.select()

    result = engine.execute(s)

    for idx, row in enumerate(result):
        json_ = row.json
        id_ = row.id
        new_json = deepcopy(json_)
        new_json = change_taxonomy(new_json)
        if not new_json or (json_ == new_json):
            logger.info(f"{idx}. Record with id: {id_} have been already modified")
            continue
        s = update(records_metadata).where(
            records_metadata.c.id == id_
        ).values(
            json=new_json
        )
        engine.execute(s)
        logger.info(f"{idx}. Updated record with id: {id_}")


def change_taxonomy(value, result=None):
    if not result:
        result = {}
    if isinstance(value, (list, tuple)):
        return [change_taxonomy(_) for _ in value]
    if isinstance(value, dict):
        if "is_ancestor" in value.keys() and "links" in value.keys():
            value = add_level(value)
        for k, v in value.items():
            result[k] = change_taxonomy(v)
    else:
        return value
    return result


def add_level(value):
    if "level" in value:
        return value
    url = value["links"]["self"]
    parsed_url = urlparse(url)
    path_arr = parsed_url.path.split("/")
    level = -1
    for _ in path_arr[::-1]:
        if _ == "taxonomies":
            break
        else:
            level += 1
    value["level"] = level
    return value


if __name__ == '__main__':
    run()
