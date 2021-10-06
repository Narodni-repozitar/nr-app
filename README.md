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

### Inicializace S3 bucketu pro vychozi file storage location

```bash
S3_BUCKET=oarepo
oarepo files location --default 'default-s3' s3://${S3_BUCKET}
```

### Import taxonomii (data v nr-taxonomies/data/excel)
```shell
oarepo taxonomies import institutions.xlsx
oarepo taxonomies import funders.xlsx
oarepo taxonomies import itemRelationType.xlsx
oarepo taxonomies import countries.xlsx
oarepo taxonomies import licenses.xlsx
oarepo taxonomies import resourceType.xlsx
oarepo taxonomies import languages.xlsx
oarepo taxonomies import accessRights.xlsx
oarepo taxonomies import subjects.xlsx
oarepo taxonomies import subjectCategories.xlsx
oarepo taxonomies import studyFields.xlsx
oarepo taxonomies import Nresults_usage.xlsx
oarepo taxonomies import Nresults_type.xlsx
oarepo taxonomies import contributorType.xlsx
```

### Vytvoření indexu na taxonomiích
```shell
CREATE INDEX json_index ON taxonomy_term USING gin (extra_data);
```

### Vytvoření uživatelů a komunit
```bash
oarepo users create -a <email>
```

```shell
oarepo oarepo:communities create cesnet 'CESNET community' --description 'Default CESNET OA repository community'
oarepo oarepo:communities actions list -c cesnet
```

### Import z NUŠLu
```shell
oarepo oai run -p nusl
```