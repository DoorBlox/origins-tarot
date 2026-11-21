"""Six source-traced Hanged Man powers backed by the bounded Sin engine.

All six are deliberately PARTIAL. The actual 1.18.2 damage_taken stat
does not distinguish individual damage sources and Apoli cannot dynamically
damage arbitrary entities for exactly the stored scoreboard health amount.
The engine provides a real capped resource, decay, no-teammate AoE debuffs,
Trinity window and 60s capstone rather than a dummy passive placeholder.
"""
from ..powers import power, apply, mod, compound
from .shared import active, periodic, cmd


def sin_active():
    return {"type": "origins:scoreboard", "objective": "a_sin",
            "comparison": ">", "compare_to": 0}


def form_active():
    return {"type": "origins:scoreboard", "objective": "a_sin_form",
            "comparison": ">", "compare_to": 0}


def register(add):
    add("hanged_man", 9, "Sin-Bearing",
        periodic("Sin-Bearing",
                 "25% of measured damage-taken is retained as Sin (16HP cap); after 200t idle it dissipates. Low health releases a tiered safe hostile pulse.",
                 cmd("function tarot_arcane:sin/status"), 100,
                 condition=sin_active()),
        "partial",
        "A persistent sampled damage_taken scoreboard holds quarter-damage to a 16HP-equivalent cap; "
        "subsequent 200t idle decay and low-health burst use fixed wither/weakness tiers, not exact "
        "per-hit/per-damage-source Sin math, true dynamic stored HP damage, proportional 50% heal "
        "or direct enemy-player damage. Team-safe debuffs do not touch allies.")

    add("hanged_man", 5, "Burden Bearer",
        power("Burden Bearer",
              "Reduce damage taken by 10% while stored Sin is positive; gain 60t Regeneration after idle dissipation.",
              "origins:modify_damage_taken",
              condition=sin_active(), modifier=mod(-0.10)),
        "partial",
        "10% damage reduction only when resource>0 is native. Shared Sin engine also grants 60t Regen "
        "on its idle dissipation, but the underlying source's per-hit fraction, timing and incoming "
        "damage distinctions are approximated by a scoreboard sampling loop.")

    add("hanged_man", 3, "Trinity",
        power("Trinity",
              "Three received hit events in a 100t window grant Resistance II 60t and heal 2 hearts.",
              "origins:self_action_when_hit",
              cooldown=1,
              entity_action=cmd("function tarot_arcane:sin/trinity_hit")),
        "partial",
        "Counts any three received hit events within 100 online ticks rather than exactly three "
        "distinct damage sources; Resistance II 60t and Instant Health I 2 hearts are real, "
        "but critical incoming-hit attribution is not exposed by vanilla stats.")

    add("hanged_man", 1, "Sin Overflow",
        periodic("Sin Overflow",
                 "While Sin is present, show stored resource; the Sin engine upgrades the low-health burst to radius 10, Weakness II + Slowness II.",
                 cmd("function tarot_arcane:sin/status"), 120,
                 condition=sin_active()),
        "partial",
        "Shared low-health release uses radius-10 hostile wither and team-filtered Weakness II/Slowness II. "
        "It cannot inflict exact dynamic stored-Sin HP damage on players or heal precisely 75% of "
        "current Sin; regeneration is a conservative fixed-duration substitution.")

    decoy = cmd(
        'execute at @s positioned ^1 ^ ^ run summon minecraft:area_effect_cloud ~ ~ ~ '
        '{Duration:300,WaitTime:0,Radius:0.05f,Particle:"minecraft:smoke",'
        'Tags:["tarot_sin_minion_preview"]}'
    )
    add("hanged_man", 1, "Depraved Dependent",
        power("Depraved Dependent",
              "20% chance on a kill to summon one harmless 300t Sin smoke decoy (2400t cooldown).",
              "origins:self_action_on_kill", cooldown=2400,
              entity_action={"type": "origins:chance", "chance": 0.20,
                             "action": decoy}),
        "partial",
        "300t non-attacking self-expiring smoke cloud rather than a controllable AI minion; "
        "strict 2400t cooldown makes overlap impossible (max one vs handbook max two), "
        "all kills can trigger, no shared Sin payload, minion-target AI, or persistent ownership.")

    add("hanged_man", 0, "Weight of Sin Made Manifest",
        compound("Weight of Sin Made Manifest",
                 activate=active(
                     "Weight of Sin Made Manifest",
                     "Primary: 60s Sin form, capped resource raised and periodic hostile/explicit enemy-team debuffs; 14400t cooldown.",
                     cmd("function tarot_arcane:sin/form_start"),
                     14400, primary=True),
                 reduction=power(
                     "Weight of Sin Made Manifest: Resistance",
                     "Reduce damage taken by 75% while the Sin form is active.",
                     "origins:modify_damage_taken",
                     condition=form_active(), modifier=mod(-0.75)),
                 slow=power(
                     "Weight of Sin Made Manifest: Weight",
                     "Movement is 15% slower during the Sin form.",
                     "origins:conditioned_attribute",
                     tick_rate=20, condition=form_active(),
                     modifier={**mod(-0.15),
                               "attribute": "minecraft:generic.movement_speed"})),
        "partial",
        "Native primary-key 1200t active window / 14400t cooldown, -75% taken damage, "
        "-15% movement, 80t undead/hostile+enemy-team safe weakening and expiry burst "
        "are meaningful. Missing 100% exact Sin conversion, unbounded Sin, 15% stored "
        "Sin dynamic AoE damage, +5% Sin per melee hit, combat AI minions, kills rising, "
        "40-heart exact exploding final pulse and 50% proportional heal/excess absorption. "
        "Expiry is harmless to allies and has a bounded 80HP-equivalent Sin safety ceiling.")
