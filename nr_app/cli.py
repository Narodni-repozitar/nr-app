import json
import traceback

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_app.factory import create_api
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_rest.utils import obj_or_import_string
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from tqdm import tqdm


# from nr_cli import nr

@click.group()
def nr_test():
    """Czech National Repository cli commands."""
    pass


@nr_test.command('reindex')
@click.option(
    '--raise-on-error/--skip-errors', default=True,
    help='Controls if Elasticsearch bulk indexing errors raise an exception.')
@click.option(
    '--only',
    help='Index only this item')
@with_appcontext
@click.pass_context
def nr_reindex(ctx, raise_on_error=True, only=None):
    version_type = None  # elasticsearch version to use
    api = create_api()
    with api.app_context():
        def reindex_pid(pid_type, RecordClass):
            index_name = None
            indexer = RecordIndexer()
            pids = PersistentIdentifier.query.filter_by(pid_type=pid_type, object_type='rec',
                                                      status=PIDStatus.REGISTERED.value).all()
            for pid in pids:
                record = RecordClass.get_record(pid.object_uuid)
                if only and str(record.id) != only:
                    continue
                try:
                    index_name, doc_type = indexer.record_to_index(record)
                    index_name = build_alias_name(index_name)
                    # print('Indexing', record.get('id'), 'into', index_name)
                    indexer.index(record)
                except:
                    with open('/tmp/indexing-error.json', 'a') as f:
                        print(json.dumps(record.dumps(), indent=4, ensure_ascii=False), file=f)
                        traceback.print_exc(file=f)
                    if raise_on_error:
                        raise
            if index_name:
                current_search_client.indices.refresh(index_name)
                current_search_client.indices.flush(index_name)

        # reindex all objects
        endpoints = current_app.config.get("RECORDS_REST_ENDPOINTS").endpoints
        for config in endpoints.values():
            try:
                pid_type: str = config["pid_type"]
                record_class = obj_or_import_string(config["record_class"])
            except:
                raise
            print(f"pid_type: {pid_type}")
            reindex_pid(pid_type, record_class)
