# My scientific product

## Question

Where did candidate built-up surfaces change in a part of Czeladź between 2020 and 2025, based on Sentinel-2 NDBI? I want to locate possible development, then check candidate changes against independent imagery before interpreting them as construction

## Method and inputs

NDBI = (SWIR1 − NIR) / (SWIR1 + NIR), using Sentinel-2 B11 and B08 surface reflectance. The [original NDBI paper](https://doi.org/10.1080/01431160304987) describes the built-up index. I will calculate a dimensionless index and a candidate layer using a threshold of 0 as an exploratory starting point, with NaN for invalid pixels and near-zero denominators

The WGS84 bounding box `[19.04, 50.29, 19.10, 50.33]` covers part of Czeladź and nearby land, not the official municipal boundary. It includes built-up and less developed surroundings where changes could be inspected. The selected catalogue items are `S2A_T34UCA_20200701T095501_L2A` and `S2C_T34UCA_20250705T095217_L2A`, both from early July. I will check actual AOI coverage because tile cloud cover is only a screening hint

The acquisition provides calibration metadata. I will use a 20 m grid matching B11 and exclude SCL classes 0, 1, 2, 3, 7, 8, 9, 10 and 11. The product returns an index and candidate class, with 0 for below threshold, 1 for above and NaN for unknown. Candidate area uses 400 m² per grid pixel. I will compare a second threshold to show sensitivity, and use only pixels valid in both dates for the change calculation

Bare soil, construction sites, roofs, shadows, crop cycles and mixed 20 m pixels can affect the result. The 0 threshold is not a validated classification rule, and a positive change is not proof of new buildings. I would compare candidate locations against independent dated high-resolution imagery or land-cover records and use labelled samples to evaluate errors
