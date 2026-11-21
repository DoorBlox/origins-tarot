"""Hierophant Seq1: real fish-only dietary carveout, no removability loophole.

The matching pinned Sacred Dietary Vow is split into always-ban-nonfish
and conditionally-ban-fish subpowers by dietary_policy.py. When this upgrade
is trusted-source-granted, fish becomes edible and all nonfish meat still
remains banned even if the pinned power's fish subcondition is disabled.
Normal Rev3 Sequence1 has Resonance rather than player-slotted individual
Seq1 powers, so this native implementation remains PARTIAL until accepted
in a legitimate future unlock or explicit operator development grant.
"""
from ..powers import power


def register(add):
    add("hierophant", 1, "Dietary Expansion",
        power(
            "Dietary Expansion",
            "When this upgrade is source-granted, fish is permitted; nonfish meat stays prohibited.",
            "origins:prevent_item_use",
            item_condition={
                "type": "origins:ingredient",
                "ingredient": {"tag": "tarot:nonfish_meat"},
            },
        ),
        "partial",
        "Actual fish carveout requires the operator-controlled Arcane slot source "
        "and a still-pinned original Sacred Dietary Vow: nonfish meat remains banned "
        "through its unconditional native subpower. Rev3 normal Seq1 Resonance does "
        "not equip individual Seq1 kits, so this opt-in Seq1 source grant is not "
        "part of normal progression or game-runtime accepted yet.")
