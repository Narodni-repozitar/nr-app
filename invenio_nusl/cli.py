import json

import click
from flask.cli import with_appcontext

from flask_taxonomies.managers import TaxonomyManager
from flask_taxonomies.models import Taxonomy, TaxonomyTerm


@click.group()
def nusl():
    """Nusl commands."""


@with_appcontext
@nusl.command('import_taxonomies')
@click.option("-p", "--path", type=click.STRING)
def import_taxonomies(path):
    with open(path, "r") as f:
        taxonomy_dict = json.load(f)

    for k in taxonomy_dict.keys():
        print(k)
    # t = Taxonomy(code='vskp')
    # m = TaxonomyManager()
    # term = m.create('bakalarske_prace', title={'cs': 'Bakalářské práce'}, path='/vskp/', extra_data={})

    # db.session.add()
    # db.session.commit()
