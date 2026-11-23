"""Plot the NDBI rasters from a locally generated personal report."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import rasterio


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    members = {member["member_id"]: member for member in report["members"]}
    scenes = [("czeladz_20200701_ndbi", "1 July 2020"),
              ("czeladz_20250705_ndbi", "5 July 2025")]
    arrays = []
    grids = []
    for member_id, _ in scenes:
        path = members[member_id]["result"]["paths"]["index"]
        with rasterio.open(path) as raster:
            arrays.append(raster.read(1, masked=True))
            grids.append((raster.crs, raster.transform, raster.shape, raster.bounds))
    if grids[0] != grids[1]:
        raise ValueError("The two index rasters do not share a grid")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6.8), layout="constrained", sharex=True, sharey=True)
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#e5e5e5")
    bounds = grids[0][3]
    for ax, data, (_, date) in zip(axes, arrays, scenes):
        image = ax.imshow(np.ma.masked_invalid(data), cmap=cmap, vmin=-0.6, vmax=0.6,
                          extent=(bounds.left, bounds.right, bounds.bottom, bounds.top), interpolation="nearest")
        ax.set_title(date, fontsize=14, weight="bold")
        ax.set_xlabel("Easting (m)")
        ax.ticklabel_format(style="plain", useOffset=False)
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.tick_params(labelsize=9)
    axes[0].set_ylabel("Northing (m)")
    fig.suptitle("Czeladź area — Normalized Difference Built-up Index\n"
                 "Grey: outside the AOI or unavailable  ·  20 m grid  ·  EPSG:32634", fontsize=13)
    fig.colorbar(image, ax=axes, orientation="horizontal", shrink=0.72, pad=0.08,
                 label="NDBI  ·  blue: lower values    |    red: higher values")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
