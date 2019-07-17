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


if __name__ == "__main__":
    pass
