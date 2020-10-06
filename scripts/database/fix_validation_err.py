import logging
from copy import deepcopy

from invenio_records_draft.utils import parse_marshmallow_messages
from sqlalchemy import create_engine, MetaData, update

# TODO: přepracovat s novými migračními skripty

logger = logging.getLogger("fix_valid_error")
formatter = logging.Formatter(
    '%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def run():
    engine = create_engine('postgresql+psycopg2://oarepo:oarepo@nusl2.test.ntkcz.cz/oarepo')

    META_DATA = MetaData(bind=engine, reflect=True)

    records_metadata = META_DATA.tables['records_metadata']

    s = records_metadata.select()

    result = engine.execute(s)

    for idx, row in enumerate(result):
        json_ = row.json
        id_ = row.id
        new_json = deepcopy(json_)
        new_json["invenio_draft_validation"] = parse_json(json_)
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


def parse_json(data):
    data = deepcopy(data)
    invenio_draft_validation = data.setdefault('invenio_draft_validation', {"valid": True})
    if not invenio_draft_validation.get("valid", True):
        errors = invenio_draft_validation.get("errors")
        if errors:
            marshmallow = errors.get("marshmallow")
            if marshmallow and not isinstance(marshmallow, list):
                marshmallow = parse_marshmallow_messages(marshmallow)
                errors["marshmallow"] = marshmallow
                invenio_draft_validation["errors"] = errors
    return invenio_draft_validation


if __name__ == '__main__':
    run()
