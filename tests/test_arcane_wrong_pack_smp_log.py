"""Latest Fabric log must never be treated as an Arcane-successful SMP boot."""
import unittest

from scripts.arcane_server_evidence_audit import audit
from tests.test_arcane_server_evidence_audit import BASE


class SMPLogRegressions(unittest.TestCase):
    def test_missing_arcane_and_legacy_auto_loaded_is_blocker(self):
        log = (
            BASE +
            "[05:23:15] [main/WARN]: Missing data pack file/Arcane_Rev3_22_Origins_ONLY_DEV_1.18.2.zip\n"
            "[05:23:15] [main/INFO]: Found new data pack file/The_Tarot_Club_22_Arcana_Only_1.18.2.zip, loading it automatically\n"
            "[05:23:19] [Worker/ERROR]: There was a problem reading power file tarot:empress/extra_1 (skipping): Error reading data field at render_armor: JSON requires field: render_armor\n"
            "[05:23:19] [Worker/ERROR]: Origin \"tarot:empress\" contained unregistered power: \"tarot:empress/extra_1\"\n"
            "Done (11.540s)! For help, type help\n"
            "[05:23:37] [Server thread/ERROR]: Error while reading power holder data: Could not get power type from id 'tarot:moon/9_sanguine_sight_vision', as it was not registered!\n"
        )
        report = audit(log, intentional_offline_mode=True)
        findings = {x["id"] for x in report["alerts"]}
        for issue in ("arcane_datapack_missing", "legacy_tarot_pack_loaded",
                      "tarot_power_decoder_error", "tarot_unregistered_power",
                      "saved_power_missing"):
            self.assertIn(issue, findings)
        self.assertFalse(report["ready_for_arcane_load_test"])
        self.assertFalse(report["log_contains_arcane_datapack_proof"])
        self.assertFalse(report["arcane_gameplay_verified"])

    def test_optional_remote_mod_errors_not_mistaken_for_tarot_errors(self):
        log = (BASE +
               "Couldn't get patreons from https://example.invalid/data\n"
               "java.net.ConnectException\n"
               "Done (11.540s)! For help, type help\n")
        findings = {x["id"] for x in audit(log)["alerts"]}
        self.assertNotIn("tarot_power_decoder_error", findings)
        self.assertNotIn("arcane_datapack_missing", findings)

    def test_clean_legacy_pack_is_not_evidence_of_arcane(self):
        report = audit(BASE +
            "Found new data pack file/The_Tarot_Club_22_Arcana_Only_1.18.2.zip, loading it automatically\n"
            "Done (11.540s)!")
        self.assertFalse(report["log_contains_arcane_datapack_proof"])
        self.assertFalse(report["ready_for_arcane_load_test"])


if __name__ == "__main__":
    unittest.main()
