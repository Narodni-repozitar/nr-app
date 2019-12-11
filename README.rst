################
Nušl repozitář
################
*************
Datový model
*************

Elasticsearch
==============
Řešení možných komplikací
---------------------------
1. Nedostatek místa na disku:

Projevuje se tímto tracebackem:

.. code-block:: bash

    elasticsearch.exceptions.AuthorizationException: AuthorizationException(403, 'cluster_block_exception', 'blocked by: [FORBIDDEN/12/index read-only / allow delete (api)];') at 13
    12/02/2019 09:40:36 AM ERROR data {'modified': '2017-06-29T11:15:10', 'contributor': [{'role': 'advisor', 'name': 'Taušer, Josef'}, {'role': 'referee', 'name': 'Taušer, Josef'}], 'doctype': {'$ref': 'https://nusl2.test.ntkcz.cz/api/taxonomies/doctype/diplomove_prace'}, 'accessibility': [{'lang': 'cze', 'name': 'Dostupné v digitálním repozitáři VŠE.'}, {'lang': 'eng', 'name': 'Available in the digital repository of the University of Economics, Prague.'}], 'id': '13', 'abstract': [{'lang': 'cze', 'name': 'Diplomová práce se zabývá efekty přímých zahraničních investic v české ekonomice a zejména jejich vlivem na vnější ekonomickou rovnováhu České republiky. V první části je definován pojem PZI (přímá zahraniční investice), je zde rovněž popsán základní vztah PZI a základních makroekonomických veličin a jak PZI tvarují vnější ekonomickou rovnováhu. Druhá část se zabývá analýzou dynamiky a struktury PZI do české ekonomiky a konečně v třetí stěžejní části práce je analyzován vliv PZI na vnější ekonomickou rovnováhu. Postupně je analyzována platební bilanci, zejména pak projevy PZI v jejích jednotlivých částech. V závěru práce autor zkoumá možnost spojitosti PZI a vyvolání měnové krize.'}], 'language': [{'$ref': 'https://nusl2.test.ntkcz.cz/api/taxonomies/languages/cze'}], 'degreeGrantor': [{'$ref': 'https://nusl2.test.ntkcz.cz/api/taxonomies/universities/61384399_no_faculty_no_department'}], 'title': [{'lang': 'cze', 'name': 'Přímé zahraniční investice a vnější ekonomická rovnováha České republiky'}], 'dateAccepted': '2006-05-21', 'studyField': [{'$ref': 'https://nusl2.test.ntkcz.cz/api/taxonomies/studyfields/6210T010'}], 'creator': [{'name': 'Stříteský, Jan'}], 'pr
    ovider': {'$ref': 'https://nusl2.test.ntkcz.cz/api/taxonomies/provider/vysoka_skola_ekonomicka_v_praze'}, 'identifier': [{'value': 'http://www.vse.cz/vskp/eid/13', 'type': 'originalRecord'}, {'value': 'http://www.nusl.cz/ntk/nusl-13', 'type': 'nusl'}, {'value': 'oai:vse.cz:vskp/13', 'type': 'originalOAI'}, {'value': 'oai:invenio.nusl.cz:13', 'type': 'nuslOAI'}], 'accessRights': 'open'} at 13

Oprava:
 viz: https://github.com/elastic/kibana/issues/13685

.. code-block:: bash

    curl -XPUT -H "Content-Type: application/json" https://[YOUR_ELASTICSEARCH_ENDPOINT]:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'

Často tato oprava nemusí pomoci. Potom je nutné index smazat, znovu vytvořit a spustit reindex.

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
