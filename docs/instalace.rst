***********
Instalace
***********

Instalace ze zdrojového kódu
=============================

0. Instalace Invenia a Invenio-Oarepo

    Invenio NUSL předpokládá nainstalované `Invenio <https://invenio.readthedocs.io/en/stable/quickstart.html>`_ a
    `Invenio OARepo <https://pypi.org/project/invenio-oarepo/>`_.

1. Instalace závislostí

    Nejprve musíme nainstalovat moduly, které chceme pod Inveniem provozovat.
    V tuto chvíli se jedná o **invenio-nusl-common** a **invenio-nusl-theses**

.. code-block::

    pip instal -e <<cesta do složky se setup.py>>

2. Instalace samotného invenio-nusl

    Instalaci spustíme stejně jako předchozí instalace závislostí.

.. code-block::

     pip instal -e <<cesta do složky se setup.py>>

3. Konfigurace invenia *venv/var/instance/invenio.cfg*.
    Příklad invenio.cfg z testovacího serveru:

.. code-block::

    #from invenio_cis_login.remote import CISLoginAuthRemote
    #from hashlib import md5, sha256
    import logging
    logging.getLogger('elasticsearch.trace').setLevel(logging.DEBUG)

    #APP_DEFAULT_SECURE_HEADERS = {
    #  'content_security_policy': {
    #    'default-src': [
    #        '\'self\'',
    #    ],
    #    'script-src': [
    #        '\'sha256-eWKugvnGzWDg1/cLEtGsYUa2Gmocx1sNVm/kWiIxkC0=\'',
    #    ]
    #  }
    #}
    #
    #FILES_REST_PERMISSION_FACTORY = 'cis_theses_repository.permissions.files_permission_factory'

    JSONSCHEMAS_HOST='nusl.cz'
    JSONSCHEMAS_REPLACE_REFS=True
    JSONSCHEMAS_RESOLVE_SCHEMA=True

    SERVER_NAME = 'nusl2.test.ntkcz.cz'

    #APP_ENABLE_SECURE_HEADERS = False

    APP_ALLOWED_HOSTS=[
    '127.0.0.1', 'localhost', '127.0.1.1', 'nusl2.test.ntkcz.cz'
    ]

    #SEARCH_INDEX_PREFIX='oarepo-'

    #INVENIO_EXPLICIT_ACLS_SCHEMA_TO_INDEX = 'invenio_explicit_acls.utils.default_schema_to_index_returning_doc'
    #INDEXER_RECORD_TO_INDEX = 'invenio_explicit_acls.utils.default_record_to_index_returning_doc'

    #INVENIO_OAREPO_UI_LOGIN_URL='/oauth/login/eduid'
    #INVENIO_OAREPO_UI_LOGIN_URL='/oauth/login/cis_login'


    #PIDSTORE_RECID_FIELD='id'
    USERPROFILES_EXTEND_SECURITY_FORMS=False
    #CIS_LOGIN_CONFIG = dict(,,dasdksadisajdoijwqoidjwq)
    #OAUTHCLIENT_REMOTE_APPS = dict(
    ##    eduid=PerunAuthRemote().remote_app()
    #    cis_login=CISLoginAuthRemote().remote_app(),
    #)

4. Invenio Nušl vyžaduje schéma pro drafty. Je nutné nainstalovat **oarepo-invenio-records-draft** ,
    a poté vytvořit JSON schéma a Elasticseacrh mapping. Více v dokumentaci balíčku
    `zde <https://github.com/oarepo/invenio-records-draft>`_.

.. code-block::

    pip install oarepo-invenio-records-draft
    invenio draft make-schemas
    invenio draft make-mappings

5. Nasazení services
    Services jsou dodávány jako docker image. Pro nasazení stačí pustis docker-compose up. Každá verze Elasticsearch má
    specifika. Více o nasazení ES v `dokumentaci <https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html>`_.
    Základní konfigurační yml soubor je k dipozici v `cookiecutter-invenio-instance <https://github.com/inveniosoftware/cookiecutter-invenio-instance>`_.

.. code-block::

    docker-compose up

6. Invenio bootstrap
    Administrátorské rozhraní potřebuje statické soubory. Invenio dodává v `cookiecutter-invenio-instance <https://github.com/inveniosoftware/cookiecutter-invenio-instance>`_
    skript s názvem: bootstrap.sh. Ten instaluje celé Invenio včetně závislostí.
    V případě OARepa není nutné spouštět každy skript, ale spustit jen tyto příkazy:

.. code-block::

    invenio collect -v
    invenio webpack buildall

.. warning::

    Pro příkaz invenio webpack **buildall** je nutné mít nainstalované **NodeJS** a **npm**.
    Alternativou je zkopírovat složky: /assets a /static z /venv/var/instance.

7. Invenio setup
    V této části se nastavuje databáze, elasticsearch, redis a vytváří se admin uživatel. V `cookiecutter-invenio-instance <https://github.com/inveniosoftware/cookiecutter-invenio-instance>`_
    se skript nazývá *setup*.

.. code-block::

    # Clean redis
    invenio shell --no-term-title -c "import redis; redis.StrictRedis.from_url(app.config['CACHE_REDIS_URL']).flushall(); print('Cache cleared')"
    invenio db destroy --yes-i-know
    invenio db init create
    invenio index destroy --force --yes-i-know
    invenio index init --force
    invenio index queue init purge
    invenio files location --default 'default-location'  $(invenio shell --no-term-title -c "print(app.instance_path)")'/data'
    
    # Create admin role to restrict access
    invenio roles create admin
    invenio access allow superuser-access role admin

Instalace přes pip repozitář
=============================

.. todo::

    Dopsat až budou všechny balíčky v pip repozitáři.

Instalace pomocí pip-tools přes requirements
==============================================
#. Nainstalujeme nástroj **pip-tools**

    .. code-block::

        pip install pip-tools

#. Vytvoříme soubor s názvem requirements.in se závislostmi. Poslední funkční in file má tuto podobu:

    .. code-block::

        oarepo[deploy-es7,heartbeat,models,files,includes]~=3.2.1
        Babel>=2.4.0
        Flask-BabelEx>=0.9.3
        lxml>=3.5.0,<4.2.6
        marshmallow>=3.0.0,<4.0.0
        lorem>=0.1.1
        names>=0.3.0
        uwsgi>=2.0
        uwsgi-tools>=1.1.1
        uwsgitop>=0.11
        WTForms==2.2.1

#. Zkompilujeme závislost do requirements.txt:

    .. code-block::

        pip-compile requirements.in > requirements.txt

#. Invenio nainstalujeme přes pip:

    .. code-block::

        pip install -r requirements.txt

Dále pokračujeme bodem 1. jako u instalace ze zdrojového kódu