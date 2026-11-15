# Lab 05 submission evidence

The report and JSON records were generated locally on 15 November 2026 from the captured Sentinel-2 fixtures. Open `report/index.html` to inspect the six completed products. The report includes its catalogue snapshot, manifest and preview.

The evidence files retain the recorded states and attempt identities before and after each drill. The coordinator case exited with code 87 after one result; the worker process exit code 86 is recorded separately. `identity.json` compares storage and scientific changes. Paths and timestamps describe the original run and are historical; they do not establish present file availability or make the snapshots executable after relocation.

To reproduce, install `requirements.txt`, run the code cells in `Lab05_Solution.ipynb` from the Lab05 directory, and use a fresh directory without a file synchronizer. The notebook writes `work/`, `cases/`, `reports/` and `evidence/`. Keep those together when rerunning so the original before-recovery records remain available. Use a fresh copy or remove only your own generated workspace to run the experiments from scratch.

The recorded outputs use nodata masking. Cloud and shadow suitability and independent calibration review remain unassessed. Live acquisition was not run.
