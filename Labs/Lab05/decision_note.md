# Delivery decision

On Saturday morning, five members have verified outputs and one is blocked by
a missing input. Delivery is due Monday afternoon. I would investigate now.

I would identify the blocked member, input role and registered locations, then
check a trusted alternate copy or the preserved fixture. If its size and SHA256
match, I would restore it and rerun the same manifest. The missing input has not
consumed an application attempt. I would verify the new output, export a new
report, and retain the blocked observation and recovery history.

The existing outputs were verified at their recorded times. Current availability
needs fresh checks. Cloud and shadow suitability remain unassessed, so I would
describe these as delivered NDVI products with nodata masking. Calling them
clear sky vegetation observations requires additional scientific QC.

If calibration may be wrong in published products, I would flag the affected
requests immediately and pause their use. I would compare the red/NIR scale and
offset with preserved source metadata and the frozen processing specification.
A confirmed calibration correction changes the scientific identity: create new
requests and a new manifest, publish corrected products, and document which
earlier products they supersede. Keep the original outputs and attempt history.

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
