# Lab 06 submission

The report and science plan are in this folder. The personal NDBI extension, its configurations and its test are in the Lab 06 package

| File or folder | Contents |
|---|---|
| `report.md` and `science_plan.md` | Investigation, results, limitations and assistance note |
| `../extensions/ndbi.py` | Personal product |
| `../config/personal_acquisition.json`, `personal_batch.json` and `personal_threshold010.json` | Input selection and processing settings |
| `investigation.sql` | Queries for execution history, outputs and assessments |
| `../tests/test_personal_ndbi.py` | Arithmetic and invalid-pixel check |
| `inputs/` | Small Czeladź input bundle, source item records and checksums |
| `evidence/personal/` and `evidence/threshold010/` | Frozen manifests and generated personal reports |
| `evidence/common/` | Reference exercise manifests, reports and assessment history |
| `reproduce.py`, `compare_ndbi.py` and `check_real_ndbi.py` | Local reproduction, comparison and real-pixel check |

From the Lab 06 directory, `python submission/reproduce.py` runs the personal investigation with the included inputs in a new local workspace. It creates local manifests and reports without changing the saved evidence. See `report.md` for the individual commands and the limits of comparing results across environments

The input bundle is included here to satisfy the handout's submission requirement. Generated raster outputs and SQLite catalogues stay in the ignored `work/` directory
