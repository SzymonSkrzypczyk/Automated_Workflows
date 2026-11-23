"""Independently check the first valid 2020 pixel against the original bands."""
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from rasterio.windows import from_bounds

bundle = Path(__file__).resolve().parent / 'inputs'
manifest = json.loads((bundle / 'manifest.json').read_text(encoding='utf-8'))
report = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
member = next(m for m in report['members'] if m['member_id'] == 'czeladz_20200701_ndbi')
source = next(m for m in manifest['members'] if m['item_file'].startswith('S2A_T34UCA_20200701'))
with rasterio.open(member['result']['paths']['index']) as output:
    array = output.read(1)
    for row, col in zip(*np.where(np.isfinite(array))):
        x0, y1 = output.transform * (int(col), int(row))
        x1, y0 = output.transform * (int(col) + 1, int(row) + 1)
        values = {}
        for role in ('nir', 'swir16'):
            record = source['bands'][role]
            with rasterio.open(bundle / record['file']) as band:
                raw = band.read(1, window=from_bounds(x0, y0, x1, y1, band.transform))
            values[role] = float(raw.mean()) * record['plan']['scale'] + record['plan']['offset']
        expected = (values['swir16'] - values['nir']) / (values['swir16'] + values['nir'])
        actual = float(array[row, col])
        if not np.isclose(expected, actual, atol=1e-6):
            raise AssertionError(f'Expected {expected}, got {actual}')
        print(f'Pixel ({row}, {col}): NIR {values["nir"]:.6f}, SWIR1 {values["swir16"]:.6f}, expected {expected:.6f}, observed {actual:.6f}')
        break
    else:
        raise ValueError('No valid output pixel to check')
