"""Regression: complete player-owned clickable Tarot slot flow without Command Aliases."""
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from arcane_rev3.full_build import build

class ClickableTarotMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.artifacts=build(output=Path(cls.tmp.name))
        cls.z=ZipFile(cls.artifacts["only"])
    @classmethod
    def tearDownClass(cls):
        cls.z.close()
        cls.tmp.cleanup()

    def fn(self,p):
        return self.z.read("data/tarot_arcane/functions/"+p+".mcfunction").decode()

    def test_menu_uses_vanilla_nonop_triggers_only(self):
        load=self.fn("load")
        tick=self.fn("player/tick")
        for trigger in ("a_menu","a_card","a_seqpick"):
            self.assertIn(f"scoreboard objectives add {trigger} trigger",load)
            self.assertIn(f"scoreboard players enable @s {trigger}",tick)
        for objective in ("a_pick_slot","a_pick_path"):
            self.assertIn(f"scoreboard objectives add {objective} dummy",load)
        self.assertIn("function tarot_arcane:ui/menu_slot",tick)
        self.assertIn("function tarot_arcane:ui/menu_card",tick)
        self.assertIn("function tarot_arcane:ui/menu_commit",tick)
        for trigger in ("a_menu","a_card","a_seqpick"):
            self.assertIn(f"scoreboard players set @s {trigger} 0",tick)
        self.assertIn("unless score @s a_paused matches 1",tick)
        for path in ("ui/help","ui/slots"):
            self.assertIn("\"clickEvent\":",self.fn(path))

    def test_all_eight_slots_expose_edit_and_clear_buttons(self):
        for slot in range(1,9):
            script=self.fn("ui/slot_"+str(slot))
            self.assertIn(f"/trigger a_menu set {slot}",script)
            self.assertIn(f"/trigger a_clear set {slot}",script)
        self.assertIn("/trigger a_auto",self.fn("ui/slots"))

    def test_card_selector_has_22_branches_and_partner_is_locked_until_seq4(self):
        menu=self.fn("ui/menu_cards")
        self.assertEqual(menu.count("run tellraw @s"),44)
        self.assertEqual(menu.count("if score @s a_path matches "),22)
        self.assertEqual(menu.count("if score @s a_partner matches "),22)
        self.assertEqual(menu.count("if score @s a_seq matches ..4"),22)
        self.assertIn("/trigger a_card set 1",menu)
        self.assertIn("/trigger a_card set 22",menu)
        select=self.fn("ui/menu_card")
        self.assertIn("if score @s a_card = @s a_path",select)
        self.assertIn("if score @s a_card = @s a_partner",select)
        self.assertIn("a_pick_path = @s a_card",select)
        self.assertIn("function tarot_arcane:ui/menu_sequences",select)

    def test_sequence_menu_uses_8_clickable_choices_and_checks_progression(self):
        seq=self.fn("ui/menu_sequences")
        for n in range(2,10):
            self.assertIn("/trigger a_seqpick set "+str(n),seq)
            self.assertIn(f"if score @s a_seq matches ..{n}",seq)
        dispatch=self.fn("ui/menu_commit")
        self.assertIn("a_pick_slot <= @s a_max",dispatch)
        self.assertIn("a_seqpick >= @s a_seq",dispatch)
        self.assertIn("a_pick_path = @s a_path",dispatch)
        self.assertIn("a_pick_path = @s a_partner",dispatch)
        self.assertIn("a_mode matches 1",dispatch)
        self.assertIn("function tarot_arcane:ui/menu_assign",dispatch)
        assignment=self.fn("ui/menu_assign")
        self.assertIn("a_assign += @s a_rcode",assignment)
        self.assertIn("function tarot_arcane:slot/assign",assignment)
        self.assertIn("scoreboard players set @s a_assign 0",assignment)

    def test_clickable_ui_never_sends_op_privileged_or_cross_player_command(self):
        from re import findall
        paths=[p for p in self.z.namelist() if
               p.startswith("data/tarot_arcane/functions/ui/") and
               p.endswith(".mcfunction")]
        found=[]
        for path in paths:
            script=self.z.read(path).decode()
            for command in findall(r'"clickEvent":\{"action":"run_command","value":"([^"]+)"\}',script):
                found.append(command)
                self.assertTrue(command.startswith("/trigger a_"),(path,command))
                self.assertFalse(any(x in command for x in (" @a"," @e","/op ","/function ","/execute ")))
        self.assertGreaterEqual(len(found),70)
