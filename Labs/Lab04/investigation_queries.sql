PRAGMA foreign_keys = ON;

-- Attempts by request and outcome.
SELECT r.request_id, a.status, COUNT(a.attempt_id) AS attempts
FROM processing_requests r LEFT JOIN processing_attempts a ON a.request_id=r.request_id
GROUP BY r.request_id,a.status ORDER BY r.request_id,a.status;

-- Trace each produced NDVI output to the two acquired inputs and their origins.
SELECT o.artifact_id AS ndvi_artifact, a.attempt_id AS producing_attempt,
       r.request_id, r.normalized_json, i.role, p.artifact_id AS input_artifact,
       f.artifact_id AS acquisition_artifact, s.subset_id, s.aoi_json, s.recipe_version,
       asset.collection, asset.item_id, asset.asset_key
FROM processing_outputs o
JOIN processing_attempts a ON a.attempt_id=o.attempt_id AND a.status='succeeded'
JOIN processing_requests r ON r.request_id=a.request_id
JOIN processing_inputs i ON i.request_id=r.request_id
JOIN processing_artifacts p ON p.artifact_id=i.artifact_id
JOIN artifacts f ON f.artifact_id=p.source_artifact_id
JOIN subset_requests s ON s.subset_id=f.subset_id
JOIN assets asset ON asset.asset_id=s.asset_id
WHERE o.role='ndvi' ORDER BY o.artifact_id,i.role;

-- Failed, interrupted and later attempts remain visible for the same request.
SELECT request_id,attempt_id,status,stage,error_code,error_message,started_at,finished_at
FROM processing_attempts ORDER BY request_id,started_at,attempt_id;

-- Historical successes whose artifact currently has no recorded available location.
-- Current disk state still requires a filesystem and checksum check.
SELECT a.attempt_id,o.artifact_id
FROM processing_attempts a JOIN processing_outputs o ON o.attempt_id=a.attempt_id
WHERE a.status='succeeded' AND NOT EXISTS
 (SELECT 1 FROM processing_artifact_locations l WHERE l.artifact_id=o.artifact_id AND l.status='available');

-- An unresolved attempt can have a receipt and file without a published output.
SELECT a.attempt_id,a.status,a.stage,a.temp_path,a.final_path,a.receipt_json,o.artifact_id
FROM processing_attempts a LEFT JOIN processing_outputs o ON o.attempt_id=a.attempt_id
WHERE a.status IN ('running','interrupted') ORDER BY a.started_at;

-- Compare source values with the reviewed settings preserved in the request.
SELECT i.role, json_extract(p.raster_json,'$.scale') AS source_scale,
 json_extract(p.raster_json,'$.offset') AS source_offset,
 json_extract(r.normalized_json,'$.settings.calibration.' || i.role || '.scale') AS reviewed_scale,
 json_extract(r.normalized_json,'$.settings.calibration.' || i.role || '.offset') AS reviewed_offset,
 json_extract(r.normalized_json,'$.settings.calibration.' || i.role || '.evidence') AS review_evidence
FROM processing_requests r JOIN processing_inputs i ON i.request_id=r.request_id
JOIN processing_artifacts p ON p.artifact_id=i.artifact_id ORDER BY r.request_id,i.role;
