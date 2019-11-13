################
Nušl repozitář
################
*************
Datový model
*************

Změna datového modelu
======================

1. Změna modulu: invenio-initial-theses-conversion
----------------------------------------------------------
V složce invenio-initial-theses-conversion/invenio_initial_theses_conversion/rules se změní konverzní python kód.
Změnu otestujeme (tests/test_rules.py)

2. Marshmallow
----------------------------------------------------------
* V souboru invenio_nusl_***/marshmallow/json.py se změní marshmallow schéma
* Změna modulu se náležitě otestuje (tests/test_marshmallow.py)

3. JSON-schema
----------------------------------------------------------
* Schéma se mění v souboru invenio_nusl_***/jsonschemas/invenio_nusl_***/nusl-theses-v1.0.0.json
* Pokud je položka taxonomie, tak se jen odkáže na taxonomická schémata např.:

.. code-block:: javascript

    "language": {
            "$ref": "../taxonomy-v1.0.0.json#/definitions/TaxonomyTermArray"
        }


4. Elasticsearch mappings
----------------------------
* Schéma se mění v souboru invenio_nusl_***/mappings/v6/invenio_nusl_***/nusl-theses-v1.0.0.json
* Rozvětvená schémata se ukládají do složky invenio_nusl_***/included_mappings/v6 a odkazuje se na ně pomocí slova type:

.. code-block:: javascript

    "title": {
                    "type": "nusl-common-v1.0.0.json#/multilanguage"
                }

* Na taxonomická schémata se odkazuje:

.. code-block:: javascript

    "language": {
                    "type": "taxonomy-v1.0.0.json#/TaxonomyTerm"
                }

5. Vytvoření draftového JSON schématu a ES mappingu
---------------------------------------------------
* Vytvoření draft JSON schématu:

.. code-block:: bash

    invenio draft make-schemas

* Vytvoření draft ES mappingu:

.. code-block:: bash

    invenio draft make-mappings

6. Vytvoření nového indexu
---------------------------

1. Smazání starého indexu:

.. code-block:: bash

    invenio index destroy

2. Kontrola jestli byly indexy smazané (neměly by být indexy přítomné:

.. code-block:: bash

    GET http://localhost:9200/_cat/indices?v

3. Vytvoření nového indexu

.. code-block:: bash

    invenio index init

4. Kontrola jestli se nové indexy vytvořily (měly by být přítomné dva indexy draft a "ostrý")

.. code-block:: bash

    GET http://localhost:9200/_cat/indices?v

5. V případě správných dat v databázi se index přeindexuje následujícími příkazy:

.. code-block:: bash

    invenio index reindex -t dnusl
    invenio nusl reindex
