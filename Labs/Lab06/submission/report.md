# Lab 06 investigation

Package version 1.0.0

## Reference run

I expected six requests and no new attempts on a repeat. The first run created six successful attempts and the second created none. There are three dates and two AOIs for each date, so six requests do not mean six dates

The MNDWI product declares green and SWIR16, calculates `(green - SWIR16) / (green + SWIR16)` and returns index and water layers. To add a third band I would declare it in `required_bands`, acquire and register that band for each scene, then use it in `calculate`. Planning records the request, preparation calibrates, masks and aligns the inputs, and the runner handles attempts, output verification and reuse. The database stores the history and artifact locations, while QC assesses whether the result meets the selected policy

| River date | Raw coverage | Usable coverage | Candidate water area |
|---|---:|---:|---:|
| 4 June | 100% | 47.60% | 130,000 m² |
| 5 June | 100% | 99.40% | 231,200 m² |

The 4 June scene has much less usable coverage, so the area difference alone cannot show that the river changed. I would compare the same valid pixels on both dates and check the classifications against independent imagery or observations

With cloud screening disabled on 4 June, usable coverage rose to 100% and candidate water area to 233,600 m². The output includes cloud and shadow observations, so a finite pixel is not necessarily a useful surface observation. QC marked that diagnostic request for review

For 5 June, raising the water threshold from 0 to 0.15 reduced candidate water area from 231,200 to 181,600 m². This created a new request because the threshold changes the classification. I would select a threshold using labelled water and non-water samples, then check errors on independent locations and dates

At a minimum valid fraction of 0.5, assessment IDs 1–6 rejected both 4 June requests and accepted the other four. At 0.995, IDs 9–14 rejected all six, including the 5 June river attempt whose valid fraction was 0.99396. The reassessment started zero attempts and left the earlier executions succeeded: execution status records whether processing completed, while QC records whether its result meets a policy

The query in `investigation.sql` lists each attempt with its assessments. For `attempt-f94fa31d2daa46ada155827b1d85f540`, assessment 3 accepted the result at 0.5 and assessment 11 rejected it at 0.995. The saved `evidence/common/assessments.json` contains both assessments and their policies. The MNDWI attempts each have the named outputs `index` and `water`, plus the shared `valid_mask`. Changing a QC threshold uses already measured coverage, while changing the cloud mask changes which observations enter the calculation and therefore needs a new request

## Personal product

I used NDBI to compare candidate built-up surfaces in a part of Czeladź on 1 July 2020 and 5 July 2025. The question, bands, source and preparation choices are in [science_plan.md](science_plan.md). The extension is `extensions/ndbi.py`, version 1.0.0. The bounding box includes surrounding land and is not the municipal boundary

| Date | Raw coverage | Usable coverage | Candidate area at threshold 0 | QC at 0.5 |
|---|---:|---:|---:|---|
| 1 July 2020 | 100% | 99.81% | 2,361,200 m² | accepted |
| 5 July 2025 | 100% | 99.55% | 1,928,800 m² | accepted |

On the 47,240 pixels valid on both dates, 5,836 were candidates in 2020 and 4,797 in 2025. There were 2,036 transitions into the candidate class and 3,075 out of it, a net change of −415,600 m² at 400 m² per pixel. These are spectral threshold transitions, not confirmed construction or demolition, and this result does not establish urban expansion. Crops, exposed soil, changing moisture and mixed pixels can change the classification. I would inspect gain and loss locations against independent dated high-resolution imagery and use labelled samples to measure errors before making a land-use claim

The first run launched two attempts and repeating it launched none. Raising the 2025 threshold from 0 to 0.1 created request `request-ec50f2e3e5b0b6875c4ad58f99e73355574344983618a7b3e0a14955e15ccde1` and a new attempt. Its candidate area fell from 1,928,800 to 246,800 m² over the 2025 valid pixels. This sensitivity shows that the starting threshold of 0 needs validation rather than being treated as an established boundary between built and unbuilt land

For an independent arithmetic check I used SWIR1 0.6 and NIR 0.2, which gives NDBI 0.5 by hand. The test returned 0.5 and candidate class 1, and checked that a zero denominator and a masked pixel become NaN. I also calculated a real 2020 output pixel from the bundled raw bands and their calibration: NIR 0.2778 and SWIR1 0.1198 give −0.397384, matching the raster value −0.397384. These checks do not validate the map against ground observations

## Reproduction and evidence

From `Labs/Lab06`, run `python submission/reproduce.py` in the lab environment. It registers the included inputs, creates local manifests, runs both configurations and writes reports and the common-pixel comparison to `work/czeladz-reproduction`. To keep an existing workspace, choose a new one with `--workspace work/another-run`. It uses no network for the bundled inputs

The retained `submission/inputs` bundle contains the source item records, B08, B11 and SCL subsets, checksums and acquisition metadata. The script creates new local manifests because those in `submission/evidence` record the original absolute paths and environment. Different software versions or operating systems are recorded in the new request identity and may affect the results

The individual commands used for the original run are below

```text
python -m eo_processing init --database work/czeladz/catalogue.sqlite
python -m eo_processing register --database work/czeladz/catalogue.sqlite --bundle submission/inputs
python -m eo_processing plan --config config/personal_batch.json --out work/czeladz/batch.json
python -m eo_processing run --manifest work/czeladz/batch.json
python -m eo_processing assess --manifest work/czeladz/batch.json --minimum-valid-fraction 0.5
python -m eo_processing report --manifest work/czeladz/batch.json --out work/czeladz/report
python -m eo_processing run --manifest work/czeladz/batch.json
python -m eo_processing plan --config config/personal_threshold010.json --out work/czeladz/threshold010_batch.json
python -m eo_processing run --manifest work/czeladz/threshold010_batch.json
python -m eo_processing assess --manifest work/czeladz/threshold010_batch.json
python -m eo_processing report --manifest work/czeladz/threshold010_batch.json --out work/czeladz/threshold010_report
python submission/compare_ndbi.py work/czeladz/report/report.json
python submission/check_real_ndbi.py work/czeladz/report/report.json
python -m pytest tests/test_personal_ndbi.py
python -m eo_processing check-core
```

I obtained the inputs with `python -m eo_processing acquire --config config/personal_acquisition.json --destination work/czeladz/inputs` after searching the public Earth Search catalogue. The exact item IDs, source URLs, checksums and calibration are in `submission/inputs/manifest.json`. The frozen manifests and generated JSON and HTML reports are in `submission/evidence`. `check-core` reported version 1.0.0 identical to the class release with no changed files

## Debugging clinic and assistance

The original attempt had written a temporary raster but failed before publishing and recording a successful result. Opening the existing binary file with `r+b` provides write access for the Windows flush without truncating it. The exercise check passed twice and confirmed that all 77,910 bytes stayed unchanged. The shared core was already corrected, so editing the exercise did not change its hash. The original runner correction changed the processing code hash and therefore needed new manifests while preserving the failed attempts

I used Codex to help trace the package, write the extension and organize the results. I checked the equation against the NDBI source, ran the arithmetic and invalid-pixel test, inspected the recorded coverage and compared the repeat and changed-threshold requests. I did not treat the candidate transitions as proof of construction because bare ground and other surfaces can also cross the threshold
