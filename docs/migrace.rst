*****************
Migrace
*****************

Migrací se rozumí migrace dat a perzistentních identifikátorů ze staré služby Národního uložiště šedé literatury (NUŠL)
běžící na systému Invenio verze 1 do nové služby Národního repozitáře (NR) pracovně nazývaného Chiméra.

Předpoklady
============

Tato kapitola předpokládá, že proběhla úspěšně :doc:`instalace <instalace>`.

Postup
=======

CLI skripty
=============

Migrace metadat
-----------------
Za migraci metadat je zodpovědný modul invenio-initial-theses-conversion. Volá se příkazem:

.. code-block::

    ivneio initial_theses_conversion [OPTIONS]

| OPTIONS:
| --url: počáteční adresa odkud se mají stahovat metadata
| --cache-dir: cesta k adresáři, kde je uložená cache/kam se má uložit cache
| --break-on-error/--no-break-on-error: přepínač, který potlačí/povolí vyjímky
| --clean-output-dir/--no-clean-output-dir: přepínač, který vymaže/ponechá minulé logy
| --start: číslo počátečního záznamu (pořadové, nikoliv NUŠL id)
| --stop: číslo konečného záznamu

Migrace OAI identifikátorů
---------------------------

OAI identifikátory je nutné synchronizovat s novým systémem. Migraci těchto identifikátorů zavoláme příkazem:

.. code-block:: console

    invenio nusl migrate oai

Migrace PID identifikátorů
---------------------------

Pro správné přidělování nových identifikátorů je nutné převést staré NUŠL identifikátory do nové databáze. Pro ukládání
identifikátorů je využita Invenio třída RecordIdentifier
`(tabulka pidstore_recid) <https://github.com/inveniosoftware/invenio-pidstore/blob/49f22cdb3efa78f9b784ffc63394a2945f6a3079/invenio_pidstore/models.py#L545>`_.
Migrační skrip voláme příkazem:

.. code-block:: console

    invenio nusl migrate pid