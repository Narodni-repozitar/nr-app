import csv
import json
import os
import unicodedata

import click
import invenio_indexer.api
import invenio_indexer.cli
import pycountry
import requests
from flask import cli
from invenio_db import db
from langcodes import Language
from sqlalchemy.exc import IntegrityError

from flask_taxonomies.models import Taxonomy, TaxonomyTerm
from invenio_nusl.scripts.university_taxonomies import f_rid_ic_dict
from invenio_oarepo.current_api import current_api


@click.group()
def nusl():
    """Nusl commands."""


################################################################################################################
#                                           Index                                                              #
################################################################################################################


@nusl.command('reindex')
@cli.with_appcontext
@click.pass_context
def reindex(ctx):
    with current_api.app_context():
        ctx.invoke(invenio_indexer.cli.reindex, pid_type='dnusl')
        invenio_indexer.api.RecordIndexer(version_type=None).process_bulk_queue(
            es_bulk_kwargs={'raise_on_error': True})


################################################################################################################
#                                           Taxonomies                                                         #
################################################################################################################

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
            "title": [
                {
                    "value": "Univerzity",
                    "lang": "cze"
                },
                {
                    "value": "Universities",
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
            if universities.get_term(row["ic"].strip()) is None:
                university = universities.create_term(
                    slug=row["ic"].strip(),
                    extra_data={
                        "title": [
                            {
                                "value": row["nazev_cz"].strip(),
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

                db.session.add(university)
                db.session.commit()
                print(f"{counter}. {row['nazev_cz']}")

            university = universities.get_term(slug=row["ic"].strip())
            if universities.get_term(slug=f"{row['ic'].strip()}_no_faculty") is None:
                no_faculty = university.create_term(
                    slug=f"{row['ic'].strip()}_no_faculty",
                    extra_data={
                        "title": [
                            {
                                "value": "Bez fakulty",
                                "lang": "cze"
                            }
                        ]
                    }
                )
                db.session.add(no_faculty)
                db.session.commit()
                print(f"{counter}. {row['nazev_cz']} no_faculty")


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
            ic = faculties_dict.get(row["rid_f"])
            if ic is not None:
                ic = ic.strip()
            if ic is None:
                continue
            counter += 1
            if universities.get_term(row["rid_f"]) is None:
                university = universities.get_term(ic)
                term = university.create_term(slug=row["rid_f"].strip(),
                                              extra_data={
                                                  "title": [
                                                      {
                                                          "value": row["nazev_cz"],
                                                          "lang": "cze"
                                                      }
                                                  ],
                                                  "university_RID": row["rid"],
                                                  "faculty_RID": row["rid_f"],
                                                  "url": row["web"],
                                                  "aliases": row["aliases"]
                                              }
                                              )
                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {row['nazev_cz']}")

            faculty = universities.get_term(slug=row["rid_f"].strip())
            if universities.get_term(slug=f"{row['rid_f'].strip()}_no_department") is None:
                no_department = faculty.create_term(
                    slug=f"{row['rid_f'].strip()}_no_department",
                    extra_data={
                        "title": [
                            {
                                "value": "Bez katedry",
                                "lang": "cze"
                            }
                        ]
                    }
                )
                db.session.add(no_department)
                db.session.commit()
                print(f"{counter}. {row['nazev_cz']}_no_department")

            if universities.get_term(slug=f"{ic.strip()}_no_faculty_no_department") is None:
                faculty = universities.get_term(slug=f"{ic.strip()}_no_faculty")
                no_department = faculty.create_term(
                    slug=f"{ic.strip()}_no_faculty_no_department",
                    extra_data={
                        "title": [
                            {
                                "value": "Bez katedry",
                                "lang": "cze"
                            }
                        ]
                    }
                )
                db.session.add(no_department)
                db.session.commit()
                print(f"{counter}. {row['nazev_cz']}_no_department")


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
                TaxonomyTerm.extra_data[("title", 0, "value")].astext == university).all()
            if len(university_tax) != 1:
                continue
            faculty_tax = university_tax[0].descendants.filter(
                TaxonomyTerm.extra_data[("title", 0, "value")].astext == faculty).all()
            if len(faculty_tax) != 1:
                continue

            slug = create_slug(department)
            term = universities.get_term(slug)
            if term is not None:
                continue
            term = faculty_tax[0].create_term(slug=slug,
                                              extra_data={
                                                  "title": [
                                                      {
                                                          "value": department,
                                                          "lang": "cze"
                                                      }
                                                  ]
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
            "title": [
                {
                    "value": "Typ dokumentu",
                    "lang": "cze"
                },
                {
                    "value": "Type of document",
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
                                                "title": [
                                                    {
                                                        "value": row["nazev_bterm"],
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
                                             "title": [
                                                 {
                                                     "value": row["nazev_term"],
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
            "title": [
                {
                    "value": "Typ dokumentu",
                    "lang": "cze"
                },
                {
                    "title": "Type of document",
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
                        "title": [
                            {
                                "value": "Rejstřík informací o výsledcích",
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
                        "title": [
                            {
                                "value": row["name"],
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
                            "title": [
                                {
                                    "value": row["name"],
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
            "title": [
                {
                    "value": export_array[1],
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
            "title": [
                {
                    "value": "Poskytovatel záznamu",
                    "lang": "cze"
                },
                {
                    "value": "Provider of record",
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
                        "title": [
                            {
                                "value": row["name_isPartOf2"],
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
                            "title": [
                                {
                                    "value": row["name_isPartOf"],
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
    studyfields = Taxonomy.get("studyfields")
    fields_json = create_field_json()
    dicrepancy_fields = {}
    error_fields = {}
    counter = 0
    if studyfields.get_term("no_valid_studyfield") is None:
        not_valid = studyfields.create_term(
            slug="no_valid_studyfield",
            extra_data={
                "title": {
                    "value": "Neplatný obor",
                    "lang": "cze"
                }
            }
        )
        db.session.add(not_valid)
        db.session.commit()
    for k, v in fields_json.items():
        programme = studyfields.get_term(k)
        for key, value in v.items():
            counter += 1
            if k[1:] == key[:4]:
                try:
                    term = programme.create_term(
                        slug=key,
                        extra_data=value
                    )

                    db.session.add(term)
                    db.session.commit()
                    print(f"{counter}. {key} {value}")
                except IntegrityError:
                    if error_fields.get(k) is None:
                        error_fields[k] = {
                            key: value
                        }
                    else:
                        error_fields[k][key] = value
            else:
                if dicrepancy_fields.get(k) is None:
                    dicrepancy_fields[k] = {
                        key: value
                    }
                else:
                    dicrepancy_fields[k][key] = value

    counter = 0
    print("#####################        DISCREPANCY_FIELDS            ################################################")
    for k, v in dicrepancy_fields.items():
        programme = studyfields.get_term(k)
        if programme is None:
            continue
        for key, value in v.items():
            counter += 1
            try:
                term = programme.create_term(
                    slug=key,
                    extra_data=value
                )

                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {key} {value}")
            except IntegrityError:
                if error_fields.get(k) is None:
                    error_fields[k] = {
                        key: value
                    }
                else:
                    error_fields[k][key] = value

    with open("/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/error_fields.json", "w") as f:
        json.dump(error_fields, f)


def create_field_json():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "studijni_obory_edit.json")
    with open(path, "r") as file:
        data = json.load(file)
    fields = {}
    for row in data:
        language = row.get("Jazyk výuky")
        if language != "Česky":
            continue
        akvo = row.get("AKVO")
        studprog = row.get("STUDPROG")
        if akvo is None or studprog is None:
            continue
        if fields.get(studprog) is None:
            fields[studprog] = {
                akvo:
                    {
                        "title": [
                            {
                                "value": row.get("Název oboru"),
                                "lang": "cze"
                            }
                        ],
                        "grantor": [
                            {
                                "university": row.get("Název VŠ"),
                                "faculty": row.get("Součást vysoké školy")
                            }
                        ],
                        "type": "obor",
                        "degree_level": row.get("Typ programu"),
                        "form_of_study": row.get("Forma studia"),
                        "duration": row.get("Doba studia"),
                        "date_of_accreditation_validity": row.get("Datum platnosti akreditace"),
                        "reference_number": row.get("Číslo jednací"),
                        "aliases": row.get("aliases")

                    }
            }
        else:
            if fields[studprog].get(akvo) is None:
                fields[studprog][akvo] = {
                    "title": [
                        {
                            "value": row.get("Název oboru"),
                            "lang": "cze"
                        }
                    ],
                    "grantor": [
                        {
                            "university": row.get("Název VŠ"),
                            "faculty": row.get("Součást vysoké školy")
                        }
                    ],
                    "type": "obor",
                    "degree_level": row.get("Typ programu"),
                    "form_of_study": row.get("Forma studia"),
                    "duration": row.get("Doba studia"),
                    "date_of_accreditation_validity": row.get("Datum platnosti akreditace"),
                    "reference_number": row.get("Číslo jednací"),
                    "aliases": row.get("aliases")

                }
            else:
                if fields[studprog][akvo].get("title") is None:
                    fields[studprog][akvo]["tittle"] = [
                        {
                            "value": row.get("Název programu"),
                            "lang": "cze"
                        }
                    ]
                if fields[studprog][akvo].get("grantor") is not None:
                    added_grantor = {
                        "university": row.get("Název VŠ"),
                        "faculty": row.get("Součást vysoké školy")
                    }
                    same = False
                    for grantor in fields[studprog][akvo]["grantor"]:
                        if grantor == added_grantor:
                            same = True
                    if same == False:
                        fields[studprog][akvo]["grantor"].append(
                            added_grantor
                        )
                else:
                    fields[studprog][akvo]["grantor"] = [
                        {
                            "university": row.get("Název VŠ"),
                            "faculty": row.get("Součást vysoké školy")
                        }
                    ]
    return fields


@nusl.command('import_studyprogramme')
@cli.with_appcontext
def import_studyprogramme():
    studyfields = Taxonomy.get("studyfileds")
    if studyfields is None:
        studyfields = Taxonomy.create_taxonomy(code='studyfields', extra_data={
            "title": [
                {
                    "value": "Studijní obory",
                    "lang": "cze"
                },
                {
                    "value": "Study fields",
                    "lang": "eng"
                }
            ]
        })
        db.session.add(studyfields)
        db.session.commit()

        programme_json = create_programme_json()

        counter = 0
        for k, v in programme_json.items():
            counter += 1
            term = studyfields.create_term(
                slug=k,
                extra_data=v
            )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {k} {v}")


def create_programme_json():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "studijni_obory_edit.json")
    with open(path, "r") as file:
        data = json.load(file)
    programmes = {}
    for row in data:
        language = row.get("Jazyk výuky")
        if language != "Česky":
            continue
        studprog = row.get("STUDPROG")
        if studprog is None:
            continue
        if programmes.get(studprog) is None:
            programmes[studprog] = {
                "title": [
                    {
                        "value": row.get("Název programu"),
                        "lang": "cze"
                    }
                ],
                "grantor": [
                    {
                        "university": row.get("Název VŠ"),
                        "faculty": row.get("Součást vysoké školy")
                    }
                ],
                "type": "program",
                "degree_level": row.get("Typ programu"),
                "form_of_study": row.get("Forma studia"),
            }
            if row.get("Název oboru") is None:
                programmes[studprog].update(
                    {
                        "duration": row.get("Doba studia"),
                        "date_of_accreditation_validity": row.get("Datum platnosti akreditace"),
                        "reference_number": row.get("Číslo jednací")
                    }
                )
        else:
            if programmes[studprog].get("title") is None:
                programmes[studprog]["tittle"] = [
                    {
                        "value": row.get("Název programu"),
                        "lang": "cze"
                    }
                ]
            if programmes[studprog].get("grantor") is not None:
                added_grantor = {
                    "university": row.get("Název VŠ"),
                    "faculty": row.get("Součást vysoké školy")
                }
                same = False
                for grantor in programmes[studprog]["grantor"]:
                    if grantor == added_grantor:
                        same = True
                if same == False:
                    programmes[studprog]["grantor"].append(
                        added_grantor
                    )
            else:
                programmes[studprog]["grantor"] = [
                    {
                        "university": row.get("Název VŠ"),
                        "faculty": row.get("Součást vysoké školy")
                    }
                ]
    return programmes


@nusl.command('import_other_studyfields')
@cli.with_appcontext
def import_other_studyfields():
    studyfields = Taxonomy.get("studyfields")
    fields_json = create_other_json()
    fields_json = delete_none(fields_json)
    fields_json = delete_none(fields_json)
    fields_json = delete_none(fields_json)
    counter = 0

    programme = studyfields.create_term(
        slug="others"
    )
    for key, value in fields_json.items():
        counter += 1
        if studyfields.get_term(key) is None:
            term = programme.create_term(
                slug=key,
                extra_data=value
            )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {key} {value}")


def create_other_json():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "studijni_obory_edit.json")
    with open(path, "r") as file:
        data = json.load(file)
    fields = {}
    for row in data:
        language = row.get("Jazyk výuky")
        if language == "" or language is None:
            akvo = row.get("AKVO")
            if akvo is None:
                continue
            if fields.get(akvo) is None:
                fields[akvo] = {
                    "title": [
                        {
                            "value": row.get("Název oboru"),
                        }
                    ],
                    "grantor": [
                        {
                            "university": row.get("Název VŠ"),
                            "faculty": row.get("Součást vysoké školy")
                        }
                    ],
                    "type": "obor",
                    "degree_level": degree_level(akvo),
                    "form_of_study": row.get("Forma studia"),
                    "duration": row.get("Doba studia"),
                    "date_of_accreditation_validity": row.get("Datum platnosti akreditace"),
                    "reference_number": row.get("Číslo jednací"),
                    "aliases": row.get("aliases")

                }

    return fields


def delete_none(x):
    if isinstance(x, dict):
        return {k: delete_none(v) for k, v in x.items() if
                v is not None and len(v) != 0}
    elif isinstance(x, list) or isinstance(x, tuple):
        return [delete_none(v) for v in x if
                v is not None and len(v) != 0]
    return x


def degree_level(code):
    degree_dict = {
        "R": "Bakalářský",
        "T": "Magisterský",
        "V": "Doktorský"
    }
    return degree_dict.get(code[4])


@nusl.command('import_subjects')
@cli.with_appcontext
def import_subjects():
    subject = Taxonomy.get('subject')
    if not subject:
        subject = Taxonomy.create_taxonomy(code='subject', extra_data={
            "title": [
                {
                    "value": "Klíčová slova",
                    "lang": "cze"
                },
                {
                    "value": "Keywords",
                    "lang": "eng"
                }
            ]
        })
        db.session.add(subject)
        db.session.commit()

    taxonomies = {
        "PSH": {
            "title": [
                {
                    "value": "Polytematický strukturovaný heslář",
                    "lang": "cze"
                },
                {
                    "value": "Polythematic Structured Subject Heading System",
                    "lang": "eng"
                }
            ],
            "url": "https://psh.techlib.cz/skos/"
        },
        "CZMESH": {
            "title": [
                {
                    "value": "Tezaurus Medical Subject Headings",
                    "lang": "cze"
                },
                {
                    "value": "Medical Subject Headings",
                    "lang": "eng"
                }
            ],
            "url": "https://www.medvik.cz/bmc/subject.do"
        },
        "MEDNAS": {
            "title": [
                {
                    "value": "Autoritní soubor oborů – Národní lékařská knihovna, Praha (MEDNAS)",
                    "lang": "cze"
                },
            ],
            "url": "https://www.medvik.cz/bmc/subject.do"
        },
        "CZENAS": {
            "title": [
                {
                    "value": "Soubor vĕcných autorit Národní knihovny ČR",
                    "lang": "cze"
                },
                {
                    "value": "CZENAS thesaurus: a list of subject terms used in the National Library of the Czech Republic",
                    "lang": "eng"
                }
            ],
            "url": ""
        },
        "keyword": {
            "title": [
                {
                    "value": "Klíčová slova",
                    "lang": "cze"
                },
                {
                    "value": "Keywords",
                    "lang": "eng"
                }
            ],
        }
    }

    counter = 0
    for k, v in taxonomies.items():
        counter += 1
        if subject.get_term(k) is None:
            term = subject.create_term(
                slug=k,
                extra_data=v
            )

            db.session.add(term)
            db.session.commit()
            print(f"{counter}. {k} {v}")


@nusl.command('import_languages')
@cli.with_appcontext
def import_languages():
    languages = Taxonomy.get("languages")
    if languages is None:
        languages = Taxonomy.create_taxonomy(code='languages', extra_data={
            "title": [
                {
                    "value": "Jazyky",
                    "lang": "cze"
                },
                {
                    "value": "Languages",
                    "lang": "eng"
                }
            ]
        })
        db.session.add(languages)
        db.session.commit()

    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, "data", "languages.csv")
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        counter = 0
        for row in reader:
            counter += 1
            lang = language_code(row[0])
            if languages.get_term(lang) is None:
                term = languages.create_term(slug=lang, extra_data={
                    "title": [
                        {
                            "value": Language.get(lang).language_name("cze"),
                            "lang": "cze"
                        },
                        {
                            "value": Language.get(lang).language_name("eng"),
                            "lang": "eng"
                        }
                    ]
                })
                db.session.add(term)
                db.session.commit()
                print(f"{counter}. {row[0]}")


def language_code(language):
    alpha3 = pycountry.languages.get(alpha_3=language)
    bib = pycountry.languages.get(bibliographic=language)
    if bib is not None:
        lang = bib.bibliographic
    elif alpha3 is not None:
        lang = alpha3.alpha_3
    else:
        raise ValueError("The language  is not known.")
    return lang


@nusl.command('import_psh')
@cli.with_appcontext
def get_psh():
    top_terms = get_top_terms()['@graph']
    subject = Taxonomy.get('subject')
    psh_term = subject.get_term('PSH')
    for term in top_terms:
        save_all_terms_recursively(subject, term, psh_term)
    print("All terms were saved")


def save_all_terms_recursively(taxonomy, term, parent_term):
    slug = term.pop('pshid')
    narrower = term['narrower']
    if len(term['altLabel']) > 0:
        print("SLUG", slug)
        alt_title = make_multilang_list(term['altLabel'])
        del term['altLabel']
        if alt_title is not None:
            term['altTitle'] = alt_title
            print(f"{slug} ALT_title: ", alt_title)
    title = make_multilang_title(term['prefLabel'])
    del term['prefLabel']
    term['title'] = title
    parent_term = save_term(taxonomy, parent_term, slug, extra_data=term)
    for id_ in narrower:
        term = get_term(id_).get("@graph")
        if term is None:
            continue
        save_all_terms_recursively(taxonomy, term, parent_term)
    print(f"All children of term {slug} were created")


def get_top_terms():
    response = requests.get("https://psh.techlib.cz/api/concepts/top")
    return json.loads(response.text)


def get_term(psh_id):
    response = requests.get(f"https://psh.techlib.cz/api/concepts/{psh_id}")
    return json.loads(response.text)


def make_multilang_list(old_dict: dict):
    multi_langlist = []
    num_items = []
    for value in old_dict.values():
        num_items.append(len(value))
    for i in range(max(num_items)):
        multi_langlist.append([])
        for j in num_items:
            if j > 0:
                multi_langlist[i].append(
                    {
                        "value": None,
                        "lang": None
                    }
                )

    return filter_none((fill_multilang_list(old_dict, multi_langlist)))


def make_multilang_title(old_dict: dict):
    multilang_list = []
    for k, v in old_dict.items():
        new_lang = language_three_place(k)
        multilang_list.append(
            {
                "value": v,
                "lang": new_lang
            }
        )
    return multilang_list


def language_three_place(old_lang):
    lang_pycountry = pycountry.languages.get(alpha_2=old_lang)
    if lang_pycountry is None:
        return None
    new_lang = getattr(lang_pycountry, "bibliographic", None)
    if new_lang is None:
        new_lang = getattr(lang_pycountry, "alpha_3", None)
    if new_lang is None:
        return None
    return new_lang


def fill_multilang_list(old_dict, multilang_list):
    m = 0
    for i, (k, v) in enumerate(old_dict.items()):
        j = 0
        if len(v) == 0:
            m -= 1
        for value in v:
            multilang_list[j][m]["value"] = value
            multilang_list[j][m]["lang"] = language_three_place(k)
            j += 1
        m += 1
    return multilang_list


def filter_none(old_list):
    new_list = []
    for item in old_list:
        item_list = []
        for dict in item:
            new_dict = {k: v for k, v in dict.items() if v is not None}
            if len(new_dict) > 0:
                item_list.append(new_dict)
        if len(item_list) > 0:
            new_list.append(item_list)
    return new_list


def save_term(taxonomy, parent_term, slug, extra_data: dict = None):
    term = taxonomy.get_term(slug)
    if term is None:
        term = parent_term.create_term(slug=slug, extra_data=extra_data)
        db.session.add(term)
        db.session.commit()
        print(slug)
    return term
