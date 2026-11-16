# Lab 06 submission

The report and science plan are in this folder. The personal NDMI extension, its configurations and its test are in the Lab 06 package

| File or folder | Contents |
|---|---|
| `report.md` and `science_plan.md` | Investigation, results, limitations and assistance note |
| `../extensions/ndmi.py` | Personal product |
| `../config/personal_acquisition.json`, `personal_batch.json` and `personal_nodata.json` | Input selection and processing settings |
| `investigation.sql` | Queries for execution history, outputs and assessments |
| `../tests/test_personal_ndmi.py` | Arithmetic and invalid-pixel check |
| `inputs/` | Small Warsaw input bundle, source item records and checksums |
| `evidence/personal/` and `evidence/nodata/` | Frozen manifests and generated personal reports |
| `evidence/common/` | Reference exercise manifests, reports and assessment history |
| `compare_ndmi.py` | Common-pixel comparison helper |

See `report.md` for the commands to run the personal investigation with the included inputs and for the limits of comparing results across environments

The input bundle is included here to satisfy the handout's submission requirement. Generated raster outputs and SQLite catalogues stay in the ignored `work/` directory
