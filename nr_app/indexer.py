from oarepo_records_draft.record import record_to_index as draft_record_to_index


def record_to_index(record):
    index = getattr(record, 'index_name', None)
    if index:
        return index, '_doc'

    return draft_record_to_index(record)
