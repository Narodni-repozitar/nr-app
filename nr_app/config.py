from flask_babelex import lazy_gettext as _
import jsonresolver

SUPPORTED_LANGUAGES = ['cs', 'en', 'sk', 'de', 'fr', 'ru', 'es', 'nl', 'it', 'no', 'pl', 'da', 'el',
                       'hu', 'lt', 'pt', 'bg', 'ro', 'sv']

JSONSCHEMAS_HOST = 'repozitar.narodni-repozitar.cz'

BABEL_DEFAULT_LOCALE = 'cs'
I18N_LANGUAGES = (('en', _('English')), ('cs', _('Czech')))
I18N_SESSION_KEY = 'language'
I18N_SET_LANGUAGE_URL = '/api/lang'

ELASTICSEARCH_DEFAULT_LANGUAGE_TEMPLATE = {
    "type": "text",
    "fields": {
        "raw": {
            "type": "keyword"
        }
    }
}

ELASTICSEARCH_LANGUAGE_TEMPLATES = {
    "*#subjectAll": {
        "type": "text",
        "copy_to": "subjectAll.*",
        "fields": {
            "raw": {
                "type": "keyword"
            }
        }
    }

}

# communities
OAREPO_COMMUNITIES_ROLES = ['member', 'curator', 'publisher']
"""Roles present in each community."""

# added automatically
# OAREPO_COMMUNITIES_ENDPOINTS = []

OAREPO_COMMUNITIES_PRIMARY_COMMUNITY_FIELD = '_primary_community'
OAREPO_COMMUNITIES_COMMUNITIES_FIELD = 'communities'
# OAREPO_COMMUNITIES_PRIMARY_COMMUNITY_FIELD = '_administration.primaryCommunity'
# OAREPO_COMMUNITIES_COMMUNITIES_FIELD = '_administration.communities'
OAREPO_COMMUNITIES_OWNED_BY_FIELD = '_administration.ownedBy'

OAREPO_FSM_ENABLED_REST_ENDPOINTS = [

]


# hack to serve schemas both on jsonschemas host and server name (if they differ)
@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """JSON resolver plugin that loads the schema endpoint.

    Injected into Invenio-Records JSON resolver.
    """
    from flask import current_app
    from invenio_jsonschemas import current_jsonschemas
    from werkzeug.routing import Rule
    url_map.add(Rule(
        "{0}/<path:path>".format(current_app.config['JSONSCHEMAS_ENDPOINT']),
        endpoint=current_jsonschemas.get_schema,
        host=current_app.config['SERVER_NAME']))


# global config
FLASK_TAXONOMIES_URL_PREFIX = '/api/2.0/taxonomies/'
PREFERRED_URL_SCHEME = 'https'
RATELIMIT_ENABLED = True
RATELIMIT_PER_ENDPOINT = {
    'oarepo_records_draft.draft-datasets_presigned_part': '25000 per hour'
}

# TODO: csrf will be enabled by default in the next invenio
REST_CSRF_ENABLED = False
CSRF_HEADER = 'X-CSRFTOKEN'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# for CSRF etc to work; normally set to /api in uAPI
# as the main content is at / (or any path other than /api), the cookie is normally
# not accessible on document.cookies and csrf header can not thus be sent.
# This workaround sets the cookie on / - this is not nice but works.
#
# Alternative solution is to add axios interceptor on the client side to fetch the CSRF
# cookie from the first (options) request but there are cases where the request is not
# made and a retry logic would be needed.
SESSION_COOKIE_PATH = '/'

OAISERVER_ID_PREFIX = 'oai:narodni-repozitar.cz:'


from cesnet_openid_remote.remote import CesnetOpenIdRemote
OAUTHCLIENT_REST_REMOTE_APPS = dict(
    eduid=CesnetOpenIdRemote().remote_app(),
)

import os

ES_USER = os.getenv('OAREPO_ES_USER', None)
ES_PASSWORD = os.getenv('OAREPO_ES_PASSWORD', None)
ES_PARAMS = {}

if ES_USER and ES_PASSWORD:
    ES_PARAMS = dict(http_auth=(ES_USER, ES_PASSWORD))

SEARCH_ELASTIC_HOSTS = [dict(host=h, **ES_PARAMS) for h in
                        os.getenv('OAREPO_SEARCH_ELASTIC_HOSTS', 'localhost').split(',')]

APP_ALLOWED_HOSTS = [h for h in os.getenv('OAREPO_APP_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]

INDEXER_RECORD_TO_INDEX = 'nr_app.indexer.record_to_index'

NR_ES_TYPED_KEYS = True

OAREPO_SEARCH_DEFAULT_INDEX = 'draft-nr_common-nr-common-v1.0.0'

if False:
    import logging

    es_trace_logger = logging.getLogger('elasticsearch.trace')
    es_trace_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    es_trace_logger.addHandler(handler)

FILES_REST_STORAGE_FACTORY = 'oarepo_s3.storage.s3_storage_factory'
