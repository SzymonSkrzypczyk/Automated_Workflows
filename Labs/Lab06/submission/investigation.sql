-- Compare the original and stricter assessments for completed attempts
SELECT a.attempt_id, a.status, q.assessment_id, q.outcome,
       json_extract(q.policy_json, '$.minimum_valid_fraction') AS minimum_valid_fraction,
       json_extract(q.metrics_json, '$.valid_fraction') AS valid_fraction
FROM processing_attempts AS a
JOIN scientific_qc_assessments AS q USING (attempt_id)
ORDER BY a.attempt_id, q.assessment_id;

-- Find requests with multiple named product outputs
SELECT a.request_id, a.attempt_id, group_concat(o.role) AS roles
FROM processing_attempts AS a
JOIN processing_outputs AS o USING (attempt_id)
GROUP BY a.request_id, a.attempt_id
HAVING count(*) > 1;
