"""Rev2 native 1.18.2 interactions batch: precise subset, no fake script hooks."""
from ..powers import power, mod, apply, compound
from .shared import active, periodic, effect, mobs, players, cmd, combined


def use_entity(name, desc, target_condition, action, *, crouch=False,
               item_condition=None):
    result=power(name, desc, "origins:action_on_entity_use",
                 bientity_condition={"type":"origins:target_condition",
                                     "condition":target_condition},
                 bientity_action={"type":"origins:target_action","action":action},
                 hands=["main_hand"])
    if crouch:
        result["condition"]={"type":"origins:sneaking"}
    if item_condition:
        result["item_condition"]=item_condition
    return result


def register(add):
    player={"type":"origins:entity_type","entity_type":"minecraft:player"}
    hostile={"type":"origins:in_tag","tag":"tarot:hostile"}
    add("lovers",8,"Triage",
        use_entity("Triage","Right-click a player to heal one heart (2 HP).",
                   player,{"type":"origins:heal","amount":2}),
        "partial","Right-click healing is native; the 400t ability cooldown cannot be enforced by 1.4.1 action_on_entity_use alone")
    add("hierophant",3,"Purify",
        use_entity("Purify","Right-click player to clear Poison and Wither.",
                   player, combined(
                       {"type":"origins:clear_effect","effect":"minecraft:poison"},
                       {"type":"origins:clear_effect","effect":"minecraft:wither"})),
        "partial","Right-click cleansing is native; exact 600t cooldown is not implemented")
    add("justice",7,"Calm",
        use_entity("Calm","Right-click hostile mob to apply Slowness I 60t.",
                   hostile,apply("slowness",60)),
        "partial","Enemy players excluded for ally safety; native right-click hook has no built-in 400t cooldown")
    nearby={"type":"origins:command",
            "command":"execute at @s if entity @e[type=#tarot:passive,distance=..4]",
            "comparison":">=","compare_to":1}
    add("lovers",6,"Symbiosis",
        power("Symbiosis","One additional maximum health point while near passive mobs.",
              "origins:conditioned_attribute", tick_rate=20, condition=nearby,
              modifier={**mod(1.0,"addition"),
                        "attribute":"minecraft:generic.max_health"}),
        "partial","Nearby passive detection uses a server-side command condition; one HP is one health point, not one heart; runtime not verified")
    work={"type":"origins:block_in_radius","radius":8,"shape":"sphere",
          "block_condition":{"type":"origins:or","conditions":[
              {"type":"origins:block","block":"minecraft:lectern"},
              {"type":"origins:block","block":"minecraft:enchanting_table"}]}}
    add("hierophant",9,"Consecrated Workspace",
        compound("Consecrated Workspace",
            haste={"type":"origins:action_over_time","interval":40,
                   "condition":work,"entity_action":apply("haste",80)},
            low_exhaustion={"type":"origins:modify_exhaustion","condition":work,
                             "modifier":mod(-0.15)}),
        "partial","Repeated 8-block spherical scans may be costly with many players; server runtime/performance needs verification")
    sanctified={"type":"origins:block_in_radius","radius":5,"shape":"sphere",
               "block_condition":{"type":"origins:in_tag","tag":"tarot:sanctified_ground"}}
    add("hierophant",4,"Sanctified Ground II",
        power("Sanctified Ground II","Nearby stone-brick blocks improve XP gain 5%.",
              "origins:modify_xp_gain",condition=sanctified,
              modifier=mod(0.05)),
        "partial","Radius expanded and vanilla stone-brick variants tagged, but this can stack with Seq9 Sanctified Ground")
    add("tower",9,"Unstable Ground",
        power("Unstable Ground","5% chance of stone-crack particles when mining natural stone.",
              "origins:action_on_block_break",
              block_condition={"type":"origins:in_tag","tag":"tarot:natural_stone"},
              entity_action={"type":"origins:chance","chance":0.05,
                             "action":cmd("particle minecraft:block minecraft:stone ~ ~0.5 ~ 0.3 0.3 0.3 0.1 8")}),
        "partial","Particles appear at the miner instead of the exact broken stone position")
    add("emperor",7,"Coin",
        use_entity("Coin","Right-click a hostile mob while holding a gold ingot to slow it.",
                   hostile,apply("slowness",100),
                   item_condition={"type":"origins:ingredient",
                                   "ingredient":{"item":"minecraft:gold_ingot"}}),
        "partial","Does not erase hostile AI target or pacify enemy players; active-key source and 600t cooldown not enforced")
    add("fool",7,"Stage Magician",
        power("Stage Magician","25% chance when hit by hostile mob to retreat three blocks.",
              "origins:self_action_when_hit",cooldown=400,
              damage_condition={"type":"origins:attacker",
                                "entity_condition":{"type":"origins:in_tag","tag":"tarot:hostile"}},
              entity_action={"type":"origins:chance","chance":0.25,
                  "action":cmd("execute at @s positioned ^ ^ ^-3 "
                                "if block ~ ~ ~ minecraft:air "
                                "if block ~ ~1 ~ minecraft:air run tp @s ~ ~ ~")}),
        "partial","Decoy armor stand not spawned, player attackers omitted, and backward destination lacks collision raycast")
    in_crowd={"type":"origins:command",
              "command":"execute at @s if entity @e[type=#tarot:hostile,distance=..8]",
              "comparison":">=","compare_to":3}
    add("fool",9,"Spiritual Overload",
        periodic("Spiritual Overload","Three or more hostile mobs near the Fool cause Nausea I.",
                 apply("nausea",100),40,condition=in_crowd),
        "partial","The alternative one-enemy-player crowd condition is not implemented; only tagged hostiles count")
    add("justice",1,"Compassionate Restraint II",
        compound("Compassionate Restraint II",
           passive={"type":"origins:modify_damage_dealt",
                    "target_condition":{"type":"origins:in_tag","tag":"tarot:passive"},
                    "modifier":mod(-0.8)},
           hostile={"type":"origins:modify_damage_dealt",
                    "target_condition":hostile,"modifier":mod(0.10)}),
        "partial","Innate Seq9 Compassionate Restraint still applies -70% passive damage; this upgrade stacks instead of replacing")
    skulls={"type":"origins:or","conditions":[
        {"type":"origins:block","block":x} for x in
        ("minecraft:skeleton_skull","minecraft:wither_skeleton_skull",
         "minecraft:zombie_head","minecraft:player_head")]}
    add("death",8,"Grave Dirt",
        power("Grave Dirt","Right-click a grave skull or head for one experience point.",
              "origins:action_on_block_use", block_condition=skulls,
              entity_action=cmd("experience add @s 1 points"),
              hands=["main_hand"]),
        "partial","Only four vanilla skull/head block variants; no custom graves or 1200t cooldown")
    crop={"type":"origins:or","conditions":[
        {"type":"origins:block","block":x} for x in
        ("minecraft:wheat","minecraft:carrots","minecraft:potatoes")]}
    add("lovers",7,"Blessing",
        power("Blessing","Crouch-right-click wheat, carrots or potatoes to mature them.",
              "origins:action_on_block_use", condition={"type":"origins:sneaking"},
              block_condition=crop,hands=["main_hand"],
              block_action={"type":"origins:modify_block_state",
                            "property":"age","operation":"set","change":7}),
        "partial","Only wheat, carrots and potatoes supported; beetroot and modded crops excluded; 1200t per-crop cooldown absent")
    add("chariot",7,"Flame Burst",
        periodic("Flame Burst","While sprinting, ignite hostile mobs within two blocks.",
                 cmd("execute at @s as @e[type=#tarot:hostile,distance=..2] "
                     "run data merge entity @s {Fire:40s}"),40,
                 condition={"type":"origins:sprinting"}),
        "partial","Applies on nearby hostile mobs rather than persistent terrain trail; enemy players omitted")
    add("lovers",4,"Transmute",
        active("Transmute","Secondary key: safely exchange two iron ingots for one gold ingot.",
               cmd("function tarot_arcane:abilities/lovers_transmute"),12000),
        "partial","Cooldown starts even without two iron ingots; only one fixed transaction per activation")
