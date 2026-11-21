"""Source-traced non-stacking Rev2 upgrades for Rev3's selectable kits.

The old power remains granted by its sequence slot, but its effect is inactive
while the replacement has been granted from the Arcane slot source. This uses
the Origins/Apoli 1.4.1 "origins:power" entity condition, not tick-time
scoreboard polling or a permanent revoke. Unswitching the upgrade restores
the original, including after relog, refresh, repair and admin pause/resume.

Only fully superseded single-effect bonuses belong here. Do NOT suppress an
entire origins:multiple kit (e.g. Law's Weight keeps +2 armor), any innate
identity drawback, or Nightwatch while its light/night upgrade scope differs.
Real Minecraft 1.18.2 runtime acceptance is still required.
"""

SLOT_SOURCE = "tarot_arcane:slot_grants"

# (original, replacement) — exact IDs from the Rev2 catalog; Rev3 permits
# equipping both sequence kits simultaneously. All eight are one-effect
# powers whose source-defined upgrade replaces, rather than adds, that effect.
REPLACEMENTS = (
    ("tarot:moon/9_blood_s_renewal", "tarot:moon/4_shaman"),
    ("tarot:sun/9_unshadowed", "tarot:sun/4_unshadowed_ii"),
    ("tarot:world/9_cold_precision", "tarot:world/1_cold_precision_ii"),
    ("tarot:tower/9_ruin_proof", "tarot:tower/1_ruin_proof_ii"),
    ("tarot:wheel_of_fortune/9_fate_intervenes", "tarot:wheel_of_fortune/4_misfortune"),
    ("tarot:devil/9_desperate_malice", "tarot:devil/4_demon_form"),
    ("tarot:empress/9_witch_s_venom", "tarot:empress/5_plague_touch"),
    ("tarot:hierophant/9_sanctified_ground", "tarot:hierophant/4_sanctified_ground_ii"),
    # Both are the same book/potion-held periodic healing niche; avoid
    # stacking doubled regeneration pulses when Seq1 upgrades are slotted.
    ("tarot:moon/9_pharmacist", "tarot:moon/1_pharmacist_ii"),
)


def apply_replacement_conditions(compiled):
    """Inactivate an original bonus only while its slotted upgrade is owned.

    Idempotence matters if the compiler is ever reused by an incremental build.
    The power-source restriction prevents unrelated Origins/other mods granting
    a power of the same ID from changing the Tarot slot's lower-tier effect.
    """
    if len({old for old, _ in REPLACEMENTS}) != len(REPLACEMENTS):
        raise ValueError("duplicate original in upgrade replacement policy")
    for old, new in REPLACEMENTS:
        if old not in compiled or new not in compiled:
            raise ValueError(f"missing concrete upgrade pair: {old} -> {new}")
        original = compiled[old]
        if original["type"] == "origins:multiple":
            raise ValueError(f"cannot suppress mixed-benefit origin power: {old}")
        gate = {
            "type": "origins:power",
            "power": new,
            "source": SLOT_SOURCE,
            "inverted": True,
        }
        previous = original.get("condition")
        if previous == gate or (
            isinstance(previous, dict)
            and previous.get("type") == "origins:and"
            and previous.get("conditions", [])[-1:] == [gate]
        ):
            continue
        original["condition"] = (
            {"type": "origins:and", "conditions": [previous, gate]}
            if previous else gate
        )
