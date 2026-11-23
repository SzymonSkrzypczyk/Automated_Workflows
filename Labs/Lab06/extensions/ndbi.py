"""Candidate built-up surfaces using the NDBI of Zha, Gao and Ni (2003)."""
import numpy as np
from eo_processing.products import ProductResult, normalized_difference


class NDBI:
    name = "ndbi"
    version = "1.0.0"
    required_bands = ("nir", "swir16")
    output_roles = ("index", "candidate")
    primary_role = "index"
    nominal_range = (-1.0, 1.0)
    default_parameters = {"epsilon": 1e-6, "threshold": 0.0}

    def calculate(self, bands, valid, parameters, pixel_area_m2):
        index = normalized_difference(bands["swir16"], bands["nir"], parameters["epsilon"])
        index[~valid] = np.nan
        observed = np.isfinite(index)
        candidate = np.full(index.shape, np.nan, dtype="float32")
        candidate[observed] = (index[observed] > parameters["threshold"]).astype("float32")
        count = int(np.count_nonzero(candidate == 1))
        return ProductResult({"index": index, "candidate": candidate}, {
            "candidate_pixels": count,
            "candidate_area_m2": float(count * pixel_area_m2),
            "observed_area_m2": float(observed.sum() * pixel_area_m2),
            "threshold": parameters["threshold"],
        })


PRODUCT = NDBI()
