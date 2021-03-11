import json
import traceback

from invenio_indexer.api import RecordIndexer
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_search import current_search_client
from invenio_search.utils import build_alias_name
from tqdm import tqdm


def reindex_pid(pid_type, RecordClass, only: bool = False, raise_on_error=None):
    index_name = None
    indexer = RecordIndexer()
    pids = PersistentIdentifier.query.filter_by(pid_type=pid_type, object_type='rec',
                                                status=PIDStatus.REGISTERED.value).all()
    for pid in tqdm(pids):
        record = RecordClass.get_record(pid.object_uuid)
        keywords = record.get("keywords")
        if keywords:
            if keywords == "Keywords must be fixed in draft mode":
                del record["keywords"]
        if "rulesExceptions" in record.keys():
            new_array = []
            for _ in record["rulesExceptions"]:
                _["element"] = str(_["element"])
                new_array.append(_)
            record["rulesExceptions"] = new_array
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
