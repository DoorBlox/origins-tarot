"""Rev3 datapack-only developer build: 22 origins and genuine scoreboard slots.

No KubeJS or custom Java; all /tarot aliases execute as the player via /trigger.
The full 10-skill Resonance stage deliberately fails closed while [S] skills
remain unimplemented. Never install this alpha over a production world.
"""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from .model import PATHWAYS, PAIRS, PARTNER
from .powers import compile_powers
from progression.catalog import CARDS, ACT_MARKS, RITUALS
from progression.build import quest

ROOT=Path(__file__).resolve().parent.parent
SOURCE="tarot_arcane:slot_grants"
PREFIX="tarot_arcane:"
NUM={slug:i+1 for i,slug in enumerate(PATHWAYS)}
SCORES=("a_init","a_path","a_partner","a_seq","a_mode","a_max","a_marks","a_phase",
        "a_actcd","a_combat","a_clock","a_probe","a_has","a_ok","a_a","a_b",
        "a_rslot","a_rcode","a_rpath","a_rseq","a_swap_a","a_swap_b","a_tmp","a_tmpb",
        "a_s1","a_s2","a_s3","a_s4","a_s5","a_s6","a_s7","a_s8")
TRIGGERS=("a_help","a_status","a_slots","a_assign","a_clear","a_swap",
          "a_auto","a_reset","a_ascend")


def J(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(",",":"))

def F(name):
    return "function "+PREFIX+name

def msg(message,color="gold"):
    return "tellraw @s "+J({"text":"[Tarot] "+message,"color":color})

def score(obj):
    return {"score":{"name":"*","objective":obj}}


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


def emit_content(w,root,compiled,variant):
    from .powers import current_catalog
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
        w.j("data/tarot/origins/"+slug+".json",{
             "powers":wings, "icon":"minecraft:paper", "name":c["name"],
             "description":"Rev3 player-owned slot kits; "+c["lore"],
             "impact":3,"order":c["id"]-1})
        if wings:
            w.j("data/tarot/powers/"+slug+"/wings.json",{
                "type":"origins:elytra_flight","render_elytra":True,
                "name":c["name"]+" Wings",
                "description":"Innate Elytra-style gliding, separate from the removable sequence kit."})
    for a,b,res in PAIRS:
        w.j("data/tarot/origins/"+res+".json",{
            "powers":[],"icon":"minecraft:nether_star",
            "name":"The "+res.replace("_"," ").title(),
            "description":"Resonance for "+a+" + "+b+"; development-only, not selectable.",
            "impact":3,"unchoosable":True})
    for ident,power in compiled.items():
        w.j("data/tarot/powers/"+ident.split(":")[1]+".json",power)


def emit_player(w,kits):
    w.f("load",
        [f"scoreboard objectives add {x} dummy" for x in SCORES],
        [f"scoreboard objectives add {x} trigger" for x in TRIGGERS],
        "scoreboard objectives add a_const dummy",
        "scoreboard players set #10 a_const 10",
        "scoreboard players set #100 a_const 100",
        "scoreboard players set #10000 a_const 10000")
    w.f("tick","execute as @a at @s run "+F("player/tick"))
    w.f("player/tick",
        [f"scoreboard players enable @s {x}" for x in TRIGGERS],
        "execute unless score @s a_init matches 1 run "+F("player/detect"),
        "execute if score @s a_help matches 1.. run "+F("ui/help"),
        "execute if score @s a_status matches 1.. run "+F("ui/status"),
        "execute if score @s a_slots matches 1.. run "+F("ui/slots"),
        "execute if score @s a_assign matches 1.. run "+F("slot/assign"),
        "execute if score @s a_clear matches 1.. run "+F("slot/clear"),
        "execute if score @s a_swap matches 1.. run "+F("slot/swap"),
        "execute if score @s a_auto matches 1.. run "+F("slot/auto"),
        "execute if score @s a_reset matches 1.. run "+F("slot/auto"),
        "execute if score @s a_ascend matches 1.. run "+F("ascend/dispatch"),
        [f"scoreboard players set @s {x} 0" for x in TRIGGERS],
        "execute if score @s a_init matches 1 run scoreboard players add @s a_clock 1",
        "execute if score @s a_actcd matches 1.. run scoreboard players remove @s a_actcd 1",
        "execute if score @s a_combat matches 1.. run scoreboard players remove @s a_combat 1",
        "execute if score @s a_init matches 1 if score @s a_clock matches 600.. run "+F("player/periodic"))
    detection=[]
    for slug,idnum in NUM.items():
        detection.extend([
            "execute unless score @s a_init matches 1 store success score @s a_probe run origin has origin @s origins:origin tarot:"+slug,
            "execute unless score @s a_init matches 1 if score @s a_probe matches 1 run "+F("player/init/"+slug)])
        w.f("player/init/"+slug,
            "scoreboard players set @s a_init 1",
            f"scoreboard players set @s a_path {idnum}",
            f"scoreboard players set @s a_partner {NUM[PARTNER[slug]]}",
            "scoreboard players set @s a_seq 9",
            "scoreboard players set @s a_mode 0",
            "scoreboard players set @s a_max 1",
            "scoreboard players set @s a_marks 0",
            "scoreboard players set @s a_phase 0",
            "scoreboard players set @s a_actcd 0",
            "scoreboard players set @s a_combat 0",
            "scoreboard players set @s a_clock 0",
            f"scoreboard players set @s a_s1 {idnum*100+9}",
            [f"scoreboard players set @s a_s{i} 0" for i in range(2,9)],
            F("powers/refresh"),
            msg("Awakened "+slug+" at Sequence 9. /tarot status for instructions.","aqua"))
    w.f("player/detect",detection)
    verify=[]
    for slug,i in NUM.items():
        verify.extend([
            f"execute if score @s a_path matches {i} store success score @s a_probe run origin has origin @s origins:origin tarot:{slug}",
            f"execute if score @s a_path matches {i} if score @s a_probe matches 0 run origin set @s origins:origin tarot:{slug}"])
    w.f("player/verify",verify)
    w.f("player/periodic","scoreboard players set @s a_clock 0",
        F("player/verify"),F("powers/reconcile"))
    for kind,trigger in (("taken","minecraft:entity_hurt_player"),("dealt","minecraft:player_hurt_entity")):
        w.j("data/tarot_arcane/advancements/events/combat_"+kind+".json",{
            "criteria":{"hit":{"trigger":trigger}},
            "rewards":{"function":PREFIX+"events/combat_"+kind}})
        w.f("events/combat_"+kind,
            "scoreboard players set @s a_combat 200",
            f"advancement revoke @s only {PREFIX}events/combat_{kind}")


def emit_slots(w):
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
        "execute if score @s a_mode matches 1 if score @s a_rslot matches 1..8 if score @s a_rslot <= @s a_max if score @s a_rseq matches 2..9 if score @s a_rseq >= @s a_seq if score @s a_rpath = @s a_path run scoreboard players set @s a_ok 1",
        "execute if score @s a_mode matches 1 if score @s a_rslot matches 1..8 if score @s a_rslot <= @s a_max if score @s a_rseq matches 2..9 if score @s a_rseq >= @s a_seq if score @s a_rpath = @s a_partner run scoreboard players set @s a_ok 1",
        [f"execute unless score @s a_rslot matches {i} if score @s a_rcode = @s a_s{i} run scoreboard players set @s a_ok 0" for i in range(1,9)],
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


def emit_grants(w,kits):
    refresh=["power revokeall @s "+SOURCE]
    repair=[]
    for (slug,seq),powers in sorted(kits.items()):
        if not powers or slug not in NUM:
            continue
        code=NUM[slug]*100+seq
        w.f(f"kits/{slug}/s{seq}",[f"power grant @s {id} {SOURCE}" for id in powers])
        checks=[]
        for ident in powers:
            checks += [
                f"execute store success score @s a_has run power has @s {ident}",
                f"execute if score @s a_has matches 0 run power grant @s {ident} {SOURCE}"]
        w.f(f"kits/{slug}/repair_s{seq}",checks)
        for i in range(1,9):
            refresh.append(f"execute if score @s a_s{i} matches {code} run "+F(f"kits/{slug}/s{seq}"))
            repair.append(f"execute if score @s a_s{i} matches {code} run "+F(f"kits/{slug}/repair_s{seq}"))
    w.f("powers/refresh",refresh)
    w.f("powers/reconcile",repair)
    w.f("admin/rollback_player","power revokeall @s "+SOURCE,msg("Arcane slot powers revoked; progression preserved.","yellow"))
    w.f("admin/rollback_all","execute as @a run "+F("admin/rollback_player"))


def emit_ui(w):
    w.f("ui/help",
        msg("Rev3 | /tarot status | /tarot slots | /tarot ascend","aqua"),
        msg("Seq4-2: /tarot slot N tarot:pathway S; /tarot slot N clear","yellow"),
        msg("/tarot slot auto | /tarot slot swap N M | /tarot reset","yellow"),
        msg("Seq1 Resonance temporarily gated until all 10 pair powers exist.","red"))
    w.f("ui/status",
        "execute unless score @s a_init matches 1 run "+msg("Choose a Tarot origin.","red"),
        "execute if score @s a_init matches 1 run tellraw @s "+J([
            {"text":"[Tarot] Path: ","color":"gold"},score("a_path"),
            {"text":" | Paired: "},score("a_partner"),
            {"text":" | Seq: "},score("a_seq"),
            {"text":" | Slots: "},score("a_max"),
            {"text":" | Acting: "},score("a_marks")]))
    w.f("ui/slots",
        "execute unless score @s a_init matches 1 run "+msg("Choose a Tarot origin.","red"),
        [f"execute if score @s a_init matches 1 if score @s a_max matches {i}.. run tellraw @s "+J([
            {"text":f"[{i}] Kit code: ","color":"aqua"},score(f"a_s{i}")]) for i in range(1,9)],
        "execute if score @s a_mode matches 0 run "+msg("SINGLE mode: automatic kits.","gold"),
        "execute if score @s a_mode matches 1 run "+msg("SLOT mode: 0=empty; kit code=pathID*100+Seq.","yellow"))


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
    checks=["scoreboard players set @s a_ok 0"]
    for seq in range(9,1,-1):
        checks += [
            f"execute if score @s a_seq matches {seq} if score @s a_marks matches {ACT_MARKS[seq]}.. run scoreboard players set @s a_ok 1",
            f"execute if score @s a_seq matches {seq} if score @s a_marks matches {ACT_MARKS[seq]}.. run "+F(f"ascend/check_s{seq}")]
    checks.append("execute if score @s a_ok matches 0 run "+msg("Not enough acting marks.","red"))
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
            msg(f"Ascended to Sequence {seq-1}.","green"))
    w.f("ascend/check_s2",
        msg("Seq1 Resonance is locked until every pair has all ten implemented powers. No materials consumed.","red"))


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
                lit("status",actions=[a("a_status")]),
                lit("slots",actions=[a("a_slots")]),
                lit("ascend",actions=[a("a_ascend")]),
                lit("reset",actions=[a("a_reset")]),
                lit("slot",[lit("auto",actions=[a("a_auto")]),lit("swap",swaps)]+slots)]}


def build(root=ROOT,output=None):
    root=Path(root)
    output=Path(output) if output else root/"output"
    output.mkdir(parents=True,exist_ok=True)
    compiled,manifest,kits=compile_powers(root)
    artifacts={}
    for variant in ("only","addon"):
        w=Pack()
        emit_content(w,root,compiled,variant)
        emit_player(w,kits)
        emit_slots(w)
        emit_grants(w,kits)
        emit_ui(w)
        emit_progression(w)
        dest=output/f"Arcane_Rev3_22_Origins_{variant.upper()}_DEV_1.18.2.zip"
        with ZipFile(dest,"w",ZIP_DEFLATED,compresslevel=9) as z:
            for key,value in sorted(w.files.items()):z.writestr(key,value)
        artifacts[variant]=dest
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
    artifacts.update(manifest=manifest_path,alias=alias_path)
    return artifacts


if __name__=="__main__":
    for name,path in build().items():print(name,path)
