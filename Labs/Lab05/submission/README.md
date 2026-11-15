# Lab 05 submission evidence

The report and JSON files come from the local run on 15 November 2026 using the captured Sentinel-2 fixtures
Open `report/index.html` to see the six completed products
The report includes the catalogue snapshot, manifest and preview

The evidence files show states and attempt IDs before and after each drill
The coordinator exited with code 87 after one result
The worker exit code 86 is saved seperately
`identity.json` compares storage and scientific changes

Paths and timestamps belong to the original run
They do not show if files are available now or make the snapshots executable after moving them

To reproduce, install `requirements.txt` and run the cells in `Lab05_Solution.ipynb` from the Lab05 directory
Use a fresh workspace without a file synchronizer
The notebook writes `work/`, `cases/`, `reports/` and `evidence/`
Keep them together for reruns so the earlier recovery evidence remains available
For a fresh run, use a fresh copy or remove only your own generated workspace
If the solution notebook is missing, restore it from Git first

The outputs use nodata masking
Cloud and shadow suitability and independent calibration review are unassessed
Live acquisition was not run for this saved evidence
