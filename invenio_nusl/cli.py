import click
import invenio_indexer.api
import invenio_indexer.cli
from flask import cli

from invenio_oarepo.current_api import current_api


@click.group()
def nusl():
    """Nusl commands."""


################################################################################################################
#                                           Index
#                                           #
################################################################################################################


@nusl.command('reindex')
@cli.with_appcontext
@click.pass_context
def reindex(ctx):
    with current_api.app_context():
        ctx.invoke(invenio_indexer.cli.reindex, pid_type='dnusl')
        invenio_indexer.api.RecordIndexer(version_type=None).process_bulk_queue(
            es_bulk_kwargs={'raise_on_error': True})
