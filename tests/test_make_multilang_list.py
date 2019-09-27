from invenio_nusl.cli import make_multilang_list


def test_multilang_list_1():
    source = {
        "cs": [
            "antropolingvistika",
            "antropologická lingvistika"
        ],
        "en": [
            "anthropological linguistics"
        ]
    }
    expected_result = [
        [
            {
                "value": "antropolingvistika",
                "lang": "cze"
            },
            {
                "value": "anthropological linguistics",
                "lang": "eng"
            }
        ],
        [
            {
                "value": "antropologická lingvistika",
                "lang": "cze"
            }
        ]
    ]
    result = make_multilang_list(source)
    assert result == expected_result


def test_multilang_list_2():
    source = {
        "cs": [
            "srovnávací religionistika"
        ],
        "en": []
    }
    expected_result = [
        [
            {
                "value": "srovnávací religionistika",
                "lang": "cze"
            }
        ]
    ]
    result = make_multilang_list(source)
    assert result == expected_result


def test_multilang_list_3():
    source = {
        "cs": [
            "sociální antropologie"
        ],
        "en": [
            "social anthropology"
        ]
    }
    expected_result = [
        [
            {
                "value": "sociální antropologie",
                "lang": "cze"
            },
            {
                "value": "social anthropology",
                "lang": "eng"
            }
        ]
    ]
    result = make_multilang_list(source)
    assert result == expected_result
