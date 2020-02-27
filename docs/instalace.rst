===========
Instalace
===========

Instalace ze zdrojového kódu
-----------------------------
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

3. Nyní je nutné nastavit ve *venv/var/instance/invenio.cfg* SERVER_NAME.
    Pro lokální vývoj nastavíme SERVER_NAME = "127.0.0.1"

4. Invenio Nušl vyžaduje schéma pro drafty. Je nutné nainstalovat **oarepo-invenio-records-draft** ,
    a poté vytvořit JSON schéma a Elasticseacrh mapping. Více v dokumentaci balíčku
    `zde <https://github.com/oarepo/invenio-records-draft>`_.

.. code-block::

    pip install oarepo-invenio-records-draft
    invenio draft make-schemas
    invenio draft make-mappings

Instalace přes pip repozitář
-----------------------------

.. todo::

    Dopsat až budou všechny balíčky v pip repozitáři.