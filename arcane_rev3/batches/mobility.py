"""Rev2 bulk batch C: six real movement, rescue and stealth mechanics."""
from ..powers import power, apply, mod, compound
from .shared import active, periodic, effect, mobs, combined, cmd


def register(add):
    add("magician", 9, "Threshold Step",
        power("Threshold Step", "20% chance to prevent fall damage.",
              "origins:modify_damage_taken",
              damage_condition={"type":"origins:name","name":"fall"},
              condition={"type":"origins:chance","chance":0.20},
              modifier=mod(-1.0)),
        "partial", "Does not teleport two blocks horizontally or enforce 100t cooldown/shared fall-save flag")
    add("magician", 5, "Doorstep",
        active("Doorstep", "Secondary key: attempt to step eight blocks forward into clear air.",
               cmd("execute at @s positioned ^ ^ ^8 if block ~ ~ ~ minecraft:air "
                   "if block ~ ~1 ~ minecraft:air run tp @s ~ ~ ~"), 300),
        "partial", "Vertical pitch affects trajectory, and there is no collision-safe raycast/solid-ground check or destination fallback")
    add("magician", 4, "Sealed Room",
        power("Sealed Room", "On receiving fall damage, blind tagged hostile mobs within three blocks.",
              "origins:self_action_when_hit", cooldown=100,
              damage_condition={"type":"origins:name","name":"fall"},
              entity_action=effect(mobs(3),"blindness",20)),
        "partial", "Cannot link Blindness to a successful Threshold Step proc; enemy players omitted for ally safety")
    add("temperance", 1, "Wraith's Veil II",
        power("Wraith's Veil II", "While sneaking in dim light, become invisible.",
              "origins:invisibility", render_armor=True,
              condition={"type":"origins:and","conditions":[
                  {"type":"origins:sneaking"},
                  {"type":"origins:brightness","comparison":"<=","compare_to":0.6}]}),
        "partial", "Brightness <= 0.6 approximates light <=9, depends on dimension's ambient lighting")
    add("temperance", 5, "Incorporeal",
        active("Incorporeal", "Secondary key grants invisibility for 60t.",
               apply("invisibility",60), 1200),
        "partial", "Missing leaves/cobweb phasing for 60t; the invisibility effect works independently")
    add("hanged_man", 8, "Shadow Whisper",
        power("Shadow Whisper", "15% chance when hit to gain Resistance I for 40t.",
              "origins:self_action_when_hit", cooldown=1,
              entity_action={"type":"origins:chance","chance":0.15,
                             "action":apply("resistance",40)}),
        "partial", "30% reduction in hostile mob detection and triggering on mere targeting are not implemented")
    add("strength", 8, "Iron Fist",
        power("Iron Fist", "Add 2 points of melee damage while unarmed.",
              "origins:modify_damage_dealt",
              condition={"type":"origins:equipped_item","equipment_slot":"mainhand",
                         "item_condition":{"type":"origins:empty"}},
              modifier=mod(2.0,"addition")),
        "partial", "Does not suppress simultaneous Giant's Grip 18% attack bonus when both sequence kits are slotted")
