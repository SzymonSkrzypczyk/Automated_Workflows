import numpy as np

from extensions.ndbi import PRODUCT


def test_ndbi_sign_mask_and_zero_denominator():
    bands = {"nir": np.array([[0.2, 0.0, 0.1]]),
             "swir16": np.array([[0.6, 0.0, 0.7]])}
    result = PRODUCT.calculate(bands, np.array([[True, True, False]]),
                               {"epsilon": 1e-6, "threshold": 0.0}, 400)
    assert np.isclose(result.layers["index"][0, 0], 0.5)
    assert result.layers["candidate"][0, 0] == 1
    assert np.isnan(result.layers["index"][0, 1:]).all()
    assert np.isnan(result.layers["candidate"][0, 1:]).all()
    assert result.metrics["candidate_area_m2"] == 400
