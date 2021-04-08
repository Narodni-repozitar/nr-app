import itertools
import time
from multiprocessing.pool import Pool
from random import random

from invenio_app.factory import create_api
from invenio_db import db
from invenio_records.models import RecordMetadata
from sqlalchemy.orm.attributes import flag_modified
from tqdm import tqdm

app = create_api()


def set_providers(*mds):
    with app.app_context():
        with db.session.begin_nested():
            for md in RecordMetadata.query.filter(RecordMetadata.id.in_(mds)):
                control_number = md.json.get('control_number')
                print(f"Control number: {control_number}")
                providers = md.json.get('provider')

                primary_community = None

                if providers:
                    provider = None
                    for p in providers:
                        if not provider or p['level'] > provider['level']:
                            provider = p
                    provider = providers[0]
                    self_link = provider.get('links', {}).get('self')
                    if self_link:
                        primary_community = self_link.strip('/').rsplit('/', maxsplit=1)[-1]

                md.json['_administration'] = {
                    "state": 'new',
                    "primaryCommunity": primary_community,
                    "communities": []
                }
                flag_modified(md, 'json')
                db.session.add(md)
        db.session.commit()


def grouper(n, iterable):
    iterable = iter(iterable)
    return iter(lambda: list(itertools.islice(iterable, n)), [])


def initiate():
    time.sleep(10 * random())


def run():
    md_stream = [x[0] for x in db.session.query(RecordMetadata.id).distinct()]
    md_stream = list(grouper(1000, md_stream))
    with Pool(processes=1, initializer=initiate) as pool:
        pool.starmap(set_providers, tqdm(md_stream))
    pool.join()


if __name__ == '__main__':
    with app.app_context():
        run()
