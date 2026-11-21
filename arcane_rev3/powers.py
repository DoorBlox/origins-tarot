"""Source-traced, non-placeholder Origins powers for the standalone Rev3 builder.

Every compiled ability has its own concrete JSON effect. Unsupported [S] abilities
remain catalog entries, *not* fake no-op powers. The catalog is the Rev2 handbook.
"""
import json
import re
import unicodedata
from pathlib import Path


def norm(name):
    name = unicodedata.normalize("NFKD", name).replace("’", "'")
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def mod(value, operation="multiply_total"):
    return {"name": "Arcane V2 Rev3", "value": value, "operation": operation}


def power(name, desc, kind, **fields):
    return {"type": kind, "name": name, "description": desc, **fields}


def attr(name, value, attribute, desc=""):
    return power(name, desc or name, "origins:attribute",
                 modifier={**mod(value, "addition" if attribute in ("armor", "knockback_resistance", "luck") else "multiply_total"),
                           "attribute": "minecraft:generic." + attribute})


def xp(name, value):
    return power(name, name, "origins:modify_xp_gain", modifier=mod(value))


def velocity(name, value):
    return attr(name, value, "movement_speed")


def phys(name, value):
    return attr(name, value, "attack_damage")


def armour(name, value):
    return attr(name, value, "armor")


def knock(name, value):
    return attr(name, value, "knockback_resistance")


def projectile(name, value):
    return power(name, name, "origins:modify_projectile_damage", modifier=mod(value))


def apply(effect, duration, amplifier=0):
    return {"type": "origins:apply_effect",
            "effect": {"effect": "minecraft:" + effect, "duration": duration,
                       "amplifier": amplifier, "show_particles": False}}


def compound(name, **subpowers):
    return power(name, name, "origins:multiple", **subpowers)


def current_catalog(root):
    p = root / "arcane" / "catalog.json"
    catalog = json.loads(p.read_text(encoding="utf-8"))
    total = sum(len(level["abilities"]) for family in ("individual", "resonance")
                for card in catalog[family] for level in card["sequences"])
    if len(catalog["individual"]) != 22 or len(catalog["resonance"]) != 11 or total != 434:
        raise ValueError("Rev2 catalog incomplete: expected 22 + 11, 434 named abilities")
    return catalog


def compile_powers(root):
    """Returns compiled powers, list of all statuses, and per-kit grant identifiers."""
    catalog = current_catalog(root)
    entries = {}
    for family in ("individual", "resonance"):
        for card in catalog[family]:
            for level in card["sequences"]:
                for entry in level["abilities"]:
                    key = (card["slug"], level["sequence"], norm(entry["name"]))
                    if key in entries:
                        raise ValueError("duplicate ability " + str(key))
                    entries[key] = (card, entry, family)
    compiled = {}
    accurate = {}
    notes = {}
    def add(slug, seq, name, value, accuracy="full", missing=""):
        key = (slug, seq, norm(name))
        if key not in entries:
            raise ValueError("ability not in authoritative handbook: " + str(key))
        if accuracy not in ("full", "partial") or (accuracy == "partial" and not missing):
            raise ValueError("partial implementation requires disclosed missing details")
        card, entry, family = entries[key]
        if family != "individual":
            raise ValueError("wrong family")
        if not value.get("type", "").startswith("origins:") or value["type"] == "origins:simple":
            raise ValueError("invalid or fake power")
        ident = "tarot:" + slug + "/" + str(seq) + "_" + entry["slug"]
        if ident in compiled:
            raise ValueError("duplicate compiled power")
        value = dict(value)
        value["name"] = name
        value["description"] = value.get("description", "") or entry["description"][:180]
        compiled[ident] = value
        accurate[key] = accuracy
        if missing:
            notes[key] = missing
    # Review and reuse real, version-scoped native implementations from the
    # archived PR7. They do not carry server scripts or KubeJS.
    templates = json.loads((root / "arcane" / "templates.json").read_text(encoding="utf-8"))
    for template in templates:
        add(template["slug"], template["sequence"], template["name"],
            template["power"], template["accuracy"], template.get("missing", ""))
    # Exact or conservative datapack implementations; no arbitrary enemy scans.
    # Fool Sequence 9 strictly follows the 2026 Rev2/Rev3 specifications.
    add("fool", 9, "Spirit Vision", power("Spirit Vision",
        "Sneak + secondary key: Glowing I, 10 blocks, 40 ticks; 100t cooldown.",
        "origins:active_self", cooldown=100, hud_render={"should_render":True},
        key={"key":"key.origins.secondary_active"}, condition={"type":"origins:sneaking"},
        entity_action={"type":"origins:area_of_effect", "radius":10,
             "include_target":True, "bientity_action":{"type":"origins:target_action",
                                                       "action":apply("glowing",40)}}))
    add("fool", 9, "Clown's Mischief", power("Clown's Mischief",
        "20% chance to blind attacker for 20 ticks; 100t cooldown.",
        "origins:attacker_action_when_hit", cooldown=100,
        entity_action={"type":"origins:chance","chance":0.2,"action":apply("blindness",20)}))
    add("high_priestess", 9, "Reader's Aptitude", xp("Reader's Aptitude",0.35))
    add("high_priestess", 9, "Scripted Insight", projectile("Scripted Insight",0.20),
        "partial", "Must only apply while not sprinting; pending condition")
    add("emperor", 9, "Sovereign's Plate", compound("Sovereign's Plate",
        armor={"type":"origins:attribute","modifier":{**mod(3,"addition"),"attribute":"minecraft:generic.armor"}},
        knockback={"type":"origins:attribute","modifier":{**mod(0.4,"addition"),"attribute":"minecraft:generic.knockback_resistance"}}))
    add("hierophant", 9, "Scripture and Study", xp("Scripture and Study",0.40))
    add("strength", 9, "Steel Frame", armour("Steel Frame",2))
    add("hermit", 9, "Mystery Prying", xp("Mystery Prying",0.35),
        "partial", "Cave-specific XP bonus not yet gated")
    add("wheel_of_fortune", 9, "Gentle Fortune", compound("Gentle Fortune",
        experience={"type":"origins:modify_xp_gain","modifier":mod(0.10)},
        luck={"type":"origins:attribute","modifier":{**mod(1,"addition"),"attribute":"minecraft:generic.luck"}}))
    add("justice", 9, "Emotional Recoil", power("Emotional Recoil","Attacker gets Weakness I for 80 ticks (360t CD).",
        "origins:attacker_action_when_hit", entity_action=apply("weakness",80),cooldown=360))
    add("death",9,"Soul Harvest",power("Soul Harvest","Heal 2 HP on kill (200t CD).",
        "origins:self_action_on_kill",entity_action={"type":"origins:heal","amount":2},cooldown=200),
        "partial","Kill target must be hostile mob or enemy player")
    add("devil",9,"Hellborn",power("Hellborn","Complete fire immunity.","origins:fire_immunity"))
    add("judgement",9,"Law's Weight",compound("Law's Weight",
        armor={"type":"origins:attribute","modifier":{**mod(2,"addition"),"attribute":"minecraft:generic.armor"}},
        knockback={"type":"origins:attribute","modifier":{**mod(0.45,"addition"),"attribute":"minecraft:generic.knockback_resistance"}}))
    add("world",9,"Cold Precision",projectile("Cold Precision",0.25))
    add("star",9,"Sleepless",power("Sleepless","Night vision without sleeping.","origins:night_vision"),
        "partial","Blindness and Darkness duration reductions not supported in this passive")
    add("sun",9,"Beacon of Faith",power("Beacon of Faith",
        "Permanent Glowing while active.", "origins:action_over_time",
        interval=40, entity_action=apply("glowing",90)))
    add("magician",9,"Wayfarer's Instinct",power("Wayfarer's Instinct",
        "Jump 20% higher, except while submerged.", "origins:modify_jump",
        modifier=mod(0.20), condition={"type":"origins:submerged","inverted":True}))
    add("chariot",9,"War Rush",power("War Rush","Gain Speed I 160t on kill; 360t CD.",
        "origins:self_action_on_kill",entity_action=apply("speed",160),cooldown=360))
    add("moon",9,"Blood's Renewal",power("Blood's Renewal",
        "At night heal 1 HP once per 600 ticks.", "origins:action_over_time",
        interval=600,condition={"type":"origins:daytime","inverted":True},
        entity_action={"type":"origins:heal","amount":1}))
    add("sun",9,"Inner Radiance",compound("Inner Radiance",
        night={"type":"origins:night_vision"}, fire={"type":"origins:fire_immunity"}))
    add("devil",9,"Desperate Malice",power("Desperate Malice",
        "+18% attack damage below 40% health.","origins:conditioned_attribute",
        modifier={**mod(0.18),"attribute":"minecraft:generic.attack_damage"},
        condition={"type":"origins:relative_health","comparison":"<","compare_to":0.4},
        tick_rate=20))
    add("empress",9,"Witch's Grace",compound("Witch's Grace",
        speed={"type":"origins:attribute","modifier":{**mod(0.10),"attribute":"minecraft:generic.movement_speed"}},
        poison={"type":"origins:effect_immunity","effects":["minecraft:poison"]}))
    add("hanged_man",9,"Graze the Soul",power("Graze the Soul",
        "On kill heal 2 HP and gain Resistance I for 60 ticks; CD 120t.",
        "origins:self_action_on_kill", cooldown=120,
        entity_action={"type":"origins:and","actions":[{"type":"origins:heal","amount":2},apply("resistance",60)]}),
        "partial","Only hostile mob or enemy player kills must count")
    # Manifest includes all 434, but only installed concrete effects count as implemented.
    manifest=[]
    kits={}
    for (slug,seq,normalized),(card,entry,family) in entries.items():
        ident="tarot:"+slug+"/"+str(seq)+"_"+entry["slug"]
        key=(slug,seq,normalized)
        status=accurate.get(key,"blocked")
        manifest.append({
            "family":family,"pathway":slug,"sequence":seq,
            "name":entry["name"],"power_id":ident if status!="blocked" else None,
            "flag":entry["flag"],"status":status,
            "missing":notes.get(key,"Needs exact scripting, client integration, or verified Origins 1.4.1 translation" if status=="blocked" else ""),
            "source":entry["description"],"details":entry.get("details",[]),
        })
        if status!="blocked":
            kits.setdefault((slug,seq),[]).append(ident)
    if len(manifest)!=434 or any(a["power_id"] not in compiled for a in manifest if a["power_id"]):
        raise AssertionError("manifest integrity")
    return compiled, manifest, kits
