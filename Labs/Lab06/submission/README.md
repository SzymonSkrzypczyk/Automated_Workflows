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
| `reproduce.py` and `compare_ndmi.py` | Local reproduction and common-pixel comparison helpers |

From the Lab 06 directory, `python submission/reproduce.py` runs the personal investigation with the included inputs in a new local workspace. It creates local manifests and reports without changing the saved evidence. See `report.md` for the individual commands and the limits of comparing results across environments

The input bundle is included here to satisfy the handout's submission requirement. Generated raster outputs and SQLite catalogues stay in the ignored `work/` directory
