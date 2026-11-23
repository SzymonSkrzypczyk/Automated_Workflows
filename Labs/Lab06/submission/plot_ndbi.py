"""Plot the NDBI rasters from a locally generated personal report."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
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

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 6.2), layout="constrained", sharex=True, sharey=True)
    cmap = LinearSegmentedColormap.from_list("ndbi", ["#405c69", "#9fb5b0", "#f0ede2", "#c79271", "#8c5141"])
    cmap.set_bad("#dededc")
    bounds = grids[0][3]
    for ax, data, (_, date) in zip(axes, arrays, scenes):
        image = ax.imshow(np.ma.masked_invalid(data), cmap=cmap, vmin=-0.6, vmax=0.6,
                          extent=(bounds.left, bounds.right, bounds.bottom, bounds.top), interpolation="nearest")
        ax.set_title(date, fontsize=11, loc="left", pad=8)
        ax.set_xlabel("Easting (m)", fontsize=9)
        ax.ticklabel_format(style="plain", useOffset=False)
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.tick_params(labelsize=8, length=3, colors="#3f4442")
        for spine in ax.spines.values():
            spine.set_color("#999d99")
            spine.set_linewidth(0.5)
    axes[0].set_ylabel("Northing (m)", fontsize=9)
    fig.suptitle("NDBI in the Czeladź area", fontsize=13, x=0.04, ha="left")
    colorbar = fig.colorbar(image, ax=axes, orientation="horizontal", shrink=0.65, pad=0.08,
                            label="NDBI")
    colorbar.ax.tick_params(labelsize=8, length=3)
    colorbar.outline.set_linewidth(0.5)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
