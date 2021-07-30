import json
import os
import tempfile
from datetime import datetime
from os.path import basename

import click
from flask import current_app
from flask.cli import with_appcontext
from jsonref import JsonRef, JsonRefError
from invenio_app.factory import create_api
from invenio_db import db
from invenio_jsonschemas.proxies import current_jsonschemas
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest.utils import obj_or_import_string
from sqlalchemy.orm.exc import NoResultFound
from tqdm import tqdm
from invenio_records.api import _records_state

from nr_app.index import reindex_pid


@click.group()
def nr():
    """Czech National Repository cli commands."""
    pass


@nr.group()
def index():
    pass


@nr.group()
def docs():
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
                    print(f"Commiting time: {datetime.now() - t0}")
                    if i % 100 == 0:
                        db.session.commit()
            finally:
                db.session.commit()


@docs.command('build')
@click.argument('schemas', nargs=-1)
@with_appcontext
def build_docs(schemas):
    """Generates API docs for included / specified data models."""
    from json_schema_for_humans.generate import generate_from_file_object

    for schema_path in schemas or current_jsonschemas.list_schemas():
        click.secho(f'Generating docs for schema {schema_path}')
        schema = current_jsonschemas.get_schema(schema_path, with_refs=False, resolved=False)

        try:
            schema = JsonRef.replace_refs(
                schema,
                jsonschema=True,
                base_uri=current_app.config.get('JSONSCHEMAS_HOST'),
                loader=_records_state.loader_cls(),
            )

            # TODO: this is necessary to resolve JSONRefs in allOf
            schema = json.loads(json.dumps(schema, default=lambda x: x.__subject__))

            # Resolve definition schemas
            if 'definitions' in schema:
                definitions = list(schema['definitions'].keys())
                # Consider only a first definition as a schema for now
                schema = schema['definitions'][definitions[0]]

            click.secho(f'Schema resolved to: {json.dumps(schema)}', color='blue')


        except JsonRefError as e:
            click.secho(f'Error resolving schema: {e}. Skipping...', color='red')
            continue

        # Generate and save html docs for the schema
        with tempfile.NamedTemporaryFile(mode="w+") as schema_source:
            schema_source.write(json.dumps(schema))
            schema_source.flush()

            with open(f'docs/schemas/{basename(schema_path.rstrip(".json"))}.html', mode='w+') as result_file:
                click.secho(f'Writing schema docs to {result_file.name}', color='green')
                generate_from_file_object(
                    schema_file=schema_source,
                    result_file=result_file,
                    minify=True,
                    expand_buttons=True
                )

    # Generate and save schema index page
    index_md = r"""---
layout: default
---

# Data Models Schema Docs

"""
    for f in os.listdir('docs/schemas/'):
        if f.endswith('.html'):
            index_md += f'- [{f.rstrip(".html")}](./{f})\n'

    with open(f'docs/schemas/index.md', mode='w+') as index_file:
        index_file.write(index_md)
