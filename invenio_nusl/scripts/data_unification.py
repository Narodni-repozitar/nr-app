import csv
import json
import os
from functools import lru_cache

from invenio_nusl_theses.marshmallow.data.aliases import ALIASES


def create_field_code_jsons():
    code_field_dict = {}
    field_code_dict = {}
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/field.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            code_field_dict[row["KOD"]] = row["NAZEV"]
            field_code_dict[row["NAZEV"]] = row["KOD"]

    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/code_field.json', "w") as f:
        json.dump(code_field_dict, f)

    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/field_code.json', "w") as f:
        json.dump(field_code_dict, f)


def create_programme_code_jsons():
    code_programme_dict = {}
    programme_code_dict = {}
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/programme.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            code_programme_dict[row["KOD"]] = row["NAZEV"]
            programme_code_dict[row["NAZEV"]] = row["KOD"]

    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/code_programme.json', "w") as f:
        json.dump(code_programme_dict, f)

    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/programme_code.json', "w") as f:
        json.dump(programme_code_dict, f)


@lru_cache()
def create_stud_obory_json():
    study_array = []
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            study_dict = {}
            for k in reader.fieldnames:
                study_dict[k] = row[k]
            study_array.append(study_dict)

    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory.json', "w") as f:
        json.dump(study_array, f)


def add_data(data_dict):
    for row in data_dict:
        if row['Jazyk výuky'] == "Česky":
            row = check_field(row)
            row = check_programme(row)
    return data_dict


@lru_cache()
def stud_obory_json():
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory.json') as f:
        data_dict = json.load(f)
    return data_dict


@lru_cache()
def load_code_field():
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/code_field.json') as f:
        code_field = json.load(f)
    return code_field


@lru_cache()
def load_field_code():
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/field_code.json') as f:
        field_code = json.load(f)
    return field_code


@lru_cache()
def load_code_programme():
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/code_programme.json') as f:
        code_programme = json.load(f)
    return code_programme


@lru_cache()
def load_programme_code():
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/programme_code.json') as f:
        programme_code = json.load(f)
    return programme_code


def create_akvo_aliases_json():
    field_code = load_field_code()
    code_alias = {field_code.get(k): v for k, v in ALIASES.items()}
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/code_aliases.json', "w") as f:
        json.dump(code_alias, f)


@lru_cache()
def load_akvo_aliases_json():
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/code_aliases.json') as f:
        code_alias = json.load(f)
    return code_alias


def check_field(row):
    field_code = load_field_code()
    code_field = load_code_field()
    if row["Název oboru"] == "" or row["AKVO"] == "" and not (row["Název oboru"] == "" and row["AKVO"] == ""):
        if row["Název oboru"] == "":
            name = code_field.get(row["AKVO"])
            if name is not None:
                row["Název oboru"] = name

        if row["AKVO"] == "":
            code = field_code.get(row["Název oboru"])
            if code is not None:
                row["AKVO"] = code

    return row


def check_programme(row):
    programme_code = load_programme_code()
    code_programme = load_code_programme()
    if row["Název programu"] == "" or row["STUDPROG"] == "" and not (
            row["Název programu"] == "" and row["STUDPROG"] == ""):
        if row["Název programu"] == "":
            name = code_programme.get(row["STUDPROG"])
            if name is not None:
                row["Název programu"] = name

        if row["STUDPROG"] == "":
            code = programme_code.get(row["Název programu"])
            if code is not None:
                row["STUDPROG"] = code

    return row


def add_aliases(data):
    for row in data:
        aliases = load_akvo_aliases_json()
        alias = aliases.get(row.get("AKVO"))
        row["aliases"] = alias
    return data


def add_missing_fields():
    missing_codes = field_difference()
    code_dict = load_code_field()
    missing_fields = [{"AKVO": code, "Název oboru": code_dict[code]} for code in missing_codes]
    return missing_fields


def field_difference():
    stud_obory = stud_obory_json()
    code_field = load_code_field()
    stud_obory_set = {row["AKVO"] for row in stud_obory}
    code_set = {k for k in code_field.keys()}
    return code_set - stud_obory_set


def add_missing_programmes():
    missing_codes = programme_difference()
    code_dict = load_code_programme()
    missing_fields = [{"STUDPROG": code, "Název programu": code_dict[code]} for code in missing_codes]
    return missing_fields


def programme_difference():
    stud_obory = stud_obory_json()
    code_programme = load_code_programme()
    # stud_obory_set = {row["STUDPROG"] for row in stud_obory}
    stud_obory_set = set()
    for row in stud_obory:
        studprog = row.get("STUDPROG")
        if studprog is not None:
            stud_obory_set.add(studprog)
    code_set = {k for k in code_programme.keys()}
    return code_set - stud_obory_set


def check_for_array(data):
    i = 0
    for row in data:
        i += 1
        if isinstance(row, list):
            print(row)


def create_csv():
    fieldnames = extract_fieldnames('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory.csv')
    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory_edit.json') as f:
        data_dict = json.load(f)

    with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory_edit.csv', "w",
              newline='') as csvfile:
        fieldnames.append("aliases")
        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames)

        writer.writeheader()
        for row in data_dict:
            writer.writerow(row)


def extract_fieldnames(path):
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        fieldnames = reader.fieldnames
        return fieldnames


def run():
    if not os.path.isfile('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory_edit.json'):
        data_dict = stud_obory_json()
        data_dict = add_data(data_dict)
        data_dict += add_missing_fields()
        data_dict += add_missing_programmes()
        data_dict = add_aliases(data_dict)

        with open('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory_edit.json', "w") as f:
            json.dump(data_dict, f)

    if not os.path.isfile('/home/semtex/Projekty/nusl/invenio-nusl/invenio_nusl/data/studijni_obory_edit.csv'):
        create_csv()


if __name__ == "__main__":
    run()
