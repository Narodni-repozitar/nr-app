import csv
import os
from functools import lru_cache


@lru_cache()
def university_taxonomy_tree():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(path)
    path = os.path.join(path, "data", "faculties.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        tree = dict()
        for row in reader:
            counter += 1
            tree[row["rid_f"]] = row["rid"]

    return tree


@lru_cache()
def rid_ico_dict():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.dirname(path)
    path = os.path.join(path, "data", "universities.csv")

    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        counter = 0
        tree = dict()

        for row in reader:
            tree[row["rid"]] = row["ic"]

    return tree


def f_rid_ic_dict():
    rid_taxonomy_tree = university_taxonomy_tree()
    ico_dict = rid_ico_dict()
    f_rid_ic_dict = dict()

    for k, v in rid_taxonomy_tree.items():
        try:
            f_rid_ic_dict[k] = ico_dict[v]
        except KeyError as e:
            pass

    return f_rid_ic_dict
