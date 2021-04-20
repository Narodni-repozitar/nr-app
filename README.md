# Národní repozitář - REST API aplikace

Disclaimer: The library is part of the Czech National Repository, and therefore the README is written in Czech.
General libraries extending [Invenio](https://github.com/inveniosoftware) are concentrated under the [Oarepo
 namespace](https://github.com/oarepo).

## Deployment

TODO buildovací část a nasazení do k8s.

### Vytvoření databázových tabulek a indexů

```bash
# db tables creation
oarepo db create

# destroy old indicies
oarepo index destroy --force --yes-i-know

# create new empty indicies
oarepo index init

#  Initialize indexing queue
oarepo index queue init purge

# Init taxonomies tables
oarepo taxonomies init
```
### Import taxonomii (data v nr-taxonomies/data/excel)
```shell
oarepo taxonomies import institutions
oarepo taxonomies import funders
oarepo taxonomies import itemRelationType
oarepo taxonomies import countries
oarepo taxonomies import licenses
oarepo taxonomies import resourceType
oarepo taxonomies import languages
oarepo taxonomies import accessRights
oarepo taxonomies import subjects
oarepo taxonomies import studyFields
oarepo taxonomies import Nresults_usage
oarepo taxonomies import Nresults_type
oarepo taxonomies import contributorType
```

### Vytvoření indexu na taxonomiích
```shell
CREATE INDEX json_index ON taxonomy_term USING gin (extra_data);
```

### Vytvoření uživatelů a komunit
```bash
oarepo users create -a <email>
```

TODO: Vytvoření komunit a přiřazení práv

### Import z NUŠLu
```shell
oarepo oai run -p nusl
```