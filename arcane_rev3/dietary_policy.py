"""Fail-closed fish-only exception to Hierophant's permanently pinned identity.

The Sacred Dietary Vow is an immutable native Origin identity and must NOT
become freely removable as slot ownership changes. Split its original meat
ban into two native subpowers: the nonfish ban is unconditional forever;
the fish ban is active unless the Arcane slot source specifically grants
Dietary Expansion. Revoking the upgrade restores the original fish ban.
No commands, inventory mutations, arbitrary item tags or admin permissions.
"""
from .upgrade_policy import SLOT_SOURCE


ORIGINAL_VOW = "tarot:hierophant/9_sacred_dietary_vow"
UPGRADE = "tarot:hierophant/1_dietary_expansion"


def _item_condition(tag):
    if tag not in ("tarot:fish", "tarot:nonfish_meat"):
        raise ValueError("Dietary category must be a fixed, audited tag")
    return {"type": "origins:ingredient", "ingredient": {"tag": tag}}


def apply_dietary_expansion(compiled):
    """Move only the *fish* prohibition behind a trusted native power gate.

    Original remains an innate Origin power. Disallowed nonfish items stay
    forbidden irrespective of source grants or manual admin revocation.
    """
    if ORIGINAL_VOW not in compiled or UPGRADE not in compiled:
        raise ValueError("Both original Vow and Dietary Expansion must be sourced")

    original = compiled[ORIGINAL_VOW]
    upgrade = compiled[UPGRADE]
    if upgrade.get("type") != "origins:prevent_item_use" or (
        upgrade.get("item_condition") != _item_condition("tarot:nonfish_meat")
    ):
        raise ValueError("Dietary upgrade must separately enforce nonfish meat")

    if original.get("type") == "origins:multiple":
        # Only accept the exact intended, already-expanded shape. Avoid a
        # second mutation on incremental builds or silent incompatible mods.
        if (original.get("nonfish", {}).get("item_condition")
                != _item_condition("tarot:nonfish_meat")
                or original.get("fish", {}).get("item_condition")
                != _item_condition("tarot:fish")):
            raise ValueError("Existing dietary partition differs from policy")
        return

    if original.get("type") != "origins:prevent_item_use" or (
        original.get("item_condition")
        != {"type": "origins:ingredient",
            "ingredient": {"tag": "tarot:meat"}}
    ):
        raise ValueError("Pinned Vow is not the exact original meat ban")

    original.pop("item_condition")
    original["type"] = "origins:multiple"
    original["nonfish"] = {
        "type": "origins:prevent_item_use",
        "item_condition": _item_condition("tarot:nonfish_meat"),
    }
    original["fish"] = {
        "type": "origins:prevent_item_use",
        "item_condition": _item_condition("tarot:fish"),
        "condition": {
            "type": "origins:power",
            "power": UPGRADE,
            "source": SLOT_SOURCE,
            "inverted": True,
        },
    }
