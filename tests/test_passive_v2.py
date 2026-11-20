"""V2 passive-first contract tests; not a substitute for in-game acceptance."""
import unittest
import generate

class PassiveV2Contracts(unittest.TestCase):
    def test_all_22_have_four_passive_rules(self):
        self.assertEqual(len(generate.CARDS),22)
        for slug,*_ in generate.CARDS:
            with self.subTest(slug=slug):
                p=generate.BUILD[slug]
                self.assertGreaterEqual(len(p),6)
                self.assertGreaterEqual(len(p[2:]),4)
                self.assertTrue(any(i["name"].startswith("Price:") for i in p[2:]))
    def test_original_actives_remain(self):
        for slug,*_ in generate.CARDS:
            a,b=generate.BUILD[slug][:2]
            self.assertEqual(a["key"]["key"],"key.origins.primary_active")
            self.assertEqual(b["key"]["key"],"key.origins.secondary_active")
    def test_no_generic_max_health_nerf(self):
        for slug,*_ in generate.CARDS:
            for power in generate.BUILD[slug][2:]:
                self.assertNotEqual(power.get("modifier",{}).get("attribute"),"minecraft:generic.max_health")
    def test_unique_character_constraints(self):
        expectations={"star":"origins:prevent_sleep","moon":"origins:prevent_item_use",
                      "sun":"origins:self_glow","death":"origins:disable_regen",
                      "world":"origins:prevent_entity_use"}
        for slug,typ in expectations.items():
            self.assertTrue(any(p["type"]==typ for p in generate.BUILD[slug]),slug)
    def test_retained_18_gliders(self):
        self.assertEqual(len(generate.GLIDERS),18)
        for slug in ("emperor","hierophant","strength","judgement"):
            self.assertNotIn(slug,generate.GLIDERS)
    def test_all_modifier_values_numeric(self):
        def check(o):
            if isinstance(o,dict):
                mod=o.get("modifier")
                if isinstance(mod,dict) and "value" in mod:
                    self.assertIsInstance(mod["value"],(float,int))
                for v in o.values():check(v)
            elif isinstance(o,list):
                for v in o:check(v)
        check(generate.BUILD)

if __name__=="__main__":unittest.main()
