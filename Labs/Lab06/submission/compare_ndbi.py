"""Compare candidate classes on pixels observed on both dates."""
import json
import sys

import numpy as np
import rasterio

with open(sys.argv[1], encoding="utf-8") as stream:
    members = json.load(stream)["members"]
paths = [member["result"]["paths"]["candidate"] for member in members]
with rasterio.open(paths[0]) as first, rasterio.open(paths[1]) as second:
    if (first.crs, first.transform, first.shape) != (second.crs, second.transform, second.shape):
        raise ValueError("The two rasters do not share a grid")
    a, b = first.read(1), second.read(1)
    pixel_area = abs(first.transform.a * first.transform.e - first.transform.b * first.transform.d)
valid = np.isfinite(a) & np.isfinite(b)
if not valid.any():
    raise ValueError("The rasters have no common valid pixels")
first_count = int(np.count_nonzero(valid & (a == 1)))
second_count = int(np.count_nonzero(valid & (b == 1)))
gain = int(np.count_nonzero(valid & (a == 0) & (b == 1)))
loss = int(np.count_nonzero(valid & (a == 1) & (b == 0)))
print(json.dumps({"common_pixels": int(valid.sum()), "pixel_area_m2": pixel_area,
                  "first_candidate_pixels": first_count, "second_candidate_pixels": second_count,
                  "candidate_gain_pixels": gain, "candidate_loss_pixels": loss,
                  "net_candidate_area_change_m2": (second_count - first_count) * pixel_area}, indent=2))
