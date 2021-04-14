import traceback

from flask_taxonomies.proxies import current_flask_taxonomies
from invenio_app.factory import create_api
from invenio_db import db
from oarepo_communities.api import OARepoCommunity
from oarepo_communities.errors import OARepoCommunityCreateError
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm

app = create_api()


def run():
    for res in tqdm(current_flask_taxonomies.list_taxonomy('institutions', return_descendants_count=True)):
        tax = res.TaxonomyTerm
        if tax.level > 0:
            continue
        with db.session.begin_nested():
            primary_community = tax.slug.strip('/').rsplit('/', maxsplit=1)[-1]
            title = tax.extra_data.get('title', {}).get('cs')
            provider_type = tax.extra_data.get('type', ['neznámý'])[0]
            # TODO: fix this
            if len(primary_community) > 60 or not title:
                continue
            comm_data = {
                # "curation_policy": policy,
                "id": primary_community,
                "description": f'{provider_type} - {title}',
                # TODO: "logo": "data/community-logos/ecfunded.jpg"
            }
            try:
                comm = OARepoCommunity.create(
                    comm_data,
                    id_=primary_community,
                    title=title,
                    ctype='other'
                )
            except IntegrityError:
                traceback.print_exc()
            except OARepoCommunityCreateError as e:
                traceback.print_exc()

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        run()
