"""Three plausible implementations to investigate and repair. No syntax puzzles."""
import hashlib
import json
import math
import numpy as np


def _normalize(value):
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Non-finite values cannot identify a request')
        return int(value) if value.is_integer() else value
    return value


def make_request_spec(science, inputs, environment, runtime):
    settings = {k: v for k, v in science.items() if k not in ('stage', 'inputs')}
    records = [{'role': role, **{key: inputs[role][key] for key in
               ('artifact_id', 'sha256', 'size_bytes', 'raster', 'lineage')}}
               for role in ('red', 'nir')]
    spec = _normalize({'stage': science['stage'], 'settings': settings, 'inputs': records,
                       'environment': environment, 'equivalence_policy': 'exact_environment_v1'})
    encoded = json.dumps(spec, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return spec, hashlib.sha256(encoded).hexdigest()


def validate_pair(red, nir):
    for role, record in (('red', red), ('nir', nir)):
        if record['lineage']['asset_key'] != role:
            raise ValueError(f'Incorrect {role} band role')
        raster = record['raster']
        for key in ('scale', 'offset', 'nodata'):
            if not math.isfinite(float(raster[key])):
                raise ValueError(f'Invalid {role} {key}')
        if float(raster['scale']) <= 0:
            raise ValueError(f'Invalid {role} scale')
    for key in ('collection', 'item_id', 'aoi_key', 'recipe_version'):
        if red['lineage'][key] != nir['lineage'][key]:
            raise ValueError(f'Input {key} differs')
    for key in ('crs', 'shape', 'transform'):
        if red['raster'][key] != nir['raster'][key]:
            raise ValueError(f'Input {key} differs')


def calculate_ndvi(red, nir, red_meta, nir_meta, epsilon):
    if red.shape != nir.shape or not math.isfinite(float(epsilon)) or epsilon < 0:
        raise ValueError('Invalid array shapes or denominator threshold')
    valid = (red != red_meta['nodata']) & (nir != nir_meta['nodata'])
    r = red.astype(np.float64) * red_meta['scale'] + red_meta['offset']
    n = nir.astype(np.float64) * nir_meta['scale'] + nir_meta['offset']
    denominator = n + r
    valid &= np.isfinite(r) & np.isfinite(n) & (np.abs(denominator) > epsilon)
    output = np.full(red.shape, np.nan, dtype=np.float32)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        output[valid] = (n[valid] - r[valid]) / denominator[valid]
    return output
