# import time
#
import click


# import invenio_indexer.api
# import invenio_indexer.cli
# # from elasticsearch import NotFoundError
# from flask import cli
# from invenio_db import db
# from invenio_oarepo.current_api import current_api
# from invenio_pidstore.models import RecordIdentifier
# from invenio_records.models import RecordMetadata
# # from invenio_search import current_search_client
# from sqlalchemy.exc import IntegrityError
#
#
# # from invenio_oarepo_oai_pmh_harvester.migration import OAIMigration
# # from invenio_oarepo_oai_pmh_harvester.models import OAIProvider
#
#
@click.group()
def nusl():
    """Nusl commands."""
    pass

@nusl.command("test")
def test_command():
    print("Test command")
#
#
# ########################################################################################
# #                                           Index                                      #
# ########################################################################################
#
#
# @nusl.command('reindex')
# @cli.with_appcontext
# @click.pass_context
# def reindex(ctx):
#     with current_api.app_context():
#         print("Purging queue...")
#         ctx.invoke(invenio_indexer.cli.purge_queue)
#         print("Push index to the queue...")
#         ctx.invoke(invenio_indexer.cli.reindex, pid_type='dnusl', yes_i_know=True)
#         time.sleep(2)
#         print("Running reindex...")
#         ctx.invoke(invenio_indexer.cli.run)
#         # invenio_indexer.api.RecordIndexer(version_type=None).process_bulk_queue(
#         #     es_bulk_kwargs={'raise_on_error': True})
#
#
# ########################################################################################
# #                                           Migration                                  #
# ########################################################################################
# @nusl.group()
# def migration():
#     pass
#
#
# # TODO: vložit do OAI-PMH knihovny
# # @migration.command('oai')
# # @cli.with_appcontext
# # def migrate_oai():
# #     def oai_id_handler(json):
# #         id_ = json["id"]
# #         try:
# #             doc = current_search_client.get(index="nusl_marcxml", id=id_)
# #         except NotFoundError:
# #             return
# #         oai_id = doc["_source"].get("035__") or {}
# #         oai_id = oai_id.get("a")
# #         if oai_id:
# #             return oai_id
# #
# #     provider = OAIProvider.query.filter_by(code="nusl").one_or_none()
# #     if not provider:
# #         provider = OAIProvider(
# #             code="nusl",
# #             description="Původní NUŠL na Invenio v1",
# #             oai_endpoint="https://invenio.nusl.cz/oai2d/",
# #             metadata_prefix="marcxml"
# #         )
# #         db.session.add(provider)
# #         db.session.commit()
# #     migrator = OAIMigration(handler=oai_id_handler, provider=provider)
# #     migrator.run()
#
#
# @migration.command('pid')
# @cli.with_appcontext
# def migrate_old_pid():
#     records = RecordMetadata.query.paginate()
#     while_condition = True
#     idx = 0
#     try:
#         while while_condition:
#             for record in records.items:
#                 idx += 1
#                 pid = record.json["id"]
#                 recid = RecordIdentifier.query.get(pid)
#                 if recid:
#                     continue
#                 recid = RecordIdentifier(recid=pid)
#                 db.session.add(recid)
#                 print(f"{idx}. {pid} has been added")
#                 if idx % 100 == 0:  # pragma: no cover
#                     db.session.commit()
#                     print("Session was commited")
#             while_condition = records.has_next
#             records = records.next()
#     except IntegrityError:  # pragma: no cover
#         db.session.rollback()
#         raise
#     else:
#         db.session.commit()
#     finally:
#         db.session.commit()
