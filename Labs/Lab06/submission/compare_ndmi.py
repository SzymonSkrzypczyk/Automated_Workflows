"""Compare the two NDMI rasters only where both are valid."""
import json
import sys

import numpy as np
import rasterio

with open(sys.argv[1], encoding="utf-8") as stream:
    members = json.load(stream)["members"]
paths = [member["result"]["paths"]["index"] for member in members]
with rasterio.open(paths[0]) as first, rasterio.open(paths[1]) as second:
    if (first.crs, first.transform, first.shape) != (second.crs, second.transform, second.shape):
        raise ValueError("The two rasters do not share a grid")
    a, b = first.read(1), second.read(1)
valid = np.isfinite(a) & np.isfinite(b)
if not valid.any():
    raise ValueError("The rasters have no common valid pixels")
print(f"Common pixels: {valid.sum()}")
print(f"First mean: {a[valid].mean():.6f}")
print(f"Second mean: {b[valid].mean():.6f}")
print(f"Mean difference: {(b[valid] - a[valid]).mean():.6f}")
