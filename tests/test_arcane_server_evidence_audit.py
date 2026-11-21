"""Read-only log/config audit regressions; synthetic evidence, no private logs."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.arcane_server_evidence_audit import audit, extract_versions, read_json5_subset


MODS = '\n'.join(' - ' + key + ' ' + version for key, version in {
    'minecraft': '1.18.2', 'fabricloader': '0.20.1', 'origins': '1.4.1',
    'fabric-api': '0.77.0+1.18.2', 'fabric-permissions-api-v0': '0.3.1',
    'luckperms': '5.3.86', 'remorphed': '4.2', 'skinshifter': '1.3',
    'pehkui': '3.8.3', 'extrakeybinds': '0.5.0',
    'commandaliases': '1.0.1', 'craftedcore': '5.8.1',
    'walkers': '5.8.1',
}.items())
BASE = 'Loading 138 mods:\n' + MODS + '\nSpongePowered MIXIN Subsystem Version=0.8.7\n'


class ServerEvidenceAuditTests(unittest.TestCase):
    def test_plain_and_markdown_logs_extract_same_mod_versions(self):
        plain = extract_versions(BASE)
        markdown = extract_versions('**[02:00:00] [main/INFO]:** Loading 138 mods:\n'
            + '\n'.join('&#x9;\\- ' + line.strip()[2:] + '&#x20;'
                        for line in MODS.splitlines())
            + '\n**[02:00:01] [main/INFO]:** SpongePowered MIXIN Subsystem\n')
        self.assertEqual(plain, markdown)
        self.assertEqual(markdown['fabric-permissions-api-v0'], '0.3.1')
        self.assertEqual(markdown['skinshifter'], '1.3')

    def test_baseline_start_does_not_equal_arcane_acceptance(self):
        report = audit(BASE + 'Finished loading powers from data files. Registry contains 76 powers.\n'
                       + 'Finished loading origins from data files. Registry contains 11 origins.\n'
                       + 'Done (68.464s)! For help, type "help"')
        self.assertTrue(report['ready_for_arcane_load_test'])
        self.assertFalse(report['arcane_gameplay_verified'])
        self.assertFalse(report['log_contains_arcane_datapack_proof'])
        self.assertEqual(report['baseline_origins_registry'], {'powers': 76, 'origins': 11})
        self.assertEqual(report['required_missing_from_log'], [])

    def test_out_of_memory_and_offline_mode_block_smoke_test(self):
        log = BASE + 'Done (68.464s)!\n' \
              + 'Couldn\'t load structure terralith:spire: java.lang.OutOfMemoryError: Java heap space\n' \
              + '**** SERVER IS RUNNING IN OFFLINE/INSECURE MODE!\n'
        result = audit(log)
        self.assertTrue(result['startup_completed'])
        self.assertFalse(result['ready_for_arcane_load_test'])
        self.assertEqual({x['id'] for x in result['alerts']},
                         {'heap_oom', 'unauthenticated_server'})

    def test_owner_acknowledged_dev_exceptions_do_not_claim_security_or_gameplay(self):
        log = (BASE + 'Done (68.464s)!\n'
               + "Couldn't load structure terralith:spire: java.lang.OutOfMemoryError: Java heap space\n"
               + '**** SERVER IS RUNNING IN OFFLINE/INSECURE MODE!\n')
        # Default baseline remains fail-closed.
        normal = audit(log)
        self.assertFalse(normal['ready_for_arcane_load_test'])
        self.assertEqual(normal['owner_acknowledged_conditions'],
                         {'first_worldgen_heap_oom': False,
                          'intentional_offline_mode': False})
        for args in ({'acknowledge_worldgen_oom': True},
                     {'intentional_offline_mode': True}):
            with self.subTest(args=args):
                self.assertFalse(audit(log, **args)['ready_for_arcane_load_test'])
        accepted = audit(log, acknowledge_worldgen_oom=True,
                         intentional_offline_mode=True)
        self.assertTrue(accepted['ready_for_arcane_load_test'])
        self.assertFalse(accepted['arcane_gameplay_verified'])
        self.assertFalse(accepted['log_contains_arcane_datapack_proof'])
        self.assertEqual(accepted['owner_acknowledged_conditions'],
                         {'first_worldgen_heap_oom': True,
                          'intentional_offline_mode': True})
        warnings = {a['id']: a for a in accepted['alerts']}
        self.assertEqual(warnings['heap_oom']['severity'], 'warning')
        self.assertEqual(warnings['unauthenticated_server']['severity'], 'warning')
        self.assertIn('spoofable', warnings['unauthenticated_server']['finding'])
        self.assertIn('repeated OOM', warnings['heap_oom']['finding'])

    def test_acknowledgements_do_not_override_missing_mods_or_failed_startup(self):
        flags = {'acknowledge_worldgen_oom': True,
                 'intentional_offline_mode': True}
        log = ('Loading 1 mods:\n - origins 1.4.1\nSpongePowered MIXIN\n'
               'Done (1s)!\nOutOfMemoryError\nOFFLINE/INSECURE MODE')
        report = audit(log, **flags)
        self.assertFalse(report['ready_for_arcane_load_test'])
        self.assertIn('fabric-permissions-api-v0', report['required_missing_from_log'])
        self.assertFalse(audit(BASE + '\nOutOfMemoryError\nOFFLINE/INSECURE MODE',
                               **flags)['ready_for_arcane_load_test'])
        self.assertFalse(audit(BASE + '\nOutOfMemoryError\nOFFLINE/INSECURE MODE',
                               **flags)['owner_acknowledged_conditions']['first_worldgen_heap_oom'])

    def test_legacy_config_does_not_claim_modern_permissions(self):
        report = audit(BASE + 'Done (1.1s)!', remorphed={
            'creativeUnlockAll': True, 'killToUnlock': 1,
            'loadMenuAsynchronous': True,
        }, skinshifter={'changeName': True, 'baseCommandOPLevel': 2,
                        'selfCommandOPLevel': 0})
        alerts = {x['id'] for x in report['alerts']}
        self.assertIn('remorphed_legacy_permissions', alerts)
        self.assertIn('public_self_disguise', alerts)
        self.assertIn('creative_morph_all', alerts)
        self.assertNotIn('skinshifter_admin_gate', alerts)

    def test_read_json5_subset_accepts_comments_but_not_code(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'remorphed.json5'
            path.write_text('// a config comment\n{"killToUnlock": 1, "autoTransform": false}\n')
            self.assertEqual(read_json5_subset(path),
                             {'killToUnlock': 1, 'autoTransform': False})
            path.write_text('{"killToUnlock": __import__("os").system("id")}')
            with self.assertRaises(json.JSONDecodeError):
                read_json5_subset(path)

    def test_missing_mods_detected_without_guessing_jar_versions(self):
        report = audit('Loading 1 mods:\n - origins 1.4.1\nSpongePowered MIXIN\nDone (1s)!')
        self.assertIn('fabric-permissions-api-v0', report['required_missing_from_log'])
        self.assertFalse(report['ready_for_arcane_load_test'])
        self.assertTrue(any(x['id'] == 'required_mods_not_in_log' for x in report['alerts']))
        self.assertFalse(report['arcane_gameplay_verified'])


if __name__ == '__main__':
    unittest.main()
