"""Static compatibility gate against official Origins/Apoli 1.4.1 power types.

Sources: https://origins.readthedocs.io/en/1.4.1/types/power_types/
         https://origins.readthedocs.io/en/1.4.1/types/power_types/active_self/
         https://origins.readthedocs.io/en/1.4.1/types/power_types/action_on_entity_use/

This catches unknown or newer-only power identifiers and missing common fields.
It does NOT replace an actual Minecraft 1.18.2 runtime acceptance test.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from arcane_rev3.full_build import build

OFFICIAL_POWER_TYPES=set("""
attribute_modify_transfer attribute burn climbing conditioned_attribute
conditioned_restrict_armor cooldown creative_flight damage_over_time
disable_regen effect_immunity elytra_flight entity_glow entity_group exhaust
fire_immunity fire_projectile freeze ignore_water inventory invisibility
invulnerability item_on_item keep_inventory launch lava_vision model_color
multiple night_vision overlay particle phasing recipe resource restrict_armor
self_glow shader shaking simple stacking_status_effect starting_equipment
status_bar_texture swimming toggle_night_vision toggle tooltip walk_on_fluid
action_on_being_used action_on_block_break action_on_block_use
action_on_callback action_on_entity_use action_on_hit action_on_item_use
action_on_land action_on_wake_up action_over_time action_when_damage_taken
action_when_hit active_self attacker_action_when_hit self_action_on_hit
self_action_on_kill self_action_when_hit target_action_on_hit
modify_air_speed modify_block_render modify_break_speed modify_camera_submersion
modify_crafting modify_damage_dealt modify_damage_taken modify_exhaustion
modify_falling modify_fluid_render modify_food modify_harvest modify_jump
modify_lava_speed modify_player_spawn modify_projectile_damage
modify_slipperiness modify_status_effect_amplifier modify_status_effect_duration
modify_swim_speed modify_xp_gain prevent_being_used prevent_block_selection
prevent_block_use prevent_death prevent_elytra_flight prevent_entity_collision
prevent_entity_render prevent_entity_use prevent_feature_render
prevent_game_event prevent_item_use prevent_sleep
""".split())
UNAVAILABLE_IN_141={
    "origins:modify_healing", "origins:modify_insomnia_ticks",
    "origins:prevent_block_place", "origins:modify_enchantment_level",
    "origins:action_on_block_place", "origins:game_event_listener",
}
MUTATING_PLAYER_COMMANDS=("op ","deop ","ban ","whitelist ","stop ","kick ")
OFFENSIVE=("wither","slowness","weakness","poison","blindness","mining_fatigue",
           "instant_damage","hunger")


def leaf_power_nodes(power,place):
    """Each nested child of origins:multiple is also a real power type."""
    yield place,power
    if power.get("type")=="origins:multiple":
        for key,val in power.items():
            if isinstance(val,dict) and "type" in val and
               key not in ("condition","entity_action","damage_condition",
                           "item_condition","block_condition"):
                yield from leaf_power_nodes(val,place+"."+key)


def subobjects(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values():yield from subobjects(v)
    elif isinstance(obj,list):
        for v in obj:yield from subobjects(v)


class Origins141CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
        cls.pack=ZipFile(cls.artifacts["only"])
    @classmethod
    def tearDownClass(cls):
        cls.pack.close()
        cls.tmp.cleanup()

    def test_every_compiled_power_type_exists_in_version_141(self):
        self.assertEqual(len(self.pack.namelist())>300,True)
        validated=set()
        for path in self.pack.namelist():
            if not (path.startswith("data/tarot/powers/") and path.endswith(".json")):
                continue
            power=json.loads(self.pack.read(path))
            for position,item in leaf_power_nodes(power,path):
                name=item.get("type")
                self.assertIsInstance(name,str,position)
                self.assertTrue(name.startswith("origins:"),position)
                self.assertNotIn(name,UNAVAILABLE_IN_141,position)
                self.assertIn(name.split(":",1)[1],OFFICIAL_POWER_TYPES,
                              f"{position}: {name} is not on the Origins 1.4.1 power list")
                validated.add(name)
        self.assertGreaterEqual(len(validated),14)

    def test_standard_required_fields_are_not_missing(self):
        for path in self.pack.namelist():
            if not(path.startswith("data/tarot/powers/") and path.endswith(".json")):
                continue
            for position,p in leaf_power_nodes(json.loads(self.pack.read(path)),path):
                name=p["type"]
                if name=="origins:active_self":
                    self.assertIn("entity_action",p,position)
                    self.assertIsInstance(p.get("cooldown",1),int,position)
                    self.assertGreaterEqual(p.get("cooldown",1),0,position)
                    self.assertIn(p.get("key",{"key":"key.origins.primary_active"})["key"],
                                  ("key.origins.primary_active","key.origins.secondary_active",
                                   "key.use"),position)
                if name=="origins:action_over_time":
                    self.assertIn("entity_action",p,position)
                    self.assertGreater(p.get("interval",0),0,position)
                if name=="origins:action_on_entity_use":
                    self.assertNotIn("cooldown",p,position)
                    self.assertTrue(
                        "bientity_action" in p or "held_item_action" in p or
                        "result_item_action" in p,position)
                    for hand in p.get("hands",["off_hand","main_hand"]):
                        self.assertIn(hand,("off_hand","main_hand"),position)
                if name in ("origins:attribute","origins:conditioned_attribute"):
                    self.assertTrue("modifier" in p or "modifiers" in p,position)
                    if name=="origins:conditioned_attribute":
                        self.assertIn("condition",p,position)

    def test_every_sequence_grant_refers_to_a_real_included_power(self):
        known=set(self.pack.namelist())
        for path in known:
            if not path.endswith(".mcfunction"):continue
            for line in self.pack.read(path).decode().splitlines():
                match=re.search(r"\bpower (?:grant|has) @s (tarot:[a-z0-9_/-]+)",line)
                if match:
                    powerpath="data/tarot/powers/"+match.group(1).split(":",1)[1]+".json"
                    self.assertIn(powerpath,known,(path,match.group(1)))

    def test_static_privileged_actions_cannot_op_players_or_debuff_all_players(self):
        for path in self.pack.namelist():
            if not(path.startswith("data/tarot/powers/") and path.endswith(".json")):
                continue
            power=json.loads(self.pack.read(path))
            for node in subobjects(power):
                if node.get("type")!="origins:execute_command":continue
                command=node.get("command","").lower()
                self.assertEqual(command.count("\n"),0,path)
                self.assertLessEqual(node.get("permission_level",2),2,path)
                self.assertFalse(any(command.startswith(x) for x in MUTATING_PLAYER_COMMANDS),
                                 (path,command))
                is_negative=any("minecraft:"+x in command for x in OFFENSIVE)
                if is_negative and "effect give @a" in command:
                    self.fail(f"Unsafe global player debuff in {path}: {command}")
