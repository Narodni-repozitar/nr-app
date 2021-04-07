import json

from invenio_app.factory import create_api
from invenio_db import db
from invenio_records.models import RecordMetadata
from sqlalchemy.orm.attributes import flag_modified
from tqdm import tqdm

app = create_api()


def run():
    print('Running que ry')
    for md in tqdm(
            db.session.query(RecordMetadata).yield_per(10000),
            total=db.session.query(RecordMetadata).count()
    ):
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


if __name__ == '__main__':
    with app.app_context():
        run()
