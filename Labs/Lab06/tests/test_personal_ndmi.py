import numpy as np

from extensions.ndmi import PRODUCT


def test_ndmi_band_order_and_invalid_pixels():
    bands = {"nir": np.array([[0.6, 0.0, 0.7]]),
             "swir16": np.array([[0.2, 0.0, 0.1]])}
    valid = np.array([[True, True, False]])
    result = PRODUCT.calculate(bands, valid, {"epsilon": 1e-6}, 400)
    assert np.isclose(result.layers["index"][0, 0], 0.5)
    assert np.isnan(result.layers["index"][0, 1:]).all()
    assert np.isclose(result.metrics["mean_ndmi"], 0.5)
