-- Write your own diagnostic SQL for the five new tables.
-- One worked example follows. Add your case queries below it.
SELECT r.run_id,r.command,a.item_id,a.asset_key,s.aoi_key,d.status,d.stage,
       d.network_bytes,d.http_status,d.error_code,d.error_message
FROM download_attempts d JOIN runs r ON r.run_id=d.run_id
JOIN subset_requests s ON s.subset_id=d.subset_id
JOIN assets a ON a.asset_id=s.asset_id
ORDER BY d.started_at,d.attempt_id;

-- Case A: show failed band, partial success and the later recovery history.
SELECT
    d.run_id,
    a.asset_key,
    d.attempt_id,
    d.status,
    d.stage,
    d.network_bytes,
    d.artifact_id,
    d.error_code,
    d.error_message
FROM download_attempts AS d
JOIN subset_requests AS s
    ON s.subset_id = d.subset_id
JOIN assets AS a
    ON a.asset_id = s.asset_id
WHERE d.status = 'failed'
   OR d.error_code IS NOT NULL
ORDER BY d.started_at, d.attempt_id;


-- Case B: show successful historical acquisition but current missing/corrupt location.
SELECT
    a.asset_key,
    ar.artifact_id,
    ar.sha256,
    ar.size_bytes,
    d.attempt_id,
    d.status AS attempt_status,
    l.local_path,
    l.status AS location_status,
    l.checked_at
FROM artifacts AS ar
JOIN subset_requests AS s
    ON s.subset_id = ar.subset_id
JOIN assets AS a
    ON a.asset_id = s.asset_id
JOIN download_attempts AS d
    ON d.attempt_id = ar.created_by_attempt_id
LEFT JOIN artifact_locations AS l
    ON l.artifact_id = ar.artifact_id
WHERE d.status IN ('succeeded', 'reused')
ORDER BY a.asset_key, l.checked_at;


-- AOI identity: show one source band with separate requests for two AOIs.
SELECT
    a.asset_key,
    s.asset_id,
    s.subset_id,
    s.aoi_key,
    s.aoi_json,
    s.recipe_version,
    s.status,
    s.latest_artifact_id
FROM subset_requests AS s
JOIN assets AS a
    ON a.asset_id = s.asset_id
WHERE a.asset_key = 'red'
ORDER BY s.aoi_key;
