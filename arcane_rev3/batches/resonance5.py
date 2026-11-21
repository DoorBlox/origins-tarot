"""Small Resonance wave 5: six more meaningfully partial power effects.

No ability in this module claims to emulate scripted Sin, fake decoys,
persistent brew state, or cross-team health disclosure. The unsupported
submechanics stay explicit in the manifest and Sequence 1 remains ungranted.
"""
from ..powers import apply, power
from ..team_policy import ally_effect
from .shared import active, combined, effect, mobs, periodic


HOSTILE = {"type": "origins:in_tag", "tag": "tarot:hostile"}


def register(add):
    add("paper_martyr", 8, "Shadow Step",
        power("Shadow Step", "25% on hostile damage to gain Invisibility briefly.",
              "origins:self_action_when_hit", cooldown=400,
              damage_condition={"type": "origins:attacker",
                                "entity_condition": HOSTILE},
              entity_action={"type": "origins:chance", "chance": 0.25,
                             "action": combined(apply("invisibility", 40),
                                                apply("speed", 40))}),
        "partial", "No decoy armor stand, tagged Sin payload, 2-block 2-damage detonation or damage-independent trigger; enemy players omitted")
    add("paper_martyr", 6, "Borrowed Sacrifice",
        power("Borrowed Sacrifice", "After hostile mob damage, retaliate for three health points.",
              "origins:attacker_action_when_hit", cooldown=2400,
              entity_action={"type": "origins:damage", "amount": 3,
                             "source": {"name": "generic"}}),
        "partial", "No Borrowed Face disguise synchronization, three-Sin stored decoy or on-disguise-break retaliation; excludes enemy players")
    add("marked_verdict", 6, "Silent Witness",
        power("Silent Witness", "Right-click tagged hostile mob to highlight it for 600 ticks.",
              "origins:action_on_entity_use",
              bientity_condition={"type": "origins:target_condition",
                                  "condition": HOSTILE},
              bientity_action={"type": "origins:target_action",
                               "action": apply("glowing", 600)}),
        "partial", "Does not reveal target exact HP in a UI or add Calming Presence; no enemy-player targeting or cooldown")
    add("impossible_fist", 6, "Recorded Dawnlight",
        active("Recorded Dawnlight", "Crouch + secondary gives 200t Night Vision.",
               apply("night_vision", 200), 1200, crouch=True),
        "partial", "No Recorded Step location history/return and no actual radius-three light level 8 in the world")
    add("walking_sanctuary", 3, "Ghost Blessing",
        periodic("Ghost Blessing", "While invisible, refresh self Regeneration I.",
                 combined(apply("regeneration", 80),
                          ally_effect("regeneration", 80, 8)), 80,
                 condition={"type": "origins:invisible"}),
        "partial", "Invisibility approximates phasing; same-team allies within 8 blocks receive Regeneration I during the effect, but arbitrary unlisted players never qualify")
    add("eclipse", 6, "Witness Brew",
        active("Witness Brew", "Secondary highlights nearest tagged hostile mob for 600 ticks.",
               effect(mobs(10, nearest=True), "glowing", 600), 1200),
        "partial", "The source requires Witness status for 1200t and instant brew with independent 6000t cooldown; highlighting for 600t neither reads health nor brews a potion")
