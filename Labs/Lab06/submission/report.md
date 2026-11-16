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

I used NDMI to compare the 15 and 30 June scenes over central Warsaw and the Vistula. The question, bands, source and preparation choices are in [science_plan.md](science_plan.md). The extension is `extensions/ndmi.py`, version 1.0.0

| Date | Usable coverage | Mean NDMI | QC at 0.5 |
|---|---:|---:|---|
| 15 June | 99.39% | 0.121721 | accepted |
| 30 June | 83.00% | 0.112302 | accepted |

These means include buildings, water and bare ground as well as vegetation, and the second date has less usable coverage. On the 23,672 pixels valid on both dates, the mean was 0.129665 on 15 June and 0.112476 on 30 June, a difference of −0.017188. This is a mixed-surface spectral change, not evidence on its own of a change in vegetation moisture. Field or reference data and a vegetation-specific analysis would help interpret it

The first run launched two attempts and repeating it launched none. Switching the 15 June mask to `nodata_only` produced request `request-335fecccb942a6de1852e7afefb0ed35967ffde9a09dcff96bc99ca666025213` and a new attempt, with mean 0.120784 and 100% usable pixels. QC marked it for review because screening was disabled. The small difference here does not mean cloud screening is unnecessary

For an independent arithmetic check I used NIR 0.6 and SWIR1 0.2, which gives 0.5 by hand. The test returned 0.5 and also checked that a zero denominator and a masked pixel become NaN. This checks the calculation and mask handling, but does not validate the satellite map against ground measurements

## Reproduction and evidence

The retained `submission/inputs` bundle contains the source item records, B08, B11 and SCL subsets, checksums and acquisition metadata. On another machine, register the bundle and create new local manifests because those in `submission/evidence` record the original absolute paths and environment. Different software versions or operating systems are recorded in the new request identity and may affect the results

The individual commands used for the original run are below

```text
python -m eo_processing init --database work/warsaw/catalogue.sqlite
python -m eo_processing register --database work/warsaw/catalogue.sqlite --bundle submission/inputs
python -m eo_processing plan --config config/personal_batch.json --out work/warsaw/batch.json
python -m eo_processing run --manifest work/warsaw/batch.json
python -m eo_processing assess --manifest work/warsaw/batch.json --minimum-valid-fraction 0.5
python -m eo_processing report --manifest work/warsaw/batch.json --out work/warsaw/report
python -m eo_processing run --manifest work/warsaw/batch.json
python -m eo_processing plan --config config/personal_nodata.json --out work/warsaw/nodata_batch.json
python -m eo_processing run --manifest work/warsaw/nodata_batch.json
python -m eo_processing assess --manifest work/warsaw/nodata_batch.json
python -m eo_processing report --manifest work/warsaw/nodata_batch.json --out work/warsaw/nodata_report
python submission/compare_ndmi.py work/warsaw/report/report.json
python -m pytest tests/test_personal_ndmi.py
python -m eo_processing check-core
```

I obtained the inputs with `python -m eo_processing acquire --config config/personal_acquisition.json --destination work/warsaw/inputs` after searching the public Earth Search catalogue. The exact item IDs, source URLs, checksums and calibration are in `submission/inputs/manifest.json`. The frozen manifests and generated JSON and HTML reports are in `submission/evidence`. `check-core` reported version 1.0.0 identical to the class release with no changed files

## Debugging clinic and assistance

The original attempt had written a temporary raster but failed before publishing and recording a successful result. Opening the existing binary file with `r+b` provides write access for the Windows flush without truncating it. The exercise check passed twice and confirmed that all 77,910 bytes stayed unchanged. The shared core was already corrected, so editing the exercise did not change its hash. The original runner correction changed the processing code hash and therefore needed new manifests while preserving the failed attempts

I used Codex to help trace the package, write the extension and organize the results. I checked the index against the USGS definition, ran the arithmetic and invalid-pixel test, inspected the recorded coverage and compared the repeat and changed-mask requests. The AOI-wide mean includes several land covers, so I did not treat it as a direct vegetation moisture measurement
