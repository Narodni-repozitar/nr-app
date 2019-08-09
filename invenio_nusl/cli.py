import csv
import json
import os
import unicodedata

import click
from flask import cli
from invenio_db import db
from sqlalchemy.exc import IntegrityError

from flask_taxonomies.models import Taxonomy, TaxonomyTerm
from invenio_nusl.scripts.data_unification import add_aliases
from invenio_nusl.scripts.university_taxonomies import f_rid_ic_dict


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
            term = universities.create_term(
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
                                                  "title": [
                                                      {
                                                          "value": row["nazev_cz"],
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
            row["aliases"] = add_aliases(row)
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
