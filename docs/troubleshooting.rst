*****************
Řešení problémů
*****************

Invenio
========

1. JsonRef nenalezne referenci, nejčastěji při indexaci do ES
---------------------------------------------------------------

Je nutné zkontrolovat celou URL adresu:

* HOST by se měl shodovat se SERVER_NAME v konfiguraci (invenio.cfg)
* PATH by na konci měla končit lomítkem (jedná se o bug ve Flasku)

Flask-Taxonomies
=================

1. Aplikaci chybí API kontext:
--------------------------------

    Projevuje se touto chybou:

    .. code-block:: bash

         File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask/cli.py", line 426, in decorator
        return __ctx.invoke(f, *args, **kwargs)
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/click/core.py", line 555, in invoke
        return callback(*args, **kwargs)
      File "/home/semtex/Projekty/nusl/invenio-nusl-taxonomies/invenio_nusl_taxonomies/cli.py", line 214, in reindex
        term_json = get_taxonomy_term(code=node.taxonomy.slug, slug=node.slug)
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask_taxonomies/jsonresolver.py", line 58, in get_taxonomy_term
        term.parent.tree_path or '', parents)
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask_taxonomies/views.py", line 177, in jsonify_taxonomy_term
        "links": current_flask_taxonomies.term_links(taxonomy_code, path, parent_path),
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask_taxonomies/ext.py", line 43, in term_links
        return self.api.term_links(taxonomy_code, path, parent_path)
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask_taxonomies/api.py", line 159, in term_links
        _external=True,
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask/helpers.py", line 370, in url_for
        return appctx.app.handle_url_build_error(error, endpoint, values)
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask/app.py", line 2215, in handle_url_build_error
        reraise(exc_type, exc_value, tb)
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask/_compat.py", line 39, in reraise
        raise value
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/flask/helpers.py", line 358, in url_for
        endpoint, values, method=method, force_external=external
      File "/home/semtex/Projekty/nusl/venv/lib/python3.7/site-packages/werkzeug/routing.py", line 2020, in build
        raise BuildError(endpoint, values, method, self)
        werkzeug.routing.BuildError: Could not build url for endpoint 'taxonomies.taxonomy_get_term' with values ['taxonomy_code', 'term_path']. Did you mean 'actionroles.ajax_update' instead?

    Oprava:

    Pokud tato situace nastane, je nutné aplikaci poskytnou Invenio API kontext, tímto způsobem:

    .. code-block:: python

        api = current_app.wsgi_app.mounts['/api']
        with api.app_context():
            <kód, který vyžaduje kontext>

Elasticsearch
==============

1. Nedostatek místa na disku:
------------------------------

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