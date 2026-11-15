# Delivery decision

I would investigate on Saturday
Five outputs are verified and one input is missing
I would check the registered locations and restore a trusted copy with a matching checksum
Then rerun the batch and verify the result
The blocked request has used no attempt, so I would keep its earlier observation

The file checks may be out of date
Cloud and shadow suitability are still unassessed
I would call these NDVI products with nodata masking

If calibration may be wrong, I would flag the affected products and pause their use
Then check the red and NIR scale and offset against the source metadata and frozen specification
A confirmed correction needs new requests and a new manifest
I would keep the old results and their history

# Proposed report views

These sketches show the missing input case before recovery
The saved report has the actual IDs and timestamps

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

The counts link to member lists
A seperate table shows attempts, so retries do not inflate the result count

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

The blocked member has no output evidence or application attempt
Process liveness, cloud and shadow fractions, calibration review, delivery owner and delivery forecast are unavailable
These would need more evidence before being shown
