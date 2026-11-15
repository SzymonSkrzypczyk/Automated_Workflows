"""Decisions based on the evidence assembled by the supplied job adapter."""


def classify_member(context):
    if context['active_attempt']:
        return {'state': 'unresolved', 'reason': 'Execution is still recorded as active'}
    if context['verified_result']:
        return {'state': 'complete', 'reason': 'Output bytes, grid and provenance verified'}
    if context['validation_error']:
        return {'state': 'failed', 'reason': 'Validation failed: ' + context['validation_error']}
    if context['missing_inputs']:
        return {'state': 'blocked', 'reason': 'Required input unavailable: ' + ', '.join(context['missing_inputs'])}
    if context['attempts_used'] >= context['max_attempts']:
        return {'state': 'failed', 'reason': 'Attempt budget exhausted across catalogue history'}
    last = context['last_attempt']
    if last and last['status'] == 'failed':
        return {'state': 'failed', 'reason': 'Application failed; investigate before another attempt'}
    return {'state': 'ready', 'reason': 'Inputs verified and attempt budget permits execution'}


def verify_result(member, evidence):
    request_id = member.get('request_id')
    if not isinstance(request_id, str) or not request_id.strip() or evidence.get('request_id') != request_id:
        return False
    for key in ('attempt_id', 'artifact_id'):
        if not isinstance(evidence.get(key), str) or not evidence[key].strip():
            return False
    if not all(evidence.get(key) is True for key in
               ('catalogue_link_verified', 'grid_verified', 'provenance_verified')):
        return False
    size = evidence.get('size_bytes')
    actual_size = evidence.get('actual_size_bytes')
    if type(size) is not int or size <= 0 or type(actual_size) is not int or actual_size != size:
        return False
    checksum = evidence.get('sha256')
    return (isinstance(checksum, str) and len(checksum) == 64
            and all(c in '0123456789abcdef' for c in checksum)
            and evidence.get('actual_sha256') == checksum)


def summarize_batch(rows):
    counts = {s: 0 for s in ('ready', 'complete', 'blocked', 'unresolved', 'failed', 'unobserved')}
    members = {s: [] for s in counts}
    latest = {}
    for row in rows:
        member_id = row['member_id']
        if member_id not in latest or row['observation_id'] > latest[member_id]['observation_id']:
            latest[member_id] = row
    for member_id, row in sorted(latest.items()):
        state = row['state'] if row['state'] is not None else 'unobserved'
        counts[state] += 1
        members[state].append(member_id)
    return {'expected': len(latest), 'counts': counts, 'members': members}

