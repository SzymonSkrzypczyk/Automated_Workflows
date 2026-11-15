"""Boundary checks beyond the supplied four feedback groups."""
import copy
import sqlite3
import unittest
from pathlib import Path

import batch_repairs as repairs
import batch_store
import check_lab05


class SolutionChecks(unittest.TestCase):
    def test_supplied_contracts(self):
        for name, check in check_lab05.CHECKS.items():
            with self.subTest(group=name):
                check()

    def test_missing_verification_fields_never_pass(self):
        member = {'request_id': 'request-one'}
        evidence = dict(request_id='request-one', attempt_id='attempt-one',
                        artifact_id='artifact-one', size_bytes=5, actual_size_bytes=5,
                        sha256='a' * 64, actual_sha256='a' * 64,
                        catalogue_link_verified=True, grid_verified=True, provenance_verified=True)
        self.assertTrue(repairs.verify_result(member, evidence))
        for key in evidence:
            changed = evidence.copy()
            del changed[key]
            with self.subTest(missing=key):
                self.assertFalse(repairs.verify_result(member, changed))
        for key, value in [('size_bytes', 0), ('size_bytes', True),
                           ('actual_size_bytes', True), ('sha256', 'z' * 64),
                           ('attempt_id', ' '), ('artifact_id', ''),
                           ('grid_verified', 'true'), ('provenance_verified', 1)]:
            with self.subTest(key=key, value=value):
                self.assertFalse(repairs.verify_result(member, {**evidence, key: value}))

    def test_state_priority_and_persistent_budget(self):
        base = dict(active_attempt=None, verified_result=None, missing_inputs=[],
                    validation_error=None, attempts_used=1, max_attempts=2,
                    last_attempt={'status': 'interrupted'})
        self.assertEqual(repairs.classify_member(base)['state'], 'ready')
        self.assertEqual(repairs.classify_member({**base, 'attempts_used': 2})['state'], 'failed')
        complete = {**base, 'verified_result': {'artifact_id': 'out'},
                    'attempts_used': 2, 'missing_inputs': ['red'], 'validation_error': 'old'}
        self.assertEqual(repairs.classify_member(complete)['state'], 'complete')
        self.assertEqual(repairs.classify_member({**complete, 'active_attempt': {'attempt_id': 'a'}})['state'], 'unresolved')

    def test_summary_empty_duplicates_order_and_unobserved(self):
        self.assertEqual(repairs.summarize_batch([])['expected'], 0)
        rows = [dict(member_id='z', observation_id=-1, state=None),
                dict(member_id='b', observation_id=2, state='failed'),
                dict(member_id='a', observation_id=3, state='complete'),
                dict(member_id='b', observation_id=4, state='complete')]
        original = copy.deepcopy(rows)
        result = repairs.summarize_batch(rows + list(reversed(rows)))
        self.assertEqual(result, repairs.summarize_batch(list(reversed(rows))))
        self.assertEqual(result['expected'], 3)
        self.assertEqual(sum(result['counts'].values()), 3)
        self.assertEqual(result['members']['complete'], ['a', 'b'])
        self.assertEqual(result['members']['unobserved'], ['z'])
        self.assertEqual(rows, original)

    def test_schema_rejects_nulls_bad_evidence_and_orphans(self):
        with batch_store.connect(':memory:') as c:
            for name in ('lab02_base_schema.sql', 'lab03_reference_schema.sql', 'lab04_processing_schema.sql'):
                c.executescript((Path(__file__).parent / 'support' / name).read_text())
            batch_store.initialize(c)
            self.assertEqual(c.execute('PRAGMA foreign_keys').fetchone()[0], 1)
            c.execute("INSERT INTO batches VALUES ('b','{}','2026-11-12T00:00:00Z')")
            c.execute("INSERT INTO batch_members VALUES ('b','m','planned',NULL,'{}')")
            invalid = ["INSERT INTO batches VALUES (NULL,'{}','now')",
                       "INSERT INTO batch_members VALUES ('b',NULL,'another',NULL,'{}')",
                       "INSERT INTO batch_members VALUES ('b','other','another',NULL,'invalid')",
                       "INSERT INTO batch_members VALUES ('b','other','absent','absent','{}')"]
            for sql in invalid:
                with self.subTest(sql=sql), self.assertRaises(sqlite3.IntegrityError):
                    c.execute(sql)
            sql = ('INSERT INTO batch_observations(batch_id,member_id,observed_at,state,reason,attempt_id,evidence_json) '
                   'VALUES (?,?,?,?,?,?,?)')
            for reason, attempt, evidence in [(' ', None, '{}'), ('why', 'absent', '{}'), ('why', None, 'bad')]:
                with self.subTest(reason=reason, attempt=attempt, evidence=evidence), self.assertRaises(sqlite3.IntegrityError):
                    c.execute(sql, ('b', 'm', 'now', 'ready', reason, attempt, evidence))
            c.execute(sql, ('b', 'm', 'now', 'ready', 'why', None, '{}'))
            first = c.execute('SELECT MAX(observation_id) FROM batch_observations').fetchone()[0]
            c.execute('DELETE FROM batch_observations')
            c.execute(sql, ('b', 'm', 'now', 'ready', 'why', None, '{}'))
            self.assertGreater(c.execute('SELECT MAX(observation_id) FROM batch_observations').fetchone()[0], first)
            indexes = c.execute('PRAGMA index_list(batch_observations)').fetchall()
            columns = [[r[2] for r in c.execute('PRAGMA index_info(' + idx[1] + ')')] for idx in indexes]
            self.assertIn(['batch_id', 'member_id', 'observation_id'], columns)


if __name__ == '__main__':
    unittest.main()
