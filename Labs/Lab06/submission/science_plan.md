# My scientific product

## Question

How does the NDMI pattern over a small area near central Kraków compare between 5 and 15 June 2025? I want to see whether the usable observations suggest a change in vegetation moisture conditions, keeping in mind that NDMI also responds to land cover and canopy structure

## Method and inputs

NDMI = (NIR − SWIR1) / (NIR + SWIR1), using Sentinel-2 B08 and B11 reflectance. The [USGS explanation of the index](https://www.usgs.gov/publications/terminology-spectral-vegetation-index-nir-swirnir-swir) describes its use as an indicator of vegetation moisture. I will calculate a dimensionless index and its mean over valid pixels, with NaN for invalid observations and a near-zero denominator

The AOI is `[19.91, 50.04, 19.94, 50.06]` in WGS84, a small mixed urban and vegetated area near Kraków. The public catalogue returned `S2C_T34UDA_20250605T095638_L2A` and `S2C_T34UDA_20250615T095047_L2A`, ten days apart in the same season. Tile cloud cover is only a first filter, so I will check the actual AOI coverage after processing

I will use the calibration supplied with the acquisition, a 20 m grid matching B11, and the default conservative SCL exclusions 0, 1, 2, 3, 7, 8, 9, 10 and 11. I will retain water and bare ground in the initial result, so the AOI-wide mean is a mixed-land-cover summary, not a vegetation-only moisture measurement

The output is an index raster and mean NDMI. I will change the mask policy in a separate request to see how screening affects the result. A check with known inputs and a zero denominator can catch a reversed band order and invalid-value errors

Differences in cloud and shadow coverage, land cover, mixed pixels and changing illumination can affect the comparison. A fair spatial comparison needs the same valid pixels in both dates, and ground observations would be needed to relate the index to actual vegetation water content
