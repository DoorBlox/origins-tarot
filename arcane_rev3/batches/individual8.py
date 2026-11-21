"""Wave 8: 25 genuine, handbook-keyed individual gameplay subsets.

Every power is classified PARTIAL: each implementation has an actual native
Origins 1.4.1 effect, plus a catalog-traceable, explicit missing-mechanics
statement. No arbitrary block edits, owner-spoofable commands, client-only
mod assumptions, unbounded world weather, cross-team damage or player OP.
Native API / in-game acceptance remains pending on the real Fabric server.
"""
from ..powers import power, apply, mod
from ..team_policy import ally_effect, enemy_effect
from .shared import active, periodic, combined, effect, mobs, cmd
from .resonance6 import timed_decoy


def held(item, slot="offhand"):
    return {"type": "origins:equipped_item", "equipment_slot": slot,
            "item_condition": {"type": "origins:ingredient",
                               "ingredient": {"item": "minecraft:" + item}}}


def book_offhand():
    return {"type": "origins:equipped_item", "equipment_slot": "offhand",
            "item_condition": {"type": "origins:ingredient",
                               "ingredient": {"tag": "tarot:books"}}}


def shield_hand():
    return {"type": "origins:or", "conditions": [
        held("shield", "mainhand"), held("shield", "offhand")]}


def near_villager():
    return {"type": "origins:command", "permission_level": 2,
            "command": "execute at @s if entity @e[type=minecraft:villager,distance=..8,limit=1]",
            "comparison": ">=", "compare_to": 1}


def reveal_nbt(name, nbt, radius, cooldown, *, crouch=False):
    """Reveal only a nearby player's already visible held item or health.

    Fixed, range-bounded query; no arbitrary inventory browsing, reading
    private chat, storing target data, external commands or global messages.
    """
    if nbt not in ("SelectedItem.id", "Health") or radius not in (6, 8):
        raise ValueError("Only owner-approved, small player disclosures")
    label = "held item" if nbt == "SelectedItem.id" else "health"
    payload = (
        'execute at @s if entity @a[distance=0.01..' + str(radius) + '] '
        'run tellraw @s [{"text":"[Tarot] Nearest player ' + label + ': "},'
        '{"nbt":"' + nbt + '","entity":"@p[distance=0.01..' +
        str(radius) + ']","interpret":false}]'
    )
    return active(name, "Shows the nearest non-self player's " + label +
                  " to the caster only.", cmd(payload), cooldown,
                  crouch=crouch)


def right_click_passive(name, effect_name, ticks, *, bone=False):
    data = power(name, "Right-click a passive creature to apply a harmless benefit.",
                 "origins:action_on_entity_use",
                 bientity_condition={
                     "type": "origins:target_condition",
                     "condition": {"type": "origins:in_tag", "tag": "tarot:passive"}},
                 bientity_action={"type": "origins:target_action",
                                  "action": apply(effect_name, ticks)})
    if bone:
        data["condition"] = held("bone", "mainhand")
    return data


def register(add):
    # Magician: fixed scope prevents protection-breaking adjacent block edits.
    add("magician", 3, "Shortcut",
        power("Shortcut", "Natural stone breaks 10% faster.",
              "origins:modify_break_speed",
              block_condition={"type": "origins:in_tag",
                               "tag": "tarot:natural_stone"},
              modifier=mod(0.10)),
        "partial", "10% natural-stone speed is usable but never breaks the opposite block; missing 10% BlockBreakEvent, block equality check, tool durability accounting and land protection hook")
    add("magician", 1, "Astral Lock",
        active("Astral Lock", "Primary weakens pursuers with a team-filtered slow.",
               enemy_effect("slowness", 100, 10, 1), 1800, primary=True),
        "partial", "Slowness II affects only explicitly different-team players within ten blocks; cannot cancel teleport packets/events, block potions, or restrain neutral/unlisted targets")

    # High Priestess: no forged cross-lectern inventory or economic dupe.
    index = active("Index", "Book in offhand invokes 200t self Luck I.",
                   apply("luck", 200), 1200)
    index["condition"] = book_offhand()
    add("high_priestess", 7, "Index", index, "partial",
        "Offhand-book Luck is a limited reference-memory aid; no book is stored/retrieved across lecterns, no copying or duplication, no 50-block inventory query")
    add("high_priestess", 6, "Cross-Reference",
        power("Cross-Reference", "Book offhand grants +10% earned XP.",
              "origins:modify_xp_gain", condition=book_offhand(),
              modifier=mod(0.10)),
        "partial", "Book-condition XP bonus is not the source's per-enchantment lapis discount; no enchanting screen event, lapis transfer, or XP level refund")

    # Emperor: vanilla Hero of the Village is an actual trade-affecting buff,
    # intentionally not represented as exactly 10% or exclusively one trader.
    add("emperor", 9, "Decree of the Sovereign",
        periodic("Decree of the Sovereign",
                 "Shield in hand near a villager gives brief Hero of the Village.",
                 apply("hero_of_the_village", 100), 80,
                 condition={"type": "origins:and",
                            "conditions": [shield_hand(), near_villager()]}),
        "partial", "Hero of the Village really changes vanilla villager discounts but cannot enforce exactly 10%, affects other nearby villagers, and may overlap a raid-granted effect")

    # Hierophant: blessed vision is safe and does not modify third-party builds.
    consecrate = active("Consecrate",
                       "Offhand torch blesses caster and same-team allies with Night Vision.",
                       combined(apply("night_vision", 1200),
                                ally_effect("night_vision", 1200, 3)),
                       1200)
    consecrate["condition"] = held("torch")
    add("hierophant", 7, "Consecrate", consecrate, "partial",
        "Torch-key blessing uses self/ally Night Vision for 1200t, not a clicked block light-level 10 region; no persistent three-block lighting, reversible block modification or 1200t world anchor")
    add("hierophant", 6, "Contract",
        reveal_nbt("Contract", "Health", 8, 1200),
        "partial", "Reads only one nearby player's current Health once on secondary key; no clicked-target contract, persistent 12000t tab-list display, consent, or repeated updates")

    # Hermit can ask a real fixed structure-location question with the
    # built-in 1.18.2 /locate, but cannot parse natural-language yes/no.
    add("hermit", 2, "Sage’s Counsel",
        active("Sage’s Counsel",
               "Secondary key locates a stronghold from the Overworld.",
               cmd("execute if dimension minecraft:overworld run locate minecraft:stronghold"),
               6000),
        "partial", "Fixed stronghold locate is a bounded useful structure query; no arbitrary yes/no natural-language question, selected structure category or response classifier")

    # Justice retains privacy boundaries and passive-mob protection.
    add("justice", 9, "Calming Presence",
        periodic("Calming Presence",
                 "Nearby passive creatures receive brief Regeneration I.",
                 effect(mobs(8, "passive"), "regeneration", 100), 200),
        "partial", "Protects nearby passive mobs but does not rewrite flee or panic AI, target awareness, breeding/pathfinding, or fear reactions")
    add("justice", 2, "Discern",
        reveal_nbt("Discern", "SelectedItem.id", 6, 3600),
        "partial", "Shows only the nearest non-self player's selected held item ID once; no complete inventory, no cursor selection, no item NBT/count, no protection against target changing")
    add("justice", 1, "Author’s Edit",
        active("Author’s Edit",
               "Primary key marks and weakens explicitly enemy-team players.",
               combined(enemy_effect("glowing", 300, 8),
                        enemy_effect("weakness", 300, 8)), 2400,
               primary=True),
        "partial", "No player chat editing, language parsing, command execution from chat, or mind reading; bounded debuffs on only allowlisted opponents replace scripted communication control")

    # Death: no involuntary permanent hostile AI allies or hidden player kill.
    add("death", 2, "Consul",
        active("Consul",
               "Secondary invokes a harmless 200t decoy and weakens undead nearby.",
               combined(timed_decoy(1),
                        effect(mobs(8, "undead"), "weakness", 200)), 6000),
        "partial", "10-second smoke decoy and undead Weakness are not an AI minion fighting for the caster for 200t; no undead ownership, target forcing or griefable summons")
    add("death", 1, "Reap",
        active("Reap",
               "Primary applies short Wither to nearby hostiles and Weakness to opposing teams.",
               combined(effect(mobs(8), "wither", 80, 1),
                        effect(mobs(8), "weakness", 60),
                        enemy_effect("weakness", 60, 8)),
               2400, primary=True),
        "partial", "Wither is a nonlethal bounded substitute, NOT an execute/kill under 30% health, exact post-kill Weakness pulse, boss health threshold or enemy-player execution; does not damage allies")

    # Temperance: right-click controls tagged hostiles only, no forced aggro.
    add("temperance", 4, "Puppet",
        power("Puppet", "Right-clicking a hostile weakens it for 100 ticks.",
              "origins:action_on_entity_use",
              bientity_condition={"type": "origins:target_condition",
                                  "condition": {"type": "origins:in_tag",
                                                "tag": "tarot:hostile"}},
              bientity_action={"type": "origins:target_action",
                               "action": apply("weakness", 100)}),
        "partial", "Native right-click Weakness on hostile mobs, not AI target retargeting for 100t; no safe enemy-player right-click or fixed 900t cooldown")

    # Devil: show only item currently held, never another player's inventory.
    add("devil", 5, "Desire",
        reveal_nbt("Desire", "SelectedItem.id", 6, 200, crouch=True),
        "partial", "Crouch+secondary reveals only nearest player's held item ID to caster; no crouch-right-click exact target, durability/NBT/count or snapshot of other inventory slots")
    add("devil", 3, "Blather",
        periodic("Blather",
                 "Rarely confuses tagged hostiles and enemy players with weakness.",
                 {"type": "origins:chance", "chance": 0.10,
                  "action": combined(effect(mobs(8), "weakness", 80),
                                     enemy_effect("weakness", 80, 8))},
                 200),
        "partial", "10% per 200t Weakness pulse does not change attack targets/AI; cannot force attack of nearby enemies or change player-vs-player combat allegiance")

    # Tower cannot dig someone else's blocks or bypass claims.
    add("tower", 7, "Fault Line",
        power("Fault Line", "Mine natural stone 5% faster.",
              "origins:modify_break_speed",
              block_condition={"type": "origins:in_tag", "tag": "tarot:natural_stone"},
              modifier=mod(0.05)),
        "partial", "5% break-speed bonus is not a 5% after-break proc that breaks the upper block; no land-protection bypass or adjacent world mutation")

    # Moon: living passive mobs can be protected, never fabricated resurrected
    # entities or untrusted player-controlled AI.
    add("moon", 8, "Tame",
        right_click_passive("Tame", "regeneration", 1200, bone=True),
        "partial", "Bone-in-mainhand right-click applies Regeneration for 1200t; does not suppress flight/flee AI or force permanent taming, ownership and breeding state")
    add("moon", 6, "Brew",
        active("Brew", "Secondary grants a self-only alchemical boost.",
               combined(apply("regeneration", 160),
                        apply("resistance", 160)), 6000),
        "partial", "No instant brewing-stand process, potion ingredient consumption, brewing output or potion duplication; self buff is the limited alchemical substitute")
    add("moon", 3, "Summon",
        active("Summon",
               "Secondary conjures a 200t visual decoy while protecting nearby passive mobs.",
               combined(timed_decoy(-1),
                        effect(mobs(8, "passive"), "regeneration", 200)),
               1200),
        "partial", "10-second smoke cloud does not copy a clicked passive creature or fight for Moon for 200t; no AI target ownership, spawned hostile entities or direct player damage")
    add("moon", 2, "Life",
        active("Life",
               "Secondary heals surviving passive creatures within six blocks.",
               effect(mobs(6, "passive"), "regeneration", 400), 3600),
        "partial", "Strong living-passive protection for 400t, not resurrection of a killed passive mob, dead-entity lookup, ally ownership or 400t AI attack")
    potion = held("potion", "mainhand")
    add("moon", 1, "Pharmacist II",
        periodic("Pharmacist II",
                 "Holding a potion periodically provides Regeneration I.",
                 apply("regeneration", 80), 160, condition=potion),
        "partial", "More frequent regeneration while holding a potion replaces +35% consumed potion heal/duration. No item-use hooks, healing multiplier, instant potions or exact potion effects")

    # Judgement: protect teamless/unknown players by never reading inventory
    # or dealing damage to arbitrary server accounts.
    add("judgement", 8, "Posse",
        active("Posse",
               "Secondary highlights nearest tagged hostile within 12 blocks.",
               effect(mobs(12, nearest=True), "glowing", 1200), 1200),
        "partial", "20? no: 1200t Glowing tracks only nearest tagged hostile mob; does not right-click a player, show teammate compass direction, track arbitrary player for 1200t or reveal neutral accounts")
    add("judgement", 3, "Chaos Hunter",
        power("Chaos Hunter",
              "Deal 10% more damage against hostile creatures.",
              "origins:modify_damage_dealt",
              target_condition={"type": "origins:in_tag", "tag": "tarot:hostile"},
              modifier=mod(0.10)),
        "partial", "Flat +10% to tagged hostiles is broader than attacking a mob/player currently targeting someone else; no live aggro target introspection or enemy-player bonus")
    add("judgement", 2, "Balance",
        active("Balance",
               "Secondary heals self and weakens nearby tagged hostiles.",
               combined({"type": "origins:heal", "amount": 4},
                        effect(mobs(6), "weakness", 100),
                        enemy_effect("weakness", 100, 6)), 3600),
        "partial", "Fixed 2-health-heart self heal + safe opposing debuff replaces actual health equality/exchange with a selected hostile or enemy player; no health manipulation of other players")
