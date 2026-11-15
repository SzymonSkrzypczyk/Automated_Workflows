-- Q1: Which expected members have no application attempt?
-- Params: :batch_id
-- Shows work that has not started
-- Empty: all members have an attempt, not necessarily a result
-- Next: check their states and outputs
SELECT m.member_id, m.planned_request_id, m.request_id
FROM batch_members AS m
WHERE m.batch_id = :batch_id
  AND NOT EXISTS (
    SELECT 1 FROM processing_attempts AS a
    WHERE a.request_id = m.planned_request_id AND a.status <> 'reused'
  )
ORDER BY m.member_id;

-- Q2: Which failed or interrupted requests later produced a verified result?
-- Params: :batch_id
-- Shows both attempts for each recovery
-- Empty: no recovery matches the latest recorded evidence
-- Next: refresh and inspect unresolved attempts
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

-- Q3: Which succeeded products have no available location?
-- Params: :batch_id
-- Uses recorded location status, which may be out of date
-- Empty: every succeeded product has a recorded available location
-- Next: refresh the location checks
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

-- Q4: Which members have an old observation or none?
-- Params: :batch_id, :before (UTC cutoff)
-- Compares the latest observation with the cutoff
-- Empty: every member has a recent observation
-- Next: refresh if newer checks are needed
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

-- Q5: Which inputs are blocking a member?
-- Params: :batch_id
-- Lists the missing input roles
-- Empty: no latest blocked observation lists a missing input
-- Next: inspect the blocked reason and input locations
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

-- Q6: Which attempts are still running?
-- Params: :batch_id
-- Shows their stage and any published outputs
-- Empty: no attempts are recorded as running
-- Next: check process evidence before reconciling
SELECT m.member_id, a.attempt_id, a.request_id, a.stage, a.temp_path, a.final_path,
       (SELECT COUNT(*) FROM processing_outputs AS out
        WHERE out.attempt_id = a.attempt_id) AS output_links
FROM batch_members AS m
JOIN processing_attempts AS a ON a.request_id = m.planned_request_id
WHERE m.batch_id = :batch_id AND a.status = 'running'
ORDER BY m.member_id, a.attempt_id;

