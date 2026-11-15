-- Each query is read-only. Bind :batch_id from batch_plan.load(path)['batch_id'].
-- Timestamps are recorded UTC observations, not promises about the filesystem now.

-- Q1. Which expected members have never reached an application attempt?
-- Parameters: :batch_id.
-- Columns: member_id, planned_request_id, request_id (NULL before registration).
-- Empty: every expected request has a non-reused attempt; success is not implied.
-- Next: inspect current states and producing outputs before claiming completion.
SELECT m.member_id, m.planned_request_id, m.request_id
FROM batch_members AS m
WHERE m.batch_id = :batch_id
  AND NOT EXISTS (
    SELECT 1 FROM processing_attempts AS a
    WHERE a.request_id = m.planned_request_id AND a.status <> 'reused'
  )
ORDER BY m.member_id;

-- Q2. Which failed/stopped request later produced a currently recorded verified result?
-- Parameters: :batch_id.
-- Columns: member_id, request_id, earlier_attempt_id/status, producing_attempt_id,
--          artifact_id, earlier_started_at, producing_started_at, verified_at.
-- Empty: no recovery meets these conditions in the latest observations.
-- Next: refresh file checks, then inspect attempts and outputs for unresolved cases.
-- "Verified" refers to the latest recorded observation and its adapter evidence.
SELECT DISTINCT m.member_id, m.planned_request_id AS request_id,
       old.attempt_id AS earlier_attempt_id, old.status AS earlier_status,
       produced.attempt_id AS producing_attempt_id, out.artifact_id,
       old.started_at AS earlier_started_at,
       produced.started_at AS producing_started_at, o.observed_at AS verified_at
FROM batch_members AS m
JOIN batch_observations AS o USING (batch_id, member_id)
JOIN processing_attempts AS old ON old.request_id = m.planned_request_id
JOIN processing_attempts AS produced ON produced.request_id = old.request_id
JOIN processing_outputs AS out ON out.attempt_id = produced.attempt_id AND out.role = 'ndvi'
WHERE m.batch_id = :batch_id
  AND o.observation_id = (
    SELECT MAX(x.observation_id) FROM batch_observations AS x
    WHERE x.batch_id = m.batch_id AND x.member_id = m.member_id
  )
  AND old.status IN ('failed', 'interrupted')
  AND produced.status = 'succeeded'
  AND julianday(produced.started_at) > julianday(old.started_at)
  AND o.state = 'complete'
  AND json_extract(o.evidence_json, '$.result.request_id') = m.planned_request_id
  AND json_extract(o.evidence_json, '$.result.attempt_id') = produced.attempt_id
  AND json_extract(o.evidence_json, '$.result.artifact_id') = out.artifact_id
  AND json_extract(o.evidence_json, '$.result.catalogue_link_verified') = 1
  AND json_extract(o.evidence_json, '$.result.grid_verified') = 1
  AND json_extract(o.evidence_json, '$.result.provenance_verified') = 1
ORDER BY m.member_id, old.started_at, old.attempt_id;

-- Q3. Which succeeded products have no location recorded as available?
-- Parameters: :batch_id.
-- Columns: member_id, request_id, attempt_id, artifact_id, last_location_check.
-- Empty: every succeeded NDVI has at least one location marked available.
-- Recorded availability may be stale; this query does not read or hash files.
-- Next: run refresh and inspect location_checks. A missing copy alone is insufficient.
SELECT DISTINCT m.member_id, a.request_id, a.attempt_id, out.artifact_id,
       (SELECT MAX(l.checked_at) FROM processing_artifact_locations AS l
        WHERE l.artifact_id = out.artifact_id) AS last_location_check
FROM batch_members AS m
JOIN processing_attempts AS a ON a.request_id = m.planned_request_id
JOIN processing_outputs AS out ON out.attempt_id = a.attempt_id AND out.role = 'ndvi'
WHERE m.batch_id = :batch_id AND a.status = 'succeeded'
  AND NOT EXISTS (
    SELECT 1 FROM processing_artifact_locations AS l
    WHERE l.artifact_id = out.artifact_id AND l.status = 'available'
  )
ORDER BY m.member_id, a.attempt_id;

-- Q4. Which members have an old latest observation, or none?
-- Parameters: :batch_id and :before, an explicit ISO 8601 UTC cutoff.
-- Columns: member_id, observation_id, state, observed_at, cutoff_utc.
-- Empty: every member has an observation at or after :before.
-- Next: run refresh; export a new report if current file evidence is needed.
-- observed_at is the batch observation time. Location checked_at and result
-- checked_at are separate verification times; generated_at is only report export.
SELECT m.member_id, o.observation_id, COALESCE(o.state, 'unobserved') AS state,
       o.observed_at, :before AS cutoff_utc
FROM batch_members AS m
LEFT JOIN batch_observations AS o
  ON o.batch_id = m.batch_id AND o.member_id = m.member_id
 AND o.observation_id = (
   SELECT MAX(x.observation_id) FROM batch_observations AS x
   WHERE x.batch_id = m.batch_id AND x.member_id = m.member_id
 )
WHERE m.batch_id = :batch_id
  AND (o.observation_id IS NULL OR julianday(o.observed_at) < julianday(:before))
ORDER BY m.member_id;

-- Q5. Which exact input role blocks a member in its latest observation?
-- Parameters: :batch_id.
-- Columns: member_id, state, missing_role, observed_at, reason.
-- Empty: no latest blocked observation lists a missing input. Global active work
-- can also block a member; inspect reason before inferring all inputs are usable.
-- Next: inspect artifact locations for that role, restore bytes, then run again.
SELECT m.member_id, o.state, missing.value AS missing_role, o.observed_at, o.reason
FROM batch_members AS m
JOIN batch_observations AS o USING (batch_id, member_id)
JOIN json_each(o.evidence_json, '$.context.missing_inputs') AS missing
WHERE m.batch_id = :batch_id AND o.state = 'blocked'
  AND o.observation_id = (
    SELECT MAX(x.observation_id) FROM batch_observations AS x
    WHERE x.batch_id = m.batch_id AND x.member_id = m.member_id
  )
ORDER BY m.member_id, missing.value;

-- Q6. Which attempts remain running, and have they published any catalogue output?
-- Parameters: :batch_id.
-- Columns: member_id, attempt_id, request_id, stage, temp_path, final_path, output_links.
-- Empty: no member request is recorded running; this does not prove host liveness.
-- Next: inspect paths and process/scheduler evidence; reconcile only after proving stop.
SELECT m.member_id, a.attempt_id, a.request_id, a.stage, a.temp_path, a.final_path,
       (SELECT COUNT(*) FROM processing_outputs AS out
        WHERE out.attempt_id = a.attempt_id) AS output_links
FROM batch_members AS m
JOIN processing_attempts AS a ON a.request_id = m.planned_request_id
WHERE m.batch_id = :batch_id AND a.status = 'running'
ORDER BY m.member_id, a.attempt_id;

