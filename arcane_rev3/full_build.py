"""Rev3 datapack-only developer build: 22 origins and genuine scoreboard slots.

No KubeJS or custom Java; all /tarot aliases execute as the player via /trigger.
Sequence 1 remains fail-closed UNLESS an OP explicitly enables the isolated
Resonance development transition per player. Never install on a live SMP.
"""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from .model import PATHWAYS, PAIRS, PARTNER
from .powers import compile_powers, norm
from progression.catalog import CARDS, ACT_MARKS, RITUALS
from progression.build import quest

ROOT=Path(__file__).resolve().parent.parent
SOURCE="tarot_arcane:slot_grants"
RESONANCE_SOURCE="tarot_arcane:resonance_seq1_test"
PARTNER_IDENTITY_SOURCE="tarot_arcane:resonance_partner_identity_test"
DEV_PREVIEW_SOURCE="tarot_arcane:resonance_manual_preview"
PREFIX="tarot_arcane:"
NUM={slug:i+1 for i,slug in enumerate(PATHWAYS)}
# Every pathway has an identity drawback. All 21 non-Fool drawbacks now
# compile and live on the immutable primary Origin rather than slots.
# The Fool uses a dedicated Spiritual Expenditure identity JSON.
IDENTITY_DRAWBACK_NAMES = {
    "magician": "Full Moon Ravings",
    "high_priestess": "Dependent on Rituals",
    "empress": "Exposed Reflection",
    "emperor": "Weight of the Crown",
    "hierophant": "Sacred Dietary Vow",
    "lovers": "Separation Anxiety",
    "justice": "Compassionate Restraint",
    "hanged_man": "Weight of Sin",
    "chariot": "Extinguished Fury",
    "strength": "The Giant Sinks",
    "hermit": "Forbidden Knowledge",
    "wheel_of_fortune": "Debt of Fate",
    "death": "Severed Vitality",
    "temperance": "Unstable Manifestation",
    "devil": "Sacred Rejection",
    "tower": "Falling Tower",
    "star": "True Sleeplessness",
    "moon": "Blood Diet",
    "sun": "Beacon of Faith",
    "judgement": "No Unlawful Escape",
    "world": "Terrifying Reputation",
}


def pin_identity_drawbacks(compiled, kits):
    """Move identity penalties out of removable Seq9 source-grant kits."""
    result = {}
    for slug, name in IDENTITY_DRAWBACK_NAMES.items():
        matching = [
            ident for ident, definition in compiled.items()
            if ident.startswith(f"tarot:{slug}/9_")
            and norm(definition["name"]) == norm(name)
        ]
        if len(matching) != 1:
            raise ValueError(f"Missing or ambiguous native identity drawback: {slug}: {name}")
        ident = matching[0]
        key = (slug, 9)
        if ident not in kits.get(key, []):
            raise ValueError(f"Identity drawback absent from original kit: {ident}")
        kits[key] = [power for power in kits[key] if power != ident]
        result[slug] = ident
    if len(result) != 21:
        raise ValueError("Native identity drawback extraction incomplete")
    return result


from .sin_engine import SIN_SCORES

SCORES=("a_init","a_paused","a_path","a_partner","a_seq","a_mode","a_max","a_marks","a_phase",
        "a_actcd","a_combat","a_clock","a_seen_dealt","a_seen_taken",
        "a_seen_bow","a_seen_crossbow","a_seen_trident","a_probe","a_has","a_ok","a_marks_ok","a_start_seq","a_a","a_b",
        "a_rslot","a_rcode","a_rpath","a_rseq","a_swap_a","a_swap_b","a_tmp","a_tmpb",
        "a_s1","a_s2","a_s3","a_s4","a_s5","a_s6","a_s7","a_s8",
        "a_view_slot","a_view_code","a_view_path","a_view_seq",
        "a_alone_time","a_iron_count","a_pick_slot","a_pick_path")
RESCUE_COOLDOWNS = ("a_cd_martyr", "a_cd_swift", "a_cd_history", "a_cd_hunter", "a_cd_undying")
SCORES += RESCUE_COOLDOWNS + ("a_rtest", "a_focus") + SIN_SCORES
TRIGGERS=("a_help","a_status","a_slots","a_assign","a_clear","a_swap",
          "a_auto","a_reset","a_ascend","a_menu","a_card","a_seqpick",
          "a_focus_menu","a_choose","a_guide","a_abilities","a_roadmap",
          "a_kit","a_detail","a_stages","a_book","a_tome")


def J(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(",",":"))

def F(name):
    return "function "+PREFIX+name

def msg(message,color="gold"):
    return "tellraw @s "+J({"text":"[Tarot] "+message,"color":color})

def score(obj):
    return {"score":{"name":"*","objective":obj}}


def click(label, trigger, color="green"):
    """One safe, no-OP command: the clicking player runs their own trigger."""
    if not trigger.startswith("a_") or any(c in trigger for c in ("@","/",";","\\n")):
        raise ValueError("click actions must be fixed player-scoped triggers")
    return "tellraw @s "+J({
        "text":label, "color":color, "underlined":True,
        "clickEvent":{"action":"run_command","value":"/trigger "+trigger},
    })


class Pack:
    def __init__(self):
        self.files={}
    def j(self,path,obj):
        if path in self.files:raise ValueError("file collision "+path)
        self.files[path]=(json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode()
    def f(self,name,*lines):
        path="data/tarot_arcane/functions/"+name+".mcfunction"
        if path in self.files:raise ValueError("function collision "+name)
        flat=[]
        for line in lines:
            if isinstance(line,(list,tuple)):flat.extend(line)
            else:flat.append(line)
        self.files[path]=("\n".join(l for l in flat if l)+"\n").encode()


def emit_content(w,root,compiled,variant,identity_powers):
    from .powers import current_catalog
    from .compat_141 import adapt_141, chance_predicate
    catalog=current_catalog(root)
    info={card["slug"]:card for card in CARDS}
    w.j("pack.mcmeta",{"pack":{"pack_format":9,
        "description":"Arcane V2 Rev3 22-pathway DEV build; INCOMPLETE, TEST ONLY"}})
    for tag,target in (("load",PREFIX+"load"),("tick",PREFIX+"tick")):
        w.j("data/minecraft/tags/functions/"+tag+".json",{"values":[target]})
    w.j("data/origins/origin_layers/origin.json",{"replace":variant=="only",
         "origins":["tarot:"+slug for slug in PATHWAYS]})
    tags=json.loads((root/"arcane/tags.json").read_text(encoding="utf8"))
    for key,values in tags.items():
        w.j("data/tarot/tags/"+key+".json",{"replace":False,
              "values":["minecraft:"+x for x in values]})
    for name in ("decoy","shadow_minion","shadow_sin"):
        w.j("data/tarot/tags/entity_types/"+name+".json",
            {"replace":False,"values":["minecraft:armor_stand"]})
    for slug in PATHWAYS:
        c=info[slug]
        wings=["tarot:"+slug+"/wings"] if c["glider"] else []
        # Sequence-9 identity penalties are inherent to the primary Origin;
        # unlike chosen sequence kits they cannot be removed via /tarot slot.
        identity=(["tarot:fool/identity_spiritual_expenditure"] if slug=="fool"
                  else [identity_powers[slug]] if slug in identity_powers else [])
        w.j("data/tarot/origins/"+slug+".json",{
             "powers":wings+identity+["tarot:"+slug+"/runtime_sync"],
             "icon":"minecraft:paper", "name":c["name"],
             "description":"Rev3 player-owned slot kits; "+c["lore"],
             "impact":3,"order":c["id"]-1})
        # The 1.18.2 server rejected "origin has origin" during function
        # compilation. Use the chosen Origin's own power to initialize
        # its matching scoreboard path; no player OP is granted.
        w.j("data/tarot/powers/"+slug+"/runtime_sync.json",{
            "type":"origins:action_over_time", "interval":20,
            "hidden":True,
            "name":"Internal Arcane state sync",
            "description":"Synchronizes this selected Tarot Origin with scoreboard state.",
            "entity_action":{"type":"origins:execute_command",
                             "permission_level":2,
                             "command":F("player/sync/"+slug)}})
        if wings:
            w.j("data/tarot/powers/"+slug+"/wings.json",{
                "type":"origins:elytra_flight","render_elytra":True,
                "name":c["name"]+" Wings",
                "description":"Innate Elytra-style gliding, separate from the removable sequence kit."})
    w.j("data/tarot/powers/fool/identity_spiritual_expenditure.json",{
        "type":"origins:modify_exhaustion",
        "name":"Spiritual Expenditure",
        "description":"The Fool consumes 25% more exhaustion while sprinting or gliding.",
        "modifier":{"name":"Fool Spiritual Expenditure","operation":"multiply_total","value":0.25},
        "condition":{"type":"origins:or","conditions":[
            {"type":"origins:sprinting"},
            {"type":"origins:fall_flying"}]}
    })
    for a,b,res in PAIRS:
        w.j("data/tarot/origins/"+res+".json",{
            "powers":[],"icon":"minecraft:nether_star",
            "name":"The "+res.replace("_"," ").title(),
            "description":"Resonance for "+a+" + "+b+"; development-only, not selectable.",
            "impact":3,"unchoosable":True})
    chance_rates=set()
    for ident,power in compiled.items():
        adapted, rates, changes = adapt_141(power)
        chance_rates.update(rates)
        w.j("data/tarot/powers/"+ident.split(":")[1]+".json", adapted)
    # Minecraft 1.18.2 has vanilla random-chance loot predicates;
    # Apoli 2.3.3 has NO "origins:chance" entity condition.
    for basis in sorted(chance_rates):
        w.j(f"data/tarot_arcane/predicates/chance/{basis}.json",
            chance_predicate(basis))


def emit_player(w,kits,root=ROOT):
    w.f("load",
        [f"scoreboard objectives add {x} dummy" for x in SCORES],
        [f"scoreboard objectives add {x} trigger" for x in TRIGGERS],
        "scoreboard objectives add a_dmg_dealt minecraft.custom:minecraft.damage_dealt",
        "scoreboard objectives add a_dmg_taken minecraft.custom:minecraft.damage_taken",
        "scoreboard objectives add a_deaths minecraft.custom:minecraft.deaths",
        "scoreboard objectives add a_bow minecraft.used:minecraft.bow",
        "scoreboard objectives add a_crossbow minecraft.used:minecraft.crossbow",
        "scoreboard objectives add a_trident minecraft.used:minecraft.trident",
        "scoreboard objectives add a_const dummy",
        "scoreboard players set #4 a_const 4",
        "scoreboard players set #10 a_const 10",
        "scoreboard players set #80 a_const 80",
        "scoreboard players set #100 a_const 100",
        "scoreboard players set #10000 a_const 10000")
    w.f("tick","execute as @a at @s run "+F("player/tick"))
    w.f("player/tick",
        [f"scoreboard players enable @s {x}" for x in TRIGGERS],
        "scoreboard players add @s a_dmg_dealt 0",
        "scoreboard players add @s a_dmg_taken 0",
        "scoreboard players add @s a_deaths 0",
        "scoreboard players add @s a_bow 0",
        "scoreboard players add @s a_crossbow 0",
        "scoreboard players add @s a_trident 0",
        "scoreboard players add @s a_alone_time 0",
        [f"scoreboard players add @s {x} 0" for x in RESCUE_COOLDOWNS],
        [f"execute if score @s {x} matches 1.. run scoreboard players remove @s {x} 1" for x in RESCUE_COOLDOWNS],
        "execute unless score @s a_init matches 1 unless score @s a_paused matches 1 run "+F("player/detect"),
        "execute if score @s a_init matches 1 run "+F("player/combat_stats"),
        "execute if score @s a_init matches 1 run "+F("player/alone"),
        # Persistent Sin state belongs exclusively to the owner of an
        # actual source-granted Hanged power. Never process a teamless
        # opponent's scoreboard or retain Sin after loss/death/pause.
        "execute if score @s a_deaths > @s a_seen_deaths run "+F("sin/clear"),
        "scoreboard players operation @s a_seen_deaths = @s a_deaths",
        "execute store success score @s a_sin_owned run power has @s tarot:hanged_man/9_sin_bearing",
        "execute store success score @s a_sin_capown run power has @s tarot:hanged_man/0_weight_of_sin_made_manifest",
        "execute if score @s a_sin_started matches 1 unless score @s a_sin_owned matches 1 unless score @s a_sin_capown matches 1 run "+F("sin/clear"),
        "execute if score @s a_paused matches 1 if score @s a_sin_started matches 1 run "+F("sin/clear"),
        "execute if score @s a_init matches 1 unless score @s a_paused matches 1 if score @s a_sin_owned matches 1 run "+F("sin/tick"),
        "execute if score @s a_init matches 1 unless score @s a_paused matches 1 unless score @s a_sin_owned matches 1 if score @s a_sin_capown matches 1 run "+F("sin/tick"),
        "execute if score @s a_sin_form matches 1.. run "+F("sin/form_tick"),
        "execute if score @s a_trinity_win matches 1.. run scoreboard players remove @s a_trinity_win 1",
        "execute if score @s a_trinity_win matches 0 run scoreboard players set @s a_trinity_hits 0",
        "execute if score @s a_help matches 1.. run "+F("ui/help"),
        "execute if score @s a_status matches 1.. run "+F("ui/status"),
        "execute if score @s a_slots matches 1.. run "+F("ui/slots"),
        "execute if score @s a_guide matches 1.. run "+F("ui/book/give"),
        "execute if score @s a_abilities matches 1.. run "+F("ui/book/tome"),
        "execute if score @s a_roadmap matches 1.. run "+F("ui/roadmap"),
        "execute if score @s a_stages matches 1.. run "+F("ui/book/give"),
        "execute if score @s a_book matches 1.. run "+F("ui/book/give"),
        "execute if score @s a_tome matches 1.. run "+F("ui/book/tome"),
        "execute if score @s a_kit matches 1.. run "+F("ui/codex/open"),
        "execute if score @s a_detail matches 1.. run "+F("ui/codex/detail_open"),
        # Focus selection is player-triggered and processed only when
        # unpaused. Nothing changes to original keys until opt-in.
        "execute unless score @s a_paused matches 1 if score @s a_focus_menu matches 1.. run "+F("ui/focus/menu"),
        "execute unless score @s a_paused matches 1 if score @s a_choose matches 1.. run "+F("ui/focus/choose"),
        "execute unless score @s a_paused matches 1 if score @s a_menu matches 1.. run "+F("ui/menu_slot"),
        "execute unless score @s a_paused matches 1 if score @s a_card matches 1.. run "+F("ui/menu_card"),
        "execute unless score @s a_paused matches 1 if score @s a_seqpick matches 1.. run "+F("ui/menu_commit"),
        "execute unless score @s a_paused matches 1 if score @s a_assign matches 1.. run "+F("slot/assign"),
        "execute unless score @s a_paused matches 1 if score @s a_clear matches 1.. run "+F("slot/clear"),
        "execute unless score @s a_paused matches 1 if score @s a_swap matches 1.. run "+F("slot/swap"),
        "execute unless score @s a_paused matches 1 if score @s a_auto matches 1.. run "+F("slot/auto"),
        "execute unless score @s a_paused matches 1 if score @s a_reset matches 1.. run "+F("slot/auto"),
        "execute unless score @s a_paused matches 1 if score @s a_ascend matches 1.. run "+F("ascend/dispatch"),
        [f"scoreboard players set @s {x} 0" for x in TRIGGERS],
        "execute if score @s a_init matches 1 run scoreboard players add @s a_clock 1",
        "execute if score @s a_actcd matches 1.. run scoreboard players remove @s a_actcd 1",
        "execute if score @s a_combat matches 1.. run scoreboard players remove @s a_combat 1",
        "execute if score @s a_init matches 1 if score @s a_clock matches 600.. run "+F("player/periodic"))
    detection=["# Detect via each chosen Origin's intrinsic runtime_sync power."]
    for slug,idnum in NUM.items():
        w.f("player/init/"+slug,
            "scoreboard players set @s a_init 1",
            "scoreboard players set @s a_paused 0",
            "scoreboard players set @s a_rtest 0",
            "scoreboard players set @s a_pick_slot 0",
            "scoreboard players set @s a_pick_path 0",
            "scoreboard players set @s a_focus 0",
            f"scoreboard players set @s a_path {idnum}",
            f"scoreboard players set @s a_partner {NUM[PARTNER[slug]]}",
            "scoreboard players set @s a_seq 9",
            "scoreboard players set @s a_mode 0",
            "scoreboard players set @s a_max 1",
            "scoreboard players set @s a_marks 0",
            "scoreboard players set @s a_phase 0",
            "scoreboard players set @s a_actcd 0",
            "scoreboard players set @s a_combat 0",
            "scoreboard players set @s a_alone_time 0",
            "scoreboard players set @s a_sin_started 0",
            "scoreboard players set @s a_sin 0",
            "scoreboard players set @s a_sin_form 0",
            "scoreboard players set @s a_trinity_hits 0",
            "scoreboard players set @s a_trinity_win 0",
            "scoreboard players operation @s a_sin_seen = @s a_dmg_taken",
            "scoreboard players operation @s a_seen_deaths = @s a_deaths",
            "scoreboard players operation @s a_seen_dealt = @s a_dmg_dealt",
            "scoreboard players operation @s a_seen_taken = @s a_dmg_taken",
            "scoreboard players operation @s a_seen_bow = @s a_bow",
            "scoreboard players operation @s a_seen_crossbow = @s a_crossbow",
            "scoreboard players operation @s a_seen_trident = @s a_trident",
            "scoreboard players set @s a_clock 0",
            f"scoreboard players set @s a_s1 {idnum*100+9}",
            [f"scoreboard players set @s a_s{i} 0" for i in range(2,9)],
            F("powers/refresh"),
            msg("Awakened "+slug+" at Sequence 9. Open the player guide to get started.","aqua"),
            click("[Open player guide]","a_guide","yellow"),
            click("[See my abilities]","a_abilities","green"))
    w.f("player/detect",detection)
    # Origin power owns init and recovery. Avoid the broken 1.4.1
    # origin-has-origin parser and never force Origin selection.
    for slug,i in NUM.items():
        w.f(f"player/sync/{slug}",
            f"execute unless score @s a_init matches 1 run "+F(f"player/init/{slug}"),
            f"execute if score @s a_init matches 1 unless score @s a_path matches {i} run "+F(f"player/init/{slug}"))
    w.f("player/verify",
        "# Origin identity checked by the selected Origin's runtime_sync power.")
    # Same-team-only Lovers isolation counter. Only configured vanilla team
    # members count as allies; enemy and teamless players do not reset it.
    # Team membership is admin-defined, never changed by Arcane runtime.
    # Transaction is player scoped: test inventory without removing items,
    # then remove exactly two iron ingots and give precisely one gold ingot.
    # No client alias can choose other items or invoke this function directly.
    w.f("abilities/lovers_transmute",
        "scoreboard players set @s a_iron_count 0",
        "execute store result score @s a_iron_count run clear @s minecraft:iron_ingot 0",
        "execute if score @s a_iron_count matches 2.. run clear @s minecraft:iron_ingot 2",
        "execute if score @s a_iron_count matches 2.. run give @s minecraft:gold_ingot 1",
        "execute unless score @s a_iron_count matches 2.. run "+msg("Transmute needs two iron ingots; no items taken.","yellow"))
    from .team_policy import team_names
    w.f("player/alone",
        "scoreboard players add @s a_alone_time 1",
        [f"execute if entity @s[team={team}] at @s if entity @a[team={team},distance=0.01..8] run scoreboard players set @s a_alone_time 0" for team in team_names(root)],
        "execute if score @s a_alone_time matches 601.. run scoreboard players set @s a_alone_time 601")
    w.f("player/periodic","scoreboard players set @s a_clock 0",
        "execute unless score @s a_paused matches 1 run "+F("player/verify"),
        "execute unless score @s a_paused matches 1 run "+F("powers/reconcile"))
    # Stat counters exist in Minecraft 1.18.2. The old
    # minecraft:player_hurt_entity trigger was added in 1.19.4 and silently
    # invalidated the attacker combat-lock advancement on the target server.
    # Keep the supported entity_hurt_player trigger as a backup for received
    # PvP damage, while stat deltas cover melee damage dealt and damage taken.
    w.f("player/combat_stats",
        "execute if score @s a_dmg_dealt > @s a_seen_dealt run scoreboard players set @s a_combat 200",
        "execute if score @s a_dmg_taken > @s a_seen_taken run scoreboard players set @s a_combat 200",
        "execute if score @s a_bow > @s a_seen_bow run scoreboard players set @s a_combat 200",
        "execute if score @s a_crossbow > @s a_seen_crossbow run scoreboard players set @s a_combat 200",
        "execute if score @s a_trident > @s a_seen_trident run scoreboard players set @s a_combat 200",
        "scoreboard players operation @s a_seen_dealt = @s a_dmg_dealt",
        "scoreboard players operation @s a_seen_taken = @s a_dmg_taken",
        "scoreboard players operation @s a_seen_bow = @s a_bow",
        "scoreboard players operation @s a_seen_crossbow = @s a_crossbow",
        "scoreboard players operation @s a_seen_trident = @s a_trident")
    w.j("data/tarot_arcane/advancements/events/combat_taken.json",{
        "criteria":{"hit":{"trigger":"minecraft:entity_hurt_player"}},
        "rewards":{"function":PREFIX+"events/combat_taken"}})
    w.f("events/combat_taken",
        "scoreboard players set @s a_combat 200",
        f"advancement revoke @s only {PREFIX}events/combat_taken")
    from .sin_engine import emit_sin
    emit_sin(w, PREFIX, root)


def emit_slots(w,kits):
    w.f("slot/assign",
        "scoreboard players operation @s a_rslot = @s a_assign",
        "scoreboard players operation @s a_rslot /= #10000 a_const",
        "scoreboard players operation @s a_rcode = @s a_assign",
        "scoreboard players operation @s a_rcode %= #10000 a_const",
        "scoreboard players operation @s a_rpath = @s a_rcode",
        "scoreboard players operation @s a_rpath /= #100 a_const",
        "scoreboard players operation @s a_rseq = @s a_rcode",
        "scoreboard players operation @s a_rseq %= #100 a_const",
        "scoreboard players set @s a_ok 0",
        "scoreboard players set @s a_probe 0",
        "execute if score @s a_mode matches 1 if score @s a_rslot matches 1..8 if score @s a_rslot <= @s a_max if score @s a_rseq matches 2..9 if score @s a_rseq >= @s a_seq if score @s a_rpath = @s a_path run scoreboard players set @s a_ok 1",
        "execute if score @s a_mode matches 1 if score @s a_rslot matches 1..8 if score @s a_rslot <= @s a_max if score @s a_rseq matches 2..9 if score @s a_rseq >= @s a_seq if score @s a_rpath = @s a_partner run scoreboard players set @s a_ok 1",
        [f"execute unless score @s a_rslot matches {i} if score @s a_rcode = @s a_s{i} run scoreboard players set @s a_ok 0" for i in range(1,9)],
        # Nonexistent/entirely blocked kits cannot be equipped: no silent
        # zero-effect upgrades. One generated guard per real sequence kit.
        [f"execute if score @s a_rpath matches {NUM[slug]} if score @s a_rseq matches {seq} run scoreboard players set @s a_probe 1"
          for slug,seq in sorted(kits) if kits[(slug,seq)] and slug in NUM],
        "execute if score @s a_probe matches 0 run scoreboard players set @s a_ok 0",
        "execute if score @s a_ok matches 1 run "+F("slot/assign_ok"),
        "execute if score @s a_ok matches 0 run "+msg("Locked, duplicate, or invalid slot assignment.","red"))
    w.f("slot/assign_ok",
        [f"execute if score @s a_rslot matches {i} run scoreboard players operation @s a_s{i} = @s a_rcode" for i in range(1,9)],
        F("powers/refresh"),msg("Sequence kit equipped.","green"))
    w.f("slot/clear",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_mode matches 1 if score @s a_clear matches 1..8 if score @s a_clear <= @s a_max run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run "+F("slot/clear_ok"),
        "execute if score @s a_ok matches 0 run "+msg("You cannot clear this slot.","red"))
    w.f("slot/clear_ok",
        [f"execute if score @s a_clear matches {i} run scoreboard players set @s a_s{i} 0" for i in range(1,9)],
        F("powers/refresh"),msg("Sequence kit removed.","green"))
    w.f("slot/auto",
        "execute if score @s a_mode matches 1 run "+F("slot/auto_ok"),
        "execute unless score @s a_mode matches 1 run "+msg("Slot editing unlocks at Seq4.","red"))
    reset=[]
    for i in range(1,9):
        reset.extend([
            f"scoreboard players set @s a_s{i} 0",
            f"execute if score @s a_max matches {i}.. run scoreboard players operation @s a_s{i} = @s a_path",
            f"execute if score @s a_max matches {i}.. run scoreboard players operation @s a_s{i} *= #100 a_const",
            f"execute if score @s a_max matches {i}.. run scoreboard players add @s a_s{i} {10-i}"])
    w.f("slot/auto_ok",reset,F("powers/refresh"),msg("Slots restored to primary kits.","green"))
    w.f("slot/swap",
        "scoreboard players operation @s a_swap_a = @s a_swap",
        "scoreboard players operation @s a_swap_a /= #10 a_const",
        "scoreboard players operation @s a_swap_b = @s a_swap",
        "scoreboard players operation @s a_swap_b %= #10 a_const",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_mode matches 1 if score @s a_swap_a matches 1..8 if score @s a_swap_b matches 1..8 if score @s a_swap_a <= @s a_max if score @s a_swap_b <= @s a_max run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run "+F("slot/swap_ok"),
        "execute if score @s a_ok matches 0 run "+msg("Cannot swap locked slots.","red"))
    swap=["scoreboard players set @s a_tmp 0","scoreboard players set @s a_tmpb 0"]
    for i in range(1,9):
        swap += [
            f"execute if score @s a_swap_a matches {i} run scoreboard players operation @s a_tmp = @s a_s{i}",
            f"execute if score @s a_swap_b matches {i} run scoreboard players operation @s a_tmpb = @s a_s{i}"]
    for i in range(1,9):
        swap += [
            f"execute if score @s a_swap_a matches {i} run scoreboard players operation @s a_s{i} = @s a_tmpb",
            f"execute if score @s a_swap_b matches {i} run scoreboard players operation @s a_s{i} = @s a_tmp"]
    w.f("slot/swap_ok",swap,F("powers/refresh"),msg("Slots swapped.","green"))


def emit_grants(w, kits, identity_powers, focus_entries=()):
    """Refresh slot OR opt-in Seq1 sources while preserving native identities.

    No player-facing trigger can toggle a_rtest or directly call these
    functions: vanilla /function requires operator privileges. Primary Origin
    remains the 22-way layer choice; its identity drawback is immutable.
    """
    refresh = ["power revokeall @s " + SOURCE,
               "power revokeall @s " + RESONANCE_SOURCE,
               "power revokeall @s " + PARTNER_IDENTITY_SOURCE]
    repair = []
    for (slug, seq), powers in sorted(kits.items()):
        if not powers or slug not in NUM:
            continue
        code = NUM[slug] * 100 + seq
        w.f(f"kits/{slug}/s{seq}",
            [f"power grant @s {ident} {SOURCE}" for ident in powers])
        checks = []
        for ident in powers:
            checks += [
                f"execute store success score @s a_has run power has @s {ident}",
                f"execute if score @s a_has matches 0 run power grant @s {ident} {SOURCE}"]
        w.f(f"kits/{slug}/repair_s{seq}", checks)
        for slot in range(1, 9):
            guard = (f"execute unless score @s a_paused matches 1 "
                     f"if score @s a_mode matches 0..1 "
                     f"if score @s a_s{slot} matches {code} run ")
            refresh.append(guard + F(f"kits/{slug}/s{seq}"))
            repair.append(guard + F(f"kits/{slug}/repair_s{seq}"))

    # The 11 pair records are fixed and disjoint, allowing a safe exact
    # primary-partner comparison. All 110 source entries must exist before a
    # test transition can be built; this is a structural gate, not gameplay QA.
    for first, second, pair in PAIRS:
        powers = [ident for seq in range(9, -1, -1)
                  for ident in kits.get((pair, seq), [])]
        if len(powers) != 10 or len(set(powers)) != 10:
            raise ValueError(f"Resonance pair must compile exactly 10 powers: {pair}")
        for primary, partner in ((first, second), (second, first)):
            if partner == "fool":
                partner_identity = "tarot:fool/identity_spiritual_expenditure"
            else:
                partner_identity = identity_powers[partner]
            # Neither parent identity is allowed in the ordinary slot source.
            grant = [f"power grant @s {ident} {RESONANCE_SOURCE}" for ident in powers]
            grant.append(
                f"power grant @s {partner_identity} {PARTNER_IDENTITY_SOURCE}")
            w.f(f"resonance/{primary}/grant", grant)
            checks = []
            for ident in powers:
                checks += [
                    f"execute store success score @s a_has run power has @s {ident}",
                    f"execute if score @s a_has matches 0 run power grant @s {ident} {RESONANCE_SOURCE}"]
            checks += [
                f"execute store success score @s a_has run power has @s {partner_identity}",
                f"execute if score @s a_has matches 0 run power grant @s {partner_identity} {PARTNER_IDENTITY_SOURCE}"]
            w.f(f"resonance/{primary}/repair", checks)
            guard = (
                "execute unless score @s a_paused matches 1 "
                "if score @s a_init matches 1 "
                "if score @s a_mode matches 2 "
                "if score @s a_rtest matches 1 "
                "if score @s a_seq matches 0..1 "
                f"if score @s a_path matches {NUM[primary]} "
                f"if score @s a_partner matches {NUM[partner]} run "
            )
            refresh.append(guard + F(f"resonance/{primary}/grant"))
            repair.append(guard + F(f"resonance/{primary}/repair"))

    if focus_entries:
        # Validate focus ONLY after powers have been refreshed and as part
        # of the existing periodic reconciliation, not every player tick.
        refresh.append(F("ui/focus/validate"))
        repair.append(F("ui/focus/validate"))
    w.f("powers/refresh", refresh)
    w.f("powers/reconcile", repair)
    w.f("admin/rollback_player",
        "scoreboard players set @s a_paused 1",
        "power revokeall @s " + SOURCE,
        "power revokeall @s " + RESONANCE_SOURCE,
        "power revokeall @s " + PARTNER_IDENTITY_SOURCE,
        "power revokeall @s tarot_arcane:ability_focus",
        "scoreboard players set @s a_focus 0",
        msg("Arcane PAUSED; slot and Resonance test sources revoked until admin resume.", "yellow"))
    w.f("admin/rollback_all",
        "execute as @a run " + F("admin/rollback_player"))
    w.f("admin/resume_player",
        "scoreboard players set @s a_paused 0",
        "execute if score @s a_init matches 1 run " + F("player/verify"),
        "execute if score @s a_init matches 1 run " + F("powers/refresh"),
        msg("Arcane RESUMED; assigned source powers restored.", "green"))
    w.f("admin/resume_all",
        "execute as @a run " + F("admin/resume_player"))
    # /function is inherently OP-only in 1.18.2. Do not add triggers or
    # Command Alias entries for either admin test command.
    w.f("admin/enable_seq1_dev",
        "execute if score @s a_init matches 1 if score @s a_seq matches 2 "
        "if score @s a_mode matches 1 unless score @s a_paused matches 1 "
        "run scoreboard players set @s a_rtest 1",
        "execute if score @s a_rtest matches 1 run " +
        msg("OP TEST ONLY: Seq2->Seq1 may now be attempted with original altar, marks and offerings. Do not use on the SMP.", "yellow"),
        "execute unless score @s a_rtest matches 1 run " +
        msg("Test flag not enabled: requires initialized, unpaused Seq2 slot mode.", "red"))
    w.f("admin/disable_seq1_dev",
        "execute if score @s a_mode matches 0..1 run scoreboard players set @s a_rtest 0",
        "execute if score @s a_mode matches 2 run " +
        msg("Already in Seq1 preview! Admin rollback can pause. Restore a BACKUP to reverse this test progression.", "red"),
        "execute if score @s a_mode matches 0..1 run " +
        msg("Seq1 test permission revoked; normal progression remains locked.", "yellow"))



def emit_ui(w):
    """Player-facing status/slots use real Arcana names, not encoded scores.

    a_sN remains a compact, deterministic integer internally (card ID *100
    + sequence). Render temporaries are per-player scoreboards, so requests
    from different players cannot overwrite each other's slot display.
    """
    w.f("ui/help",
        msg("ARCANE REV3 | Books first: right-click your written handbook to read it.","gold"),
        msg("ABILITIES: your Pathway Tome covers powers, controls, and incomplete mechanics.","aqua"),
        msg("ROADMAP: next acting task, marks, offerings, ritual, and unlocks.","aqua"),
        msg("Seq9-5 auto equips; Seq4-2 unlocks a fixed partner and editable slots.","yellow"),
        msg("Seq1 Resonance LOCKED for normal SMP players; incomplete powers remain PARTIAL.","red"),
        msg("Vanilla commands: /trigger a_guide, /trigger a_help, /trigger a_abilities, /trigger a_roadmap.","gray"),
        click("[Get Arcane Handbook BOOK]","a_book","gold"),
        click("[Get my Pathway Tome BOOK]","a_tome","aqua"),
        click("[My abilities (book)]","a_abilities"),
        click("[My live marks and next task]","a_roadmap","yellow"),
        click("[All Sequence milestones]","a_stages","light_purple"),
        click("[My status]","a_status"),
        click("[Manage slots]","a_slots"),
        click("[Choose active key focus]","a_focus_menu"),
        msg("Seq4-2: /tarot slot N tarot:pathway S | /tarot slot N clear | /tarot slot auto.","gray"))
    w.f("ui/status",
        "execute unless score @s a_init matches 1 run "+msg("Choose a Tarot origin.","red"),
        "execute if score @s a_paused matches 1 run "+msg("Arcane runtime paused by administrator; ask an admin to resume.","red"),
        "execute if score @s a_init matches 1 run "+F("ui/status_primary"),
        "execute if score @s a_init matches 1 if score @s a_seq matches ..4 run "+F("ui/status_partner"),
        "execute if score @s a_mode matches 2 run "+msg("OP-enabled Seq1 Resonance preview active; not game-verified.","light_purple"),
        "execute if score @s a_init matches 1 if score @s a_seq matches 5.. run "+msg("Partner unlocks at Sequence 4.","yellow"),
        "execute if score @s a_init matches 1 run tellraw @s "+J([
            {"text":"[Tarot] Sequence: ","color":"gold"},score("a_seq"),
            {"text":" | Slots: "},score("a_max"),
            {"text":" | Acting marks: "},score("a_marks")]),
        click("[How to ascend next]","a_roadmap","yellow"),
        click("[View my active abilities]","a_abilities"))
    w.f("ui/status_primary",[
        f"execute if score @s a_path matches {c['id']} run "+msg("Primary: "+c["name"],"aqua")
        for c in CARDS])
    w.f("ui/status_partner",[
        f"execute if score @s a_partner matches {c['id']} run "+msg("Unlocked partner: "+c["name"],"light_purple")
        for c in CARDS])

    w.f("ui/slots",
        "execute unless score @s a_init matches 1 run "+msg("Choose a Tarot origin.","red"),
        [f"execute if score @s a_init matches 1 if score @s a_max matches {i}.. run "+F(f"ui/slot_{i}")
         for i in range(1,9)],
        "execute if score @s a_mode matches 0 run "+msg("SINGLE: sequence kits auto-fill as you advance.","gold"),
        "execute if score @s a_mode matches 1 run "+msg("SLOT: click Edit by any slot, select pathway, then Sequence.","yellow"),
        "execute if score @s a_mode matches 2 run "+msg("RESONANCE TEST: all ten paired powers active. Slot UI disabled.","light_purple"),
        "execute if score @s a_mode matches 1 run "+click("[Auto-fill all primary slots]","a_auto","yellow"),
        click("[Inspect equipped abilities]","a_abilities","aqua"))
    for i in range(1,9):
        w.f(f"ui/slot_{i}",
            f"scoreboard players set @s a_view_slot {i}",
            f"scoreboard players operation @s a_view_code = @s a_s{i}",
            F("ui/slot_render"),
            "execute if score @s a_view_code matches 1.. run "+click("  [View abilities in slot "+str(i)+"]","a_kit set "+str(i),"aqua"),
            "execute if score @s a_mode matches 1 run "+click("  [Edit slot "+str(i)+"]","a_menu set "+str(i),"green"),
            "execute if score @s a_mode matches 1 run "+click("  [Clear slot "+str(i)+"]","a_clear set "+str(i),"red"))

    render=[
        "scoreboard players operation @s a_view_path = @s a_view_code",
        "scoreboard players operation @s a_view_path /= #100 a_const",
        "scoreboard players operation @s a_view_seq = @s a_view_code",
        "scoreboard players operation @s a_view_seq %= #100 a_const",
        "execute if score @s a_view_code matches 0 run tellraw @s "+J([
            {"text":"[Tarot] Slot ","color":"gray"},score("a_view_slot"),
            {"text":": Empty","color":"dark_gray"}]),
    ]
    for c in CARDS:
        render.append(
            f"execute if score @s a_view_path matches {c['id']} run tellraw @s "+J([
                {"text":"[Tarot] Slot ","color":"aqua"},score("a_view_slot"),
                {"text":": "+c["name"]+" — Sequence ","color":"aqua"},score("a_view_seq")]))
    w.f("ui/slot_render",render)


    # Fully vanilla, non-OP alternative to Command Aliases 1.0.1.
    # The 1.18.2 client runs only /trigger; every choice is validated again
    # by the authoritative slot/assign function before any powers change.
    w.f("ui/menu_slot",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_mode matches 1 if score @s a_menu matches 1..8 if score @s a_menu <= @s a_max run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run scoreboard players operation @s a_pick_slot = @s a_menu",
        "execute if score @s a_ok matches 1 run "+F("ui/menu_cards"),
        "execute if score @s a_ok matches 0 run "+msg("Click Edit only on an unlocked slot at Seq4-2.","red"))
    cards=[msg("Select your PRIMARY pathway, or the unlocked partner:","aqua")]
    for c in CARDS:
        choice=click("[ "+c["name"]+" ]","a_card set "+str(c["id"]),"green")
        cards.append(f"execute if score @s a_path matches {c['id']} run "+choice)
        cards.append(f"execute if score @s a_seq matches ..4 if score @s a_partner matches {c['id']} run "+choice)
    w.f("ui/menu_cards",cards)
    w.f("ui/menu_card",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_card = @s a_path run scoreboard players set @s a_ok 1",
        "execute if score @s a_seq matches ..4 if score @s a_card = @s a_partner run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 if score @s a_pick_slot matches 1..8 if score @s a_pick_slot <= @s a_max run scoreboard players operation @s a_pick_path = @s a_card",
        "execute if score @s a_ok matches 1 if score @s a_pick_slot matches 1..8 if score @s a_pick_slot <= @s a_max run "+F("ui/menu_sequences"),
        "execute if score @s a_ok matches 0 run "+msg("This pathway is locked; select your primary or available partner.","red"))
    choices=[msg("Choose a Sequence kit (no higher than your current progress):","aqua")]
    for seq in range(9,1,-1):
        choices.append(f"execute if score @s a_seq matches ..{seq} run "+click("[ Sequence "+str(seq)+" ]","a_seqpick set "+str(seq),"yellow"))
    w.f("ui/menu_sequences",choices)
    w.f("ui/menu_commit",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_mode matches 1 if score @s a_pick_slot matches 1..8 if score @s a_pick_slot <= @s a_max if score @s a_seqpick matches 2..9 if score @s a_seqpick >= @s a_seq if score @s a_pick_path = @s a_path run scoreboard players set @s a_ok 1",
        "execute if score @s a_mode matches 1 if score @s a_pick_slot matches 1..8 if score @s a_pick_slot <= @s a_max if score @s a_seqpick matches 2..9 if score @s a_seqpick >= @s a_seq if score @s a_pick_path = @s a_partner run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run "+F("ui/menu_assign"),
        "execute if score @s a_ok matches 0 run "+msg("Cannot equip a locked pathway or Sequence.","red"))
    w.f("ui/menu_assign",
        "scoreboard players operation @s a_assign = @s a_pick_slot",
        "scoreboard players operation @s a_assign *= #10000 a_const",
        "scoreboard players operation @s a_rcode = @s a_pick_path",
        "scoreboard players operation @s a_rcode *= #100 a_const",
        "scoreboard players operation @s a_rcode += @s a_seqpick",
        "scoreboard players operation @s a_assign += @s a_rcode",
        F("slot/assign"),
        "scoreboard players set @s a_assign 0",
        "scoreboard players set @s a_pick_slot 0",
        "scoreboard players set @s a_pick_path 0")


def emit_progression(w):
    for card in CARDS:
        slug=card["slug"]
        for phase in ("a","b"):
            crit=({"trigger":"minecraft:inventory_changed","conditions":{
                  "items":[{"items":["minecraft:"+card["acting_item"]]}]}}
                 if phase=="a" else quest(card["acting_event"]))
            w.j(f"data/tarot_arcane/advancements/acting/{slug}_{phase}.json",
                {"criteria":{"acting":crit},"rewards":{"function":PREFIX+f"acting/{slug}_{phase}"}})
            desired=0 if phase=="a" else 1
            w.f(f"acting/{slug}_{phase}",
                f"execute if score @s a_init matches 1 if score @s a_path matches {card['id']} if score @s a_seq matches 2..9 if score @s a_actcd matches 0 if score @s a_phase matches {desired} run "+F("acting/accept_"+phase),
                f"advancement revoke @s only {PREFIX}acting/{slug}_{phase}")
    for phase,next_phase in (("a",1),("b",0)):
        w.f("acting/accept_"+phase,
            "scoreboard players add @s a_marks 1",
            "scoreboard players set @s a_actcd 2400",
            f"scoreboard players set @s a_phase {next_phase}",
            msg("Acting proof accepted (+1 mark); alternate tasks.","green"))
    w.f("ascend/dispatch",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_init matches 1 if score @s a_seq matches 2..9 if score @s a_combat matches 0 if entity @s[nbt={OnGround:1b}] unless entity @s[nbt={FallFlying:1b}] if block ~ ~-1 ~ minecraft:lectern if block ~ ~-2 ~ minecraft:crying_obsidian run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run "+F("ascend/check"),
        "execute if score @s a_ok matches 0 run "+msg("Stand at ritual altar (lectern above crying obsidian), grounded and out of combat.","red"))
    # Snapshot the sequence before dispatch. A successful commit changes
    # a_seq in-place; testing a_seq again could chain several ascensions
    # during ONE /tarot ascend when acting marks and offerings are banked.
    checks=["scoreboard players operation @s a_start_seq = @s a_seq",
            "scoreboard players set @s a_marks_ok 0",
            "scoreboard players set @s a_ok 0"]
    for seq in range(9,1,-1):
        checks += [
            f"execute if score @s a_start_seq matches {seq} if score @s a_marks matches {ACT_MARKS[seq]}.. run scoreboard players set @s a_marks_ok 1",
            f"execute if score @s a_start_seq matches {seq} if score @s a_marks matches {ACT_MARKS[seq]}.. run "+F(f"ascend/check_s{seq}")]
    # Ingredient failure is reported by check_sN, not misreported as an
    # acting-mark failure after that helper resets a_ok.
    checks.append("execute if score @s a_marks_ok matches 0 run "+msg("Not enough acting marks.","red"))
    w.f("ascend/check",checks)
    for seq in range(9,2,-1):
        offerings=list(RITUALS[seq].items())
        (one,n1),(two,n2)=offerings
        w.f(f"ascend/check_s{seq}",
            f"execute store result score @s a_a run clear @s minecraft:{one} 0",
            f"execute store result score @s a_b run clear @s minecraft:{two} 0",
            "scoreboard players set @s a_ok 0",
            f"execute if score @s a_a matches {n1}.. if score @s a_b matches {n2}.. run scoreboard players set @s a_ok 1",
            "execute if score @s a_ok matches 1 run "+F(f"ascend/commit_s{seq}"),
            "execute if score @s a_ok matches 0 run "+msg(f"Requires {n1} {one} and {n2} {two}.","red"))
        commit=[
            f"clear @s minecraft:{one} {n1}",f"clear @s minecraft:{two} {n2}",
            f"scoreboard players remove @s a_marks {ACT_MARKS[seq]}",
            f"scoreboard players set @s a_seq {seq-1}",
            f"scoreboard players set @s a_max {11-seq}"]
        if seq>=6:
            i=11-seq
            commit += [
                f"scoreboard players operation @s a_s{i} = @s a_path",
                f"scoreboard players operation @s a_s{i} *= #100 a_const",
                f"scoreboard players add @s a_s{i} {seq-1}"]
        if seq==5:
            commit += ["scoreboard players set @s a_mode 1",
                       "scoreboard players set @s a_s6 0",
                       msg("Second pathway unlocked! Six editable slots.","light_purple")]
        if seq in (4,3):
            commit += [f"scoreboard players set @s a_s{11-seq} 0",
                       msg("New slot unlocked.","light_purple")]
        w.f(f"ascend/commit_s{seq}",commit,F("powers/refresh"),
            msg(f"Ascended to Sequence {seq-1}.","green"),
            click("[See unlocked abilities]","a_abilities","green"),
            click("[View next ascension goal]","a_roadmap","yellow"))
    # Normal player progression stays fail-closed. Only the operator-set
    # per-player a_rtest flag enables a true, fully-offered Seq2 -> Seq1
    # test transition. No magic "fast forward" / skip / admin OP exposure.
    w.f("ascend/check_s2",
        "execute unless score @s a_rtest matches 1 run " +
        msg("Resonance is locked in normal alpha. An OP can opt in on a BACKED-UP TEST WORLD. No materials consumed.", "red"),
        "execute if score @s a_rtest matches 1 run " +
        F("ascend/check_s2_dev"))
    (first, n1), (second, n2) = tuple(RITUALS[2].items())
    w.f("ascend/check_s2_dev",
        "execute store result score @s a_a run clear @s minecraft:" + first + " 0",
        "execute store result score @s a_b run clear @s minecraft:" + second + " 0",
        "scoreboard players set @s a_ok 0",
        "execute if score @s a_rtest matches 1 if score @s a_seq matches 2 "
        "if score @s a_mode matches 1 "
        f"if score @s a_a matches {n1}.. if score @s a_b matches {n2}.. "
        "run scoreboard players set @s a_ok 1",
        "execute if score @s a_ok matches 1 run " +
        F("ascend/commit_s2_dev"),
        "execute if score @s a_ok matches 0 run " +
        msg(f"Test ascension requires {n1} {first} and {n2} {second}. Nothing taken.", "red"))
    w.f("ascend/commit_s2_dev",
        f"clear @s minecraft:{first} {n1}",
        f"clear @s minecraft:{second} {n2}",
        f"scoreboard players remove @s a_marks {ACT_MARKS[2]}",
        "scoreboard players set @s a_seq 1",
        "scoreboard players set @s a_mode 2",
        "scoreboard players set @s a_max 0",
        [f"scoreboard players set @s a_s{slot} 0" for slot in range(1, 9)],
        "scoreboard players set @s a_pick_slot 0",
        "scoreboard players set @s a_pick_path 0",
        F("powers/refresh"),
        "particle minecraft:enchant ~ ~1 ~ 1 1 1 0.35 120 force @s",
        "playsound minecraft:entity.evoker.prepare_summon master @s ~ ~ ~ 1 0.8",
        msg("RESONANCE TEST ACTIVE: your two pathways have merged into all ten partial source powers. Keep a backup and verify effects!", "light_purple"))


def alias():
    def a(cmd):return {"command":"trigger "+cmd,"commandType":"CLIENT"}
    def lit(label,children=(),actions=()):
        v={"child":str(label),"type":"literal","permission":0}
        if children:v["children"]=list(children)
        if actions:v["actions"]=list(actions)
        return v
    # Finite literal grammar. Numeric commands are encoded; server decodes,
    # validates player-owned pathway and slot, and grants with its own source.
    slots=[]
    for index in range(1,9):
        paths=[]
        for slug,idnum in NUM.items():
            seqs=[lit(seq,actions=[a("a_assign set "+str(index*10000+idnum*100+seq))])
                  for seq in range(9,-1,-1)]
            paths.append(lit("tarot:"+slug,seqs))
        slots.append(lit(index,[lit("clear",actions=[a("a_clear set "+str(index))])]+paths))
    swaps=[lit(i,[lit(j,actions=[a("a_swap set "+str(i*10+j))])
                  for j in range(1,9)]) for i in range(1,9)]
    return {"schemaVersion":1,"commandMode":"COMMAND_CUSTOM","command":"tarot",
            "permission":0,"actions":[a("a_help")],"children":[
                lit("help",actions=[a("a_help")]),
                lit("guide",actions=[a("a_guide")]),
                lit("book",actions=[a("a_book")]),
                lit("tome",actions=[a("a_tome")]),
                lit("abilities",actions=[a("a_abilities")]),
                lit("roadmap",actions=[a("a_roadmap")]),
                lit("stages",actions=[a("a_stages")]),
                lit("kit",[lit(i,actions=[a("a_kit set "+str(i))])
                           for i in range(1,9)]),
                lit("detail",[lit(i,actions=[a("a_detail set "+str(i))])
                              for i in range(1,17)]),
                lit("status",actions=[a("a_status")]),
                lit("slots",actions=[a("a_slots")]),
                lit("focus",[lit("legacy",actions=[a("a_choose set 1")])],
                    actions=[a("a_focus_menu")]),
                lit("ascend",actions=[a("a_ascend")]),
                lit("reset",actions=[a("a_reset")]),
                lit("slot",[lit("auto",actions=[a("a_auto")]),lit("swap",swaps)]+slots)]}


def emit_resonance_manual_preview(output, kits):
    """Separate OP-only test datapack; NEVER included in either live/main variant.

    It has no load/tick entrypoint or player-facing alias. Its source-specific
    revoke deliberately cannot erase identity drawbacks or normal slot grants.
    Manual previews may stack with currently equipped kits; use ONLY in an
    isolated development world and clear powers before removing the pack.
    """
    w = Pack()
    w.j("pack.mcmeta", {"pack": {"pack_format": 9,
        "description": "ARCANE RESONANCE MANUAL PREVIEW ONLY - incomplete / OP use"}})
    w.f("dev/resonance/clear",
        "power revokeall @s " + DEV_PREVIEW_SOURCE,
        msg("Resonance MANUAL PREVIEW cleared; ordinary Arcane slot powers not changed.", "green"))
    entries = []
    for first, second, res in PAIRS:
        powers = [ident for seq in range(9, -1, -1)
                  for ident in kits.get((res, seq), [])]
        if not powers:
            raise ValueError("No concrete Resonance powers for " + res)
        entries.append((res, len(powers)))
        safe = [
            "power revokeall @s " + DEV_PREVIEW_SOURCE,
            *[f"power grant @s {ident} {DEV_PREVIEW_SOURCE}" for ident in powers],
            msg(f"TEST-ONLY preview {res}: {len(powers)}/10 powers; NOT the full Rev3 kit. Use /function tarot_arcane:dev/resonance/clear before leaving.", "yellow"),
        ]
        w.f(f"dev/resonance/execute/{res}", safe)
        w.f(f"dev/resonance/{res}",
            "execute unless score @s a_init matches 1 run " +
            msg("Pick a Tarot Origin before previewing.", "red"),
            "execute if score @s a_paused matches 1 run " +
            msg("Arcane runtime is administratively paused.", "red"),
            f"execute if score @s a_init matches 1 unless score @s a_paused matches 1 run " +
            F(f"dev/resonance/execute/{res}"))
        for ident in powers:
            ability = ident.split("/")[-1]
            w.f(f"dev/resonance/one/{res}/{ability}",
                "power revokeall @s " + DEV_PREVIEW_SOURCE,
                f"power grant @s {ident} {DEV_PREVIEW_SOURCE}",
                msg(f"TEST-ONLY one ability {ident}; clear manual preview before removing the datapack.", "yellow"))
    w.f("dev/resonance/list",
        msg("OP-only manual Resonance test; 11 pairs, incomplete. Not Seq1 progression!", "yellow"),
        [msg(f"{res}: {count}/10 | /function tarot_arcane:dev/resonance/{res}", "aqua")
         for res, count in entries],
        msg("For isolated power tests use /function tarot_arcane:dev/resonance/one/PAIR/ABILITY_ID; /function tarot_arcane:dev/resonance/clear resets source.", "yellow"))
    dest = output / "Arcane_Rev3_Resonance_Manual_Preview_TEST_ONLY_1.18.2.zip"
    with ZipFile(dest, "w", ZIP_DEFLATED, compresslevel=9) as z:
        for path, data in sorted(w.files.items()):
            z.writestr(path, data)
    return dest


def build(root=ROOT,output=None):
    root=Path(root)
    output=Path(output) if output else root/"output"
    output.mkdir(parents=True,exist_ok=True)
    compiled,manifest,kits=compile_powers(root)
    innate = pin_identity_drawbacks(compiled, kits)
    # Client-side active_self must use synced power-token conditions,
    # NOT server-only origins:scoreboard conditions. Legacy all-keys
    # remains the default unless the player selects an owned ability.
    from .active_focus import apply_active_focus
    focus_entries = apply_active_focus(compiled)
    artifacts={}
    for variant in ("only","addon"):
        w=Pack()
        emit_content(w,root,compiled,variant,innate)
        emit_player(w,kits,root)
        emit_slots(w,kits)
        emit_grants(w,kits,innate,focus_entries)
        emit_ui(w)
        from .player_codex import emit_player_codex, emit_roadmap
        emit_player_codex(w,compiled,manifest,kits,innate,NUM)
        emit_roadmap(w)
        from .guide_books import emit_books
        emit_books(w,compiled,manifest,kits)
        from .active_focus import emit_focus
        emit_focus(w,focus_entries)
        emit_progression(w)
        dest=output/f"Arcane_Rev3_22_Origins_{variant.upper()}_DEV_1.18.2.zip"
        with ZipFile(dest,"w",ZIP_DEFLATED,compresslevel=9) as z:
            for key,value in sorted(w.files.items()):z.writestr(key,value)
        artifacts[variant]=dest
    artifacts["resonance_preview"] = emit_resonance_manual_preview(output, kits)
    status={"specified":len(manifest),"compiled":len(compiled),
            "full":sum(x["status"]=="full" for x in manifest),
            "partial":sum(x["status"]=="partial" for x in manifest),
            "blocked":sum(x["status"]=="blocked" for x in manifest),
            "resonance":"FAIL-CLOSED until complete","live_minecraft_test":"NOT RUN"}
    manifest_path=output/"arcane_ability_manifest.json"
    manifest_path.write_text(json.dumps({"summary":status,"abilities":manifest},
                             indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    alias_path=output/"tarot.json"
    alias_path.write_text(json.dumps(alias(),indent=2)+"\n",encoding="utf8")
    from .player_codex import generate_player_manual
    manual_path = output/"Arcane_Rev3_Player_Ability_Reference.md"
    manual_path.write_text(generate_player_manual(manifest,compiled,kits,innate),
                           encoding="utf8")
    artifacts.update(manifest=manifest_path,alias=alias_path,
                     player_manual=manual_path)
    return artifacts


if __name__=="__main__":
    for name,path in build().items():print(name,path)
