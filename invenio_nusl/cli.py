import csv
import os

import click
from flask import cli
from invenio_db import db

from flask_taxonomies.models import Taxonomy
from invenio_nusl.scripts.university_taxonomies import f_rid_ic_dict


@click.group()
def nusl():
    """Nusl commands."""


@nusl.command('import_studyfields')
@cli.with_appcontext
def import_studyfields():
    studyfields = Taxonomy.get('studyfields')
    if not studyfields:
        studyfields = Taxonomy.create_taxonomy(code='studyfields', extra_data={
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
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "field.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            term = studyfields.create_term(slug=row["KOD"],
                                           extra_data={"code": row["KOD"],
                                                       "title": {
                                                           "name": row["NAZEV"],
                                                       }
                                                       })

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_studyprogramme')
@cli.with_appcontext
def import_studyprogramme():
    studyprogramme = Taxonomy.create_taxonomy(code='studyprogramme', extra_data={
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
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "programme.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            term = studyprogramme.create_term(
                slug=row["KOD"],
                extra_data={"code": row["KOD"],
                            "title": {
                                "name": [
                                    {
                                        "name": row["NAZEV"],
                                        "lang": "cze"
                                    },
                                    {"name": row["ANAZEV"], "lang": "eng"} if row["ANAZEV"] != "" else {}
                                ]
                            }
                            })

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_universities')
@cli.with_appcontext
def import_universities():
    universities = Taxonomy.create_taxonomy(code='universities', extra_data={
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
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "universities.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            term = universities.create_term(
                slug=row["ic"].strip(),
                extra_data={
                    "title": {
                        "name": row["nazev_cz"].strip(),
                    },
                    "Název": row["nazev_cz"].strip(),
                    "Typ VŠ": row["typ_VS"].strip(),
                    "Forma VŠ": row["text_forma_VS"].strip(),
                    "Kraj": row["kraj"].strip(),
                    "Resortní identifikátor (RID)": row["rid"].strip(),
                    "Sídlo": row["sidlo"].strip(),
                    "IČO": row["ic"].strip(),
                    "Datová schránka": row["datova_schranka"].strip(),
                    "Web": row["web"].strip(),
                    "Statutární zástupce": row["statutarni_zastupce"].strip(),
                    "Funkční období od": row["funkcni_obdobi_od"].strip(),
                    "Funkční období do": row["funkcni_obdobi_do"].strip()
                }
            )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_faculties')
@cli.with_appcontext
def import_faculties():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "faculties.csv")
    faculties_dict = f_rid_ic_dict()
    universities = Taxonomy.get("universities")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            ic = faculties_dict[row["rid_f"]].strip()
            counter += 1
            if not universities.get_term(row["rid_f"]):
                term = universities.create_term(slug=row["rid_f"].strip(),

                                                parent_path=ic,
                                                extra_data={
                                                    "title": {
                                                        "name": row["nazev_cz"],
                                                    },
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
    doctype = Taxonomy.get('doctype')
    if doctype is None:
        doctype = Taxonomy.create_taxonomy(code='doctype', extra_data={
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
            if not doctype.get_term(row["bterm"]):
                term = doctype.create_term(slug=row["bterm"].strip(),
                                           extra_data={
                                               "title": {
                                                   "name": row["nazev_bterm"],
                                               },
                                               "Kód": row["bterm"],
                                           }
                                           )
                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {term}")

            if not doctype.get_term(row["term"]):
                term = doctype.create_term(slug=row["term"].strip(),

                                           parent_path=row["bterm"],
                                           extra_data={
                                               "title": {
                                                   "name": row["nazev_term"],
                                               },
                                               "Kód": row["term"],
                                           }
                                           )
                db.session.add(term)
                db.session.commit()

                print(f"{counter}. {term}")


@nusl.command('import_riv')
@cli.with_appcontext
def import_riv():
    doctype = Taxonomy.get('doctype')
    if doctype is None:
        doctype = Taxonomy.create_taxonomy(code='doctype', extra_data={
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
            if not doctype.get_term('RIV'):
                term = doctype.create_term(
                    slug="RIV",
                    extra_data={
                        "title": {
                            "name": "RIV",
                        }
                    },
                )
                db.session.add(term)
                db.session.commit()
                print(f"/doctype/RIV")

            if not doctype.get_term(f'{row["base_code"]}'):
                if row["sub_code"] == "":
                    term = doctype.create_term(
                        slug=row["base_code"].strip(),
                        extra_data={
                            "title": {
                                "name": row["name"]
                            },
                            "definition": row["definice"]
                        },
                        parent_path='RIV',
                    )
                else:
                    term = doctype.create_term(
                        slug=row["base_code"].strip(),
                        extra_data={
                            "title": {
                                "name": row["base_code"]
                            }
                        },
                        parent_path='RIV',
                    )
                db.session.add(term)
                db.session.commit()
                print(f"/doctype/RIV/{row['base_code']}")

            if row["sub_code"] != "":
                if not doctype.get_term(row['sub_code']):
                    term = doctype.create_term(
                        slug=row["sub_code"].strip(),

                        extra_data={
                            "title": {
                                "name": row["name"],
                            },
                            "definition": row["definice"]
                        },
                        parent_path=f"RIV/{row['base_code']}"
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

    if Taxonomy.get('provider') is None:
        provider = Taxonomy.create_taxonomy(code='provider', extra_data={
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

    else:
        provider = Taxonomy.get('provider')

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "Institutions_ids.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            print(counter, "#######################################################")
            if not provider.get_term(row["isPartOf2"]):
                term = provider.create_term(
                    slug=row["isPartOf2"].strip(),
                    extra_data={
                        "title": {
                            "name": row["name_isPartOf2"],
                        }
                    },
                )
                db.session.add(term)
                db.session.commit()
                print(f"/provider/{row['isPartOf2']}")

            if not provider.get_term(row["isPartOf"]):
                if row["isPartOf"] != "null":
                    term = provider.create_term(
                        slug=row["isPartOf"].strip(),
                        extra_data={
                            "title": {
                                "name": row["name_isPartOf"],
                            }
                        },
                        parent_path=row["isPartOf2"],
                    )
                    db.session.add(term)
                    db.session.commit()

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}")

            if not provider.get_term(row["id"]):
                provider_details = _split_export(row["EXPORT"])
                if row["isPartOf"] != "null":
                    term = provider.create_term(
                        slug=row["id"].strip(),

                        parent_path=f'{row["isPartOf2"]}/{row["isPartOf"]}',
                        extra_data=provider_details  # TODO: nemá title?
                    )

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}/{row['id']}")
                else:
                    term = provider.create_term(slug=row["id"].strip(),
                                                parent_path=row["isPartOf2"],
                                                extra_data={
                                                    **provider_details,
                                                    "title": {
                                                        "name": provider_details["name"]
                                                    },
                                                }
                                                )

                    print(f"/provider/{row['isPartOf2']}/{row['id']}")

                db.session.add(term)
                db.session.commit()
