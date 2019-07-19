import click
from flask import cli
from invenio_db import db

from flask_taxonomies.managers import TaxonomyManager
from flask_taxonomies.models import Taxonomy
from invenio_nusl.scripts.university_taxonomies import f_rid_ic_dict

import csv
import os
import json


@click.group()
def nusl():
    """Nusl commands."""


@nusl.command('import_studyfields')
@cli.with_appcontext
def import_studyfields():
    studyfields = Taxonomy(code='studyfields', extra_data={
        "title": [
            {
                "name": "studijní obory",
                "lang": "cze"
            },
            {
                "name": "study fields",
                "lang": "eng"
            }
        ]
    })
    db.session.add(studyfields)
    db.session.commit()
    manager = TaxonomyManager()
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "field.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            term = manager.create(row["KOD"],
                                  title={
                                      "name": row["NAZEV"],
                                  },
                                  path='/studyfields/',
                                  extra_data={"code": row["KOD"]})

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_studyprogramme')
@cli.with_appcontext
def import_studyprogramme():
    studyprogramme = Taxonomy(code='studyprogramme', extra_data={
        "title": [
            {
                "name": "studijní programy",
                "lang": "cze"
            },
            {
                "name": "study programmes",
                "lang": "eng"
            }
        ]
    })
    db.session.add(studyprogramme)
    db.session.commit()
    manager = TaxonomyManager()
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "programme.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            term = manager.create(row["KOD"],
                                  title={
                                      "name": [
                                          {
                                              "name": row["NAZEV"],
                                              "lang": "cze"
                                          },
                                          {"name": row["ANAZEV"], "lang": "eng"} if row["ANAZEV"] != "" else {}
                                      ]
                                  },
                                  path='/studyprogramme/',
                                  extra_data={"code": row["KOD"]})

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_universities')
@cli.with_appcontext
def import_universities():
    universities = Taxonomy(code='universities', extra_data={
        "title": [
            {
                "name": "Univerzity",
                "lang": "cze"
            },
            {
                "name": "Universities",
                "lang": "eng"
            }
        ]
    })
    db.session.add(universities)
    db.session.commit()
    manager = TaxonomyManager()
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "universities.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            term = manager.create(row["ic"].strip(),
                                  title={
                                      "name": row["nazev_cz"],
                                  },
                                  path='/universities/',
                                  extra_data={
                                      "Název": row["nazev_cz"],
                                      "Typ VŠ": row["typ_VS"],
                                      "Forma VŠ": row["text_forma_VS"],
                                      "Kraj": row["kraj"],
                                      "Resortní identifikátor (RID)": row["rid"],
                                      "Sídlo": row["sidlo"],
                                      "IČO": row["ic"],
                                      "Datová schránka": row["datova_schranka"],
                                      "Web": row["web"],
                                      "Statutární zástupce": row["statutarni_zastupce"],
                                      "Funkční období od": row["funkcni_obdobi_od"],
                                      "Funkční období do": row["funkcni_obdobi_do"]
                                  }
                                  )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_faculties')
@cli.with_appcontext
def import_faculties():
    manager = TaxonomyManager()
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "faculties.csv")
    faculties_dict = f_rid_ic_dict()

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            ic = faculties_dict[row["rid_f"]].strip()
            counter += 1
            try:
                manager.get_from_path(f'/universities/{ic}/{row["rid_f"]}')
                print(counter)
            except AttributeError:
                term = manager.create(row["rid_f"].strip(),
                                      title={
                                          "name": row["nazev_cz"],
                                      },
                                      path=f'/universities/{ic}',
                                      extra_data={
                                          "Název": row["nazev_cz"],
                                          "Resortní identifikátor univerzity(RID)": row["rid"],
                                          "Resortní identifikátor fakulty(RID)": row["rid_f"],
                                          "Web": row["web"],
                                      }
                                      )

                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {term}")


@nusl.command('import_doctype')
@cli.with_appcontext
def import_doctype():
    manager = TaxonomyManager()
    if manager.get_taxonomy('doctype') is None:
        doctype = Taxonomy(code='doctype', extra_data={
            "title": [
                {
                    "name": "Typ dokumentu",
                    "lang": "cze"
                },
                {
                    "name": "Type of document",
                    "lang": "eng"
                }
            ]
        })
        db.session.add(doctype)
        db.session.commit()

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "document_typology_NUSL.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            try:
                manager.get_from_path(f'/doctype/{row["bterm"]}')
                print(counter)
            except AttributeError:
                term = manager.create(row["bterm"].strip(),
                                      title={
                                          "name": row["nazev_bterm"],
                                      },
                                      path=f'/doctype/',
                                      extra_data={
                                          "Kód": row["bterm"],
                                      }
                                      )
                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {term}")

            try:
                manager.get_from_path(f'/doctype/{row["bterm"]}/{row["term"]}')
            except AttributeError:
                term = manager.create(row["term"].strip(),
                                      title={
                                          "name": row["nazev_term"],
                                      },
                                      path=f'/doctype/{row["bterm"]}',
                                      extra_data={
                                          "Kód": row["term"],
                                      }
                                      )
                db.session.add(term)
                db.session.commit()

                print(f"{counter}. {term}")


@nusl.command('import_riv')
@cli.with_appcontext
def import_riv():
    manager = TaxonomyManager()
    if manager.get_taxonomy('doctype') is None:
        doctype = Taxonomy(code='doctype', extra_data={
            "title": [
                {
                    "name": "Typ dokumentu",
                    "lang": "cze"
                },
                {
                    "name": "Type of document",
                    "lang": "eng"
                }
            ]
        })
        db.session.add(doctype)
        db.session.commit()

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "document_typology_RIV.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            print(f"{counter}.", "#######################################################")
            try:
                manager.get_from_path(f'/doctype/RIV')
            except AttributeError:
                term = manager.create("RIV",
                                      title={
                                          "name": "RIV",
                                      },
                                      path=f'/doctype/',
                                      )
                db.session.add(term)
                db.session.commit()
                print(f"/doctype/RIV")

            try:
                manager.get_from_path(f'/doctype/RIV/{row["base_code"]}')
            except AttributeError:
                if row["sub_code"] == "":
                    term = manager.create(row["base_code"].strip(),
                                          title={
                                              "name": row["name"]
                                          },
                                          extra_data={
                                              "definition": row["definice"]
                                          },
                                          path=f'/doctype/RIV',
                                          )
                else:
                    term = manager.create(row["base_code"].strip(),
                                          title={
                                              "name": row["base_code"]
                                          },
                                          path=f'/doctype/RIV',
                                          )
                db.session.add(term)
                db.session.commit()

                print(f"/doctype/RIV/{row['base_code']}")

            if row["sub_code"] != "":
                try:
                    manager.get_from_path(f"/doctype/RIV/{row['base_code']}/{row['sub_code']}")
                except AttributeError:
                    term = manager.create(row["sub_code"].strip(),
                                          title={
                                              "name": row["name"],
                                          },
                                          extra_data={
                                              "definition": row["definice"]
                                          },
                                          path=f"/doctype/RIV/{row['base_code']}"
                                          )

                    print(f"/doctype/RIV/{row['base_code']}/{row['sub_code']}")

                    db.session.add(term)
                    db.session.commit()


@nusl.command('import_providers')
@cli.with_appcontext
def import_providers():
    def _split_export(export: str):
        export = export.replace("---", "|||")
        export_array = export.split("|||")
        export_dict = {
            "id": export_array[0],
            "name": export_array[1],
            "address": export_array[2],
            "url": export_array[3],
            "lib_url": export_array[4]
        }
        return export_dict

    manager = TaxonomyManager()
    if manager.get_taxonomy('provider') is None:
        provider = Taxonomy(code='provider', extra_data={
            "title": [
                {
                    "name": "Poskytovatel záznamu",
                    "lang": "cze"
                },
                {
                    "name": "Provider of record",
                    "lang": "eng"
                }
            ]
        })
        db.session.add(provider)
        db.session.commit()

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "Institutions_ids.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            print(counter, "#######################################################")
            try:
                manager.get_from_path(f'/provider/{row["isPartOf2"]}')
            except AttributeError:
                term = manager.create(row["isPartOf2"].strip(),
                                      title={
                                          "name": row["name_isPartOf2"],
                                      },
                                      path=f'/provider/',
                                      )
                db.session.add(term)
                db.session.commit()
                print(f"/provider/{row['isPartOf2']}")

            try:
                manager.get_from_path(f'/provider/{row["isPartOf2"]}/{row["isPartOf"]}')
            except AttributeError:
                if row["isPartOf"] != "null":
                    term = manager.create(row["isPartOf"].strip(),
                                          title={
                                              "name": row["name_isPartOf"],
                                          },
                                          path=f'/provider/{row["isPartOf2"]}/',
                                          )
                    db.session.add(term)
                    db.session.commit()

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}")

            try:
                manager.get_from_path(f'/provider/{row["isPartOf2"]}/{row["isPartOf"]}/{row["id"]}')
            except AttributeError:
                if row["isPartOf"] != "null":
                    term = manager.create(row["id"].strip(),
                                          title={
                                              "name": _split_export(row["EXPORT"])["name"],
                                          },
                                          path=f'/provider/{row["isPartOf2"]}/{row["isPartOf"]}',
                                          extra_data=_split_export(row["EXPORT"])
                                          )

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}/{row['id']}")
                else:
                    term = manager.create(row["id"].strip(),
                                          title={
                                              "name": _split_export(row["EXPORT"])["name"],
                                          },
                                          path=f'/provider/{row["isPartOf2"]}/',
                                          extra_data=_split_export(row["EXPORT"])
                                          )

                    print(f"/provider/{row['isPartOf2']}/{row['id']}")

                db.session.add(term)
                db.session.commit()


if __name__ == "__main__":
    pass
