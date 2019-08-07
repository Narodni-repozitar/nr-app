import csv
import json
import os
import unicodedata

import click
from flask import cli
from invenio_db import db

from flask_taxonomies.models import Taxonomy, TaxonomyTerm
from invenio_nusl.scripts.university_taxonomies import f_rid_ic_dict
from invenio_nusl_theses.marshmallow.data.fields_refactor import create_aliases
from invenio_nusl_theses.marshmallow.data.aliases import ALIASES


@click.group()
def nusl():
    """Nusl commands."""


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
                university = universities.get_term(ic)
                term = university.create_term(slug=row["rid_f"].strip(),
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


@nusl.command('import_departments')
@cli.with_appcontext
def import_departments():
    counter = 0
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "departments.json")
    universities = Taxonomy.get("universities")

    with open(path, newline='') as jsonfile:
        org_units = json.load(jsonfile)
        org_units = [org_unit for org_unit in org_units if
                     org_unit[3] == "cze" and org_unit[1] is not None and org_unit[2] is not None]
        for unit in org_units:
            counter += 1
            university = unit[0].strip()
            faculty = unit[1].strip()
            department = unit[2].strip()

            university_tax = universities.descendants.filter(
                TaxonomyTerm.extra_data[("name", 0, "name")].astext == university).all()
            if len(university_tax) != 1:
                continue
            faculty_tax = university_tax[0].descendants.filter(
                TaxonomyTerm.extra_data[("name", 0, "name")].astext == faculty).all()
            if len(faculty_tax) != 1:
                continue

            slug = create_slug(department)
            term = universities.get_term(slug)
            if term is not None:
                continue
            term = faculty_tax[0].create_term(slug=slug,
                                              extra_data={
                                                  "title": {
                                                      "value": department,
                                                      "lang": "cze"
                                                  }
                                              }
                                              )
            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {university}, {faculty}, {department}")


def create_slug(department):
    l = len(department)
    slug = remove_diacritics(department).lower()
    slug_array = slug.split(" ")
    if l > 64:
        new_slug = ""
        old_slug = ""
        i = 0
        j = -1
        l = 0
        while l < 64:
            new_slug += f"{slug_array[i]}_"
            if j >= 0:
                old_slug += f"{slug_array[j]}_"
            i += 1
            j += 1
            l = len(new_slug)
        slug = old_slug
        if slug.endswith("_"):
            slug = slug[:-1]
    else:
        slug = "_".join(slug_array)
    return slug


def remove_diacritics(text):
    text = unicodedata.normalize('NFKD', text)
    output = ''
    for c in text:
        if not unicodedata.combining(c):
            output += c
    return output




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
            bterm = doctype.get_term(row["bterm"])
            if not bterm:
                bterm = doctype.create_term(slug=row["bterm"].strip(),
                                            extra_data={
                                                "name": [
                                                    {
                                                        "name": row["nazev_bterm"],
                                                        "lang": "cze"
                                                    }
                                                ]
                                            }
                                            )
                db.session.add(bterm)
                db.session.commit()
                print(f"{counter}. {bterm}")

            if not doctype.get_term(row["term"]):
                term = bterm.create_term(slug=row["term"].strip(),
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
            riv = doctype.get_term('RIV')
            if not riv:
                riv = doctype.create_term(
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
                db.session.add(riv)
                db.session.commit()
                print(f"/doctype/RIV")

            if not doctype.get_term(f'{row["base_code"]}'):
                base_code = riv.create_term(
                    slug=row["base_code"].strip(),
                    extra_data={
                        "name": [
                            {
                                "name": row["name"],
                                "lang": "cze"
                            }
                        ]
                    },
                )
                if row["sub_code"] == "":
                    base_code.extra_data["definition"] = row["definice"]

                db.session.add(base_code)
                db.session.commit()
                print(f"/doctype/RIV/{row['base_code']}")

            if row["sub_code"] != "":
                if not doctype.get_term(row['sub_code']):
                    term = base_code.create_term(
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
            ispartof2 = provider.get_term(row["isPartOf2"])
            if not ispartof2:
                ispartof2 = provider.create_term(
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
                db.session.add(ispartof2)
                db.session.commit()
                print(f"/provider/{row['isPartOf2']}")

            ispartof = provider.get_term(row["isPartOf"])
            if not ispartof:
                if row["isPartOf"] != "null":
                    ispartof = ispartof2.create_term(
                        slug=row["isPartOf"].strip(),
                        extra_data={
                            "name": [
                                {
                                    "name": row["name_isPartOf"],
                                    "lang": "cze"
                                }
                            ]
                        },
                    )
                    db.session.add(ispartof)
                    db.session.commit()

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}")

            if not provider.get_term(row["id"]):
                provider_details = _split_export(row["EXPORT"])
                if row["isPartOf"] != "null":
                    term = ispartof.create_term(
                        slug=row["id"].strip(),
                        extra_data=provider_details
                    )

                    print(f"/provider/{row['isPartOf2']}/{row['isPartOf']}/{row['id']}")
                else:
                    term = ispartof2.create_term(slug=row["id"].strip(),
                                                 extra_data={
                                                     **provider_details
                                                 }
                                                 )

                    print(f"/provider/{row['isPartOf2']}/{row['id']}")

                db.session.add(term)
                db.session.commit()


@nusl.command('import_studyfields')
@cli.with_appcontext
def import_studyfields():
    # ALIASES = create_aliases()
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
        }
                                               )
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
                                               "name": name,
                                               "aliases": ALIASES.get(name[0]["name"])
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
