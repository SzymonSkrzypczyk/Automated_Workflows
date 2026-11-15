# Delivery decision

I would investigate on Saturday. Five outputs are verified and one request is blocked by a missing input. I would check its registered locations, restore a trusted copy with the matching checksum, rerun the batch and verify the result. The blocked request has used no attempt, and I would keep its earlier observation.

The file checks may be out of date, and cloud and shadow suitability are unassessed. I would describe the outputs as NDVI products with nodata masking, not clear sky vegetation observations.

If calibration may be wrong, I would flag the affected products and pause their use. I would check the red and NIR scale and offset against the source metadata and frozen specification. A confirmed correction needs new requests and a new manifest. I would identify the superseded products and keep their history.

# Proposed report views

These sketches use fields already present in the supplied report. Values below
describe the missing-input case before recovery. The saved report contains the
actual IDs and timestamps.

```text
Batch overview
Batch: batch_id                Membership: membership_sha256
Report exported: generated_at  Expected: 6
Complete: 5 -> member IDs      Blocked: 1 -> member ID
Ready / unresolved / failed / unobserved: 0 each
Application attempts: 5        Producing attempts: 5
Each member: state | reason | observed_at | age_seconds | next_check
Cloud suitability: unassessed  Mask policy: nodata_only
Snapshot: catalogue.sqlite and SHA256
```

Counts link to the exact member list. A separate table lists all historical
attempts, so retries cannot inflate the expected or completed member count.

```text
Member detail
member_id | planned_request_id | registered request_id
latest observation_id | state | reason | observed_at
context.missing_inputs: [red]
input role | artifact_id | expected size/SHA256
location_checks: path | status | checked_at
attempt_id | status | stage | started_at | finished_at | error_code
output artifact_id | measured size/SHA256 | result.checked_at
grid/provenance/catalogue verification flags
next_check
```

For the blocked member, output evidence and an application attempt are absent.
The detail view must show that absence. Process liveness, cloud/shadow fractions,
calibration review status, a delivery owner and a measured delivery forecast are
unavailable fields. A future interface would need new evidence to display them.
