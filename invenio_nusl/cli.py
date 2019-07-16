import json

import click
from flask import cli

from flask_taxonomies.managers import TaxonomyManager
from flask_taxonomies.models import Taxonomy, TaxonomyTerm
from invenio_db import db
# from invenio_db import InvenioDB


@click.group()
def nusl():
    """Nusl commands."""


@cli.with_appcontext
@nusl.command('import_studyfields')
def import_studyfields():
    studyfields = Taxonomy(code='studyfields', extra_data={
        "title": [
            {
                "name": "studijní obory",
                "lang": "cze"
            },
            {
                "name": "study fields",
                "lang": "eng"
            }
        ]
    }
                           )

    db.session.add(studyfields)
    db.session.commit()
    # manager = TaxonomyManager()
    # term = manager.create('6208R082',
    #                       title={
    #                           "name": "Podnikatelská činnost",
    #                       },
    #                       path='/studyfields/',
    #                       extra_data={"code": "6208R082"})
    # print(studyfields, term)
    #
    # db.session.add(studyfields)
    # db.session.add(term)
    # db.session.commit()


if __name__ == "__main__":
    import_studyfields()
