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
            "name": [
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
            name = [
                {
                    "name": row["NAZEV"],
                    "lang": "cze"
                }
            ]
            if row["ANAZEV"] != "":
                name.append(
                    {
                        "name": row["ANAZEV"],
                        "lang": "eng"
                    }
                )
            counter += 1
            term = studyfields.create_term(slug=row["KOD"],
                                           extra_data={
                                               "name": name
                                           }
                                           )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_studyprogramme')
@cli.with_appcontext
def import_studyprogramme():
    studyprogramme = Taxonomy.create_taxonomy(code='studyprogramme', extra_data={
        "name": [
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
            name = [
                {
                    "name": row["NAZEV"],
                    "lang": "cze"
                }
            ]
            if row["ANAZEV"] != "":
                name.append(
                    {
                        "name": row["ANAZEV"],
                        "lang": "eng"
                    }
                )
            counter += 1
            term = studyprogramme.create_term(
                slug=row["KOD"],
                extra_data={
                    "name": name
                }
            )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {term}")


@nusl.command('import_universities')
@cli.with_appcontext
def import_universities():
    def convert_dates(date):
        if date != "":
            array = date.split(".")
            array = [f"0{X}" if len(X) == 1 else X for X in array]
            array = array[::-1]
            return "-".join(array)
        return date

    universities = Taxonomy.get('universities')
    if not universities:
        universities = Taxonomy.create_taxonomy(code='universities', extra_data={
            "name": [
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
                    "name": [
                        {
                            "name": row["nazev_cz"].strip(),
                            "lang": "cze"
                        }
                    ],
                    "type": row["typ_VS"].strip(),
                    "form": row["text_forma_VS"].strip(),
                    "region": row["kraj"].strip(),
                    "RID": row["rid"].strip(),
                    "address": row["sidlo"].strip(),
                    "IČO": row["ic"].strip(),
                    "data_box": row["datova_schranka"].strip(),
                    "url": row["web"].strip(),
                    "deputy": row["statutarni_zastupce"].strip(),
                    "term_of_office_from": convert_dates(row["funkcni_obdobi_od"].strip()),
                    "term_of_office_until": convert_dates(row["funkcni_obdobi_do"].strip())
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
                                                    "name": [
                                                        {
                                                            "name": row["nazev_cz"],
                                                            "lang": "cze"
                                                        }
                                                    ],
                                                    "university_RID": row["rid"],
                                                    "faculty_RID": row["rid_f"],
                                                    "url": row["web"],
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
            "name": [
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
                                               "name": [
                                                   {
                                                       "name": row["nazev_bterm"],
                                                       "lang": "cze"
                                                   }
                                               ]
                                           }
                                           )
                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {term}")

            if not doctype.get_term(row["term"]):
                term = doctype.create_term(slug=row["term"].strip(),

                                           parent_path=row["bterm"],
                                           extra_data={
                                               "name": [
                                                   {
                                                       "name": row["nazev_term"],
                                                       "lang": "cze"
                                                   }
                                               ]
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
            "name": [
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
                        "name": [
                            {
                                "name": "Rejstřík informací o výsledcích",
                                "lang": "cze"
                            }
                        ]
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
                            "name": [
                                {
                                    "name": row["name"],
                                    "lang": "cze"
                                }
                            ],
                            "definition": row["definice"]
                        },
                        parent_path='RIV',
                    )
                else:
                    term = doctype.create_term(
                        slug=row["base_code"].strip(),
                        extra_data={
                            "name": [
                                {
                                    "name": row["name"],
                                    "lang": "cze"
                                }
                            ]
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
                            "name": [
                                {
                                    "name": row["name"],
                                    "lang": "cze"
                                }
                            ],
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
            "name": [
                {
                    "name": export_array[1],
                    "lang": "cze"
                }
            ],
            "address": export_array[2],
            "url": export_array[3],
            "lib_url": export_array[4]
        }
        return export_dict

    if Taxonomy.get('provider') is None:
        provider = Taxonomy.create_taxonomy(code='provider', extra_data={
            "name": [
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
                        "name": [
                            {
                                "name": row["name_isPartOf2"],
                                "lang": "cze"
                            }
                        ]
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
                            "name": [
                                {
                                    "name": row["name_isPartOf"],
                                    "lang": "cze"
                                }
                            ]
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
                        extra_data=provider_details
                    )

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}/{row['id']}")
                else:
                    term = provider.create_term(slug=row["id"].strip(),
                                                parent_path=row["isPartOf2"],
                                                extra_data={
                                                    **provider_details
                                                }
                                                )

                    print(f"/provider/{row['isPartOf2']}/{row['id']}")

                db.session.add(term)
                db.session.commit()
