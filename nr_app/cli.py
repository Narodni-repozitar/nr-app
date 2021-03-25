from datetime import datetime

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_app.factory import create_api
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest.utils import obj_or_import_string
from nr_cli import nr
from sqlalchemy.orm.exc import NoResultFound
from tqdm import tqdm

from nr_app.index import reindex_pid


@nr.group()
def index():
    pass


@nr.group()
def records():
    pass


@index.command('reindex')
@click.option('--pid', '-p', 'pids', multiple=True,
              help="Please choose PID that will be reindexed. Default option is all PIDs")
@click.option(
    '--raise-on-error/--skip-errors', default=True,
    help='Controls if Elasticsearch bulk indexing errors raise an exception.')
@click.option(
    '--only',
    help='Index only this item')
@with_appcontext
@click.pass_context
def nr_reindex(ctx, pids, raise_on_error=True, only=None):
    version_type = None  # elasticsearch version to use
    api = create_api()
    with api.app_context():
        endpoints = current_app.config.get("RECORDS_REST_ENDPOINTS").endpoints
        if not pids:
            # reindex all objects
            for config in endpoints.values():
                pid_type: str = config["pid_type"]
                record_class = obj_or_import_string(config["record_class"])
                print(f"pid_type: {pid_type}")
                reindex_pid(pid_type, record_class, only=only, raise_on_error=raise_on_error)
        else:
            for p in pids:
                config = [ep for ep in endpoints.values() if ep["pid_type"] == p][0]
                if not config:
                    raise ValueError(f'There is not PID type with the value: "{p}"')
                pid_type: str = config["pid_type"]
                record_class = obj_or_import_string(config["record_class"])
                reindex_pid(pid_type, record_class, only=only, raise_on_error=raise_on_error)


@records.command('recommit')
@with_appcontext
@click.pass_context
def nr_recommit(ctx):
    api = create_api()
    with api.app_context():
        endpoints = current_app.config.get("RECORDS_REST_ENDPOINTS").endpoints
        for config in endpoints.values():
            try:
                pid_type: str = config["pid_type"]
                print(f'PID type: {pid_type}')
                record_class = obj_or_import_string(config["record_class"])
                pids = PersistentIdentifier.query.filter_by(pid_type=pid_type).all()
                for i, pid in enumerate(tqdm(pids)):
                    try:
                        record = record_class.get_record(pid.object_uuid)
                    except NoResultFound:
                        continue
                    t0 = datetime.now()
                    record.commit()
                    print(f"Commiting time: {datetime.now()-t0}")
                    if i % 100 == 0:
                        db.session.commit()
            finally:
                db.session.commit()
