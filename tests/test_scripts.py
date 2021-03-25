from copy import deepcopy

from scripts.database.fix_level_taxonomy import change_taxonomy, add_level


def test_change_taxonomy():
    json = {
        'title': [{
            'en': 'Application of Sustainable Development Concept as a Factor of '
                  'International Competitiveness'
        }],
        '$schema': 'https://repozitar.narodni-repozitar.cz/schemas/nr_theses/nr-theses-v1.0.0.json',
        'creator': [{'name': 'Kolmosová, Lucia'}], 'abstract': {
            'cs': "\nThis Master's thesis focuses on the application of the sustainable "
                  "development concept in the company Volkswagen Slovakia to enhance its "
                  "competitiveness. The automotive company is analysed as a player in the "
                  "sustainable mobility industry and its current strategy is evaluated in sense "
                  "of sustainability. Based on the most relevant aspects of the analytical part, "
                  "several recommendations are suggested that should boost the firm's operations "
                  "in the area of electric vehicles production and mobility service providing and "
                  "which should contribute to achieving the eco-advantage in the industry.\n",
            'en': '\nTato diplomová práce se zaměřuje na aplikaci koncepce udržitelného rozvoje '
                  've firmě Volkswagen Slovakia na posílení její konkurenceschopnosti. '
                  'Automobilová společnost je analyzována jako hráč v odvětví udržitelné mobility '
                  'a její současná strategie je zhodnocena v zmyslu udržitelnosti. Na základě '
                  'nejrelevantnějších aspektů analytické části je navržena řada doporučení, '
                  'které by měli podpořit působení firmy v oblasti výroby elektrických vozidel a '
                  'poskytování transportních služeb a které by měli přispět k dosažení '
                  'eko-konkurenční výhody v daném odvětví.\n'
        }, 'defended': True,
        'keywords': [{'cs': 'sustainable development', 'en': 'udržitelný rozvoj'},
                     {'cs': 'competitiveness', 'en': 'konkurenceschopnost'},
                     {'cs': 'value', 'en': 'hodnota'},
                     {'cs': 'sustainable mobility', 'en': 'udržitelná mobilita'},
                     {'cs': 'electric vehicles', 'en': 'elektrická vozidla'},
                     {'cs': 'eco-efficiency', 'en': 'ekologická efektivnost'}], 'language': [],
        'provider': [{
            'ico': '00216305', 'url': 'http://www.vutbr.cz',
            'type': ['veřejná VŠ', 'veřejná VŠ'], 'links': {
                'self': 'https://localhost:8080/api/2.0/taxonomies/institutions/00216305'
            }, 'title': {
                'cs': 'Vysoké učení technické v Brně', 'en': 'Brno University of Technology'
            }, 'status': 'active', 'aliases': ['VUT', 'VUT'], 'related': {'rid': '26000'},
            'provider': True, 'is_ancestor': False
        }], 'publisher': 'Vysoké učení technické v Brně. Fakulta podnikatelská',
        'dateIssued': '2017', 'contributor': [{
            'name': 'Kojdová, Zuzana', 'role': [{
                'links': {
                    'self': 'https://localhost:8080/api/2.0/taxonomies/contributor-type/referee'
                },
                'title': {
                    'cs': 'oponent',
                    'en': 'referee'
                },
                'marcCode': 'opn',
                'is_ancestor': False
            }]
        }, {
            'name': 'Zich, Robert', 'role': [{
                'links': {
                    'self': 'https://localhost:8080/api/2.0/taxonomies/contributor-type/advisor'
                }, 'title': {
                    'cs': 'vedoucí', 'en': 'advisor'
                }, 'marcCode': 'ths', 'is_ancestor': False
            }]
        }], 'accessRights': [{
            'links': {
                'self': 'https://localhost:8080/api/2.0/taxonomies/accessRights/c-abf2'
            }, 'title': {
                'cs': 'otevřený přístup', 'en': 'open access'
            }, 'relatedURI': {'coar': 'http://purl.org/coar/access_right/c_abf2'},
            'is_ancestor': False
        }], 'dateDefended': '2017',
        'oarepo:draft': True, 'resourceType': [{
            'alias': {'cs': 'VŠKP', 'en': 'ETDs'}, 'links': {
                'self': 'https://localhost:8080/api/2.0/taxonomies/resourceType/theses-etds'
            }, 'title': {'cs': 'závěrečné práce', 'en': 'Theses (etds)'}, 'is_ancestor': True
        }, {
            'isGL': 'True', 'links': {
                'self': 'https://localhost:8080/api/2.0/taxonomies/resourceType/theses-etds'
                        '/master-theses',
                'parent': 'https://localhost:8080/api/2.0/taxonomies/resourceType/theses-etds'
            }, 'title': {'cs': 'Diplomové práce', 'en': 'Master theses'},
            'COARtype': ['master thesis', 'master thesis'],
            'nuslType': ['diplomove_prace',
                         'diplomove_prace'], 'relatedURI': [
                'http://purl.org/coar/resource_type/c_bdcc',
                'http://purl.org/coar/resource_type/c_bdcc'], 'is_ancestor': False
        }], 'accessibility': {
            'cs': 'Plný text je dostupný v Digitální knihovně VUT.',
            'en': 'Fulltext is available in the Brno University of Technology Digital Library.'
        }, 'control_number': '356997', 'oarepo:validity': {
            'valid': False, 'errors': {
                'marshmallow': [
                    {'field': 'degreeGrantor', 'message': 'Missing data for required field.'},
                    {'field': 'dateDefended', 'message': 'Not a valid date.'}]
            }
        }, 'recordIdentifiers': {
            'nuslOAI': 'oai:invenio.nusl.cz:356997',
            'originalRecord': 'http://hdl.handle.net/11012/69217',
            'originalRecordOAI': 'oai:dspace.vutbr.cz:11012/69217'
        }
    }
    new_json = deepcopy(json)
    res = change_taxonomy(new_json)
    assert res == {
        '$schema': 'https://repozitar.narodni-repozitar.cz/schemas/nr_theses/nr-theses-v1.0.0.json',
        'abstract': {
            'cs': '\n'
                  "This Master's thesis focuses on the application of the "
                  'sustainable development concept in the company Volkswagen '
                  'Slovakia to enhance its competitiveness. The automotive '
                  'company is analysed as a player in the sustainable '
                  'mobility industry and its current strategy is evaluated '
                  'in sense of sustainability. Based on the most relevant '
                  'aspects of the analytical part, several recommendations '
                  "are suggested that should boost the firm's operations in "
                  'the area of electric vehicles production and mobility '
                  'service providing and which should contribute to '
                  'achieving the eco-advantage in the industry.\n',
            'en': '\n'
                  'Tato diplomová práce se zaměřuje na aplikaci koncepce '
                  'udržitelného rozvoje ve firmě Volkswagen Slovakia na '
                  'posílení její konkurenceschopnosti. Automobilová '
                  'společnost je analyzována jako hráč v odvětví udržitelné '
                  'mobility a její současná strategie je zhodnocena v zmyslu '
                  'udržitelnosti. Na základě nejrelevantnějších aspektů '
                  'analytické části je navržena řada doporučení, které by '
                  'měli podpořit působení firmy v oblasti výroby '
                  'elektrických vozidel a poskytování transportních služeb a '
                  'které by měli přispět k dosažení eko-konkurenční výhody v '
                  'daném odvětví.\n'
        },
        'accessRights': [{
            'is_ancestor': False,
            'level': 1,
            'links': {
                'self':
                    'https://localhost:8080/api/2.0/taxonomies/accessRights/c-abf2'
            },
            'relatedURI': {'coar': 'http://purl.org/coar/access_right/c_abf2'},
            'title': {'cs': 'otevřený přístup', 'en': 'open access'}
        }],
        'accessibility': {
            'cs': 'Plný text je dostupný v Digitální knihovně VUT.',
            'en': 'Fulltext is available in the Brno University of '
                  'Technology Digital Library.'
        },
        'contributor': [{
            'name': 'Kojdová, Zuzana',
            'role': [{
                'is_ancestor': False,
                'level': 1,
                'links': {
                    'self':
                        'https://localhost:8080/api/2.0/taxonomies/contributor-type/referee'
                },
                'marcCode': 'opn',
                'title': {'cs': 'oponent', 'en': 'referee'}
            }]
        },
            {
                'name': 'Zich, Robert',
                'role': [{
                    'is_ancestor': False,
                    'level': 1,
                    'links': {
                        'self':
                            'https://localhost:8080/api/2.0/taxonomies/contributor-type/advisor'
                    },
                    'marcCode': 'ths',
                    'title': {'cs': 'vedoucí', 'en': 'advisor'}
                }]
            }],
        'control_number': '356997',
        'creator': [{'name': 'Kolmosová, Lucia'}],
        'dateDefended': '2017',
        'dateIssued': '2017',
        'defended': True,
        'keywords': [{'cs': 'sustainable development', 'en': 'udržitelný rozvoj'},
                     {'cs': 'competitiveness', 'en': 'konkurenceschopnost'},
                     {'cs': 'value', 'en': 'hodnota'},
                     {'cs': 'sustainable mobility', 'en': 'udržitelná mobilita'},
                     {'cs': 'electric vehicles', 'en': 'elektrická vozidla'},
                     {'cs': 'eco-efficiency', 'en': 'ekologická efektivnost'}],
        'language': [],
        'oarepo:draft': True,
        'oarepo:validity': {
            'errors': {
                'marshmallow': [{
                    'field': 'degreeGrantor',
                    'message': 'Missing data for '
                               'required field.'
                },
                    {
                        'field': 'dateDefended',
                        'message': 'Not a valid '
                                   'date.'
                    }]
            },
            'valid': False
        },
        'provider': [{
            'aliases': ['VUT', 'VUT'],
            'ico': '00216305',
            'is_ancestor': False,
            'level': 1,
            'links': {
                'self':
                    'https://localhost:8080/api/2.0/taxonomies/institutions/00216305'
            },
            'provider': True,
            'related': {'rid': '26000'},
            'status': 'active',
            'title': {
                'cs': 'Vysoké učení technické v Brně',
                'en': 'Brno University of Technology'
            },
            'type': ['veřejná VŠ', 'veřejná VŠ'],
            'url': 'http://www.vutbr.cz'
        }],
        'publisher': 'Vysoké učení technické v Brně. Fakulta podnikatelská',
        'recordIdentifiers': {
            'nuslOAI': 'oai:invenio.nusl.cz:356997',
            'originalRecord': 'http://hdl.handle.net/11012/69217',
            'originalRecordOAI': 'oai:dspace.vutbr.cz:11012/69217'
        },
        'resourceType': [{
            'alias': {'cs': 'VŠKP', 'en': 'ETDs'},
            'is_ancestor': True,
            'level': 1,
            'links': {
                'self':
                    'https://localhost:8080/api/2.0/taxonomies/resourceType/theses-etds'
            },
            'title': {'cs': 'závěrečné práce', 'en': 'Theses (etds)'}
        },
            {
                'COARtype': ['master thesis', 'master thesis'],
                'isGL': 'True',
                'is_ancestor': False,
                'level': 2,
                'links': {
                    'parent': 'https://localhost:8080/api/2.0/taxonomies/resourceType/theses-etds',
                    'self': 'https://localhost:8080/api/2.0/taxonomies/resourceType/theses-etds'
                            '/master-theses'
                },
                'nuslType': ['diplomove_prace', 'diplomove_prace'],
                'relatedURI': ['http://purl.org/coar/resource_type/c_bdcc',
                               'http://purl.org/coar/resource_type/c_bdcc'],
                'title': {'cs': 'Diplomové práce', 'en': 'Master theses'}
            }],
        'title': [{
            'en': 'Application of Sustainable Development Concept as a Factor '
                  'of International Competitiveness'
        }]
    }


def test_add_level():
    value = {
        'ico': '00216305', 'url': 'http://www.vutbr.cz', 'type': ['veřejná VŠ', 'veřejná VŠ'],
        'links': {'self': 'https://localhost:8080/api/2.0/taxonomies/institutions/00216305'},
        'title': {
            'cs': 'Vysoké učení technické v Brně', 'en': 'Brno University of Technology'
        }, 'status': 'active', 'aliases': ['VUT', 'VUT'], 'related': {'rid': '26000'},
        'provider': True, 'is_ancestor': False
    }
    res = add_level(value)
    assert res["level"] == 1
