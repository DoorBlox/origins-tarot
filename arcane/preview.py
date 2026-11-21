"""Build an optional Origins 1.4.1 test pack from the Arcane handbook's reviewed native templates.

Not all 434 specifications are implemented. In particular, no untested team-targeting
powers or full Resonance Origin forms are enabled. The V3 production build is unchanged.
"""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from progression.build import build_all
from progression.catalog import CARDS

SOURCE = "tarot_arcane:sequence"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def dumped(value):
    return (json.dumps(value,indent=2,ensure_ascii=False)+"\n").encode("utf-8")

def validate(root):
    catalog=read_json(root/"arcane/catalog.json")
    templates=read_json(root/"arcane/templates.json")
    origins={c["slug"]:c for c in catalog["individual"]}
    if len(origins)!=22 or len(catalog["resonance"])!=11:
        raise ValueError("Expected 22 personal and 11 proposed Resonance forms")
    if len(templates)!=22 or {t["slug"] for t in templates}!=set(origins):
        raise ValueError("Exactly one real native power per base Arcana required")
    seen=set()
    for entry in templates:
        slug,seq,name=entry["slug"],entry["sequence"],entry["name"]
        if (slug,seq,name) in seen:raise ValueError("Duplicate native template")
        seen.add((slug,seq,name))
        doc=[p for level in origins[slug]["sequences"] if level["sequence"]==seq
             for p in level["abilities"] if p["name"]==name]
        if len(doc)!=1 or doc[0]["flag"]=="S":
            raise ValueError(f"Not a valid native [D]/[D/S] source: {slug}:{seq}:{name}")
        if entry["accuracy"] not in ("full","partial"):
            raise ValueError("Missing implementation status")
        if entry["accuracy"]=="partial" and not entry.get("missing"):
            raise ValueError("Missing-part disclosure required")
        if not entry["power"].get("name") or not entry["power"].get("description"):
            raise ValueError("Missing playable power text")
        if not entry["power"].get("type","").startswith("origins:"):
            raise ValueError("Invalid power type")
        if entry["power"]["type"]=="origins:simple":
            raise ValueError("No-op placeholders are not implementations")
    return catalog,templates

def make_variant(root,variant,source,catalog,templates,tags):
    with ZipFile(source) as z:
        contents={name:z.read(name) for name in z.namelist() if not name.endswith("/")}
    ref="data/tarot_progress/functions/powers/refresh.mcfunction"
    if ref not in contents or SOURCE in contents[ref].decode("utf-8"):
        raise ValueError("Expected exactly one unmodified V3 refresh function")
    groups={c["slug"]:c for c in catalog["individual"]}
    grants={slug:[] for slug in groups}
    compiled={}
    for t in templates:
        slug,seq,name=t["slug"],t["sequence"],t["name"]
        doc=next(p for q in groups[slug]["sequences"] if q["sequence"]==seq
                 for p in q["abilities"] if p["name"]==name)
        ident=f"tarot:{slug}/{seq}_{doc['slug']}"
        filepath=f"data/tarot/powers/{slug}/{seq}_{doc['slug']}.json"
        if filepath in contents:
            raise ValueError("Colliding power ID "+filepath)
        contents[filepath]=dumped(t["power"])
        grants[slug].append(f"execute if score @s tc_curseq matches ..{seq} run power grant @s {ident} {SOURCE}")
        compiled[f"{slug}:{seq}:{doc['slug']}"]={"accuracy":t["accuracy"],"missing":t["missing"]}
    for slug,lines in grants.items():
        contents[f"data/tarot_arcane/functions/grant/{slug}.mcfunction"]=("\n".join(lines)+"\n").encode()
    lines=["power revokeall @s "+SOURCE]
    lines.extend(f"execute if score @s tc_current matches {c['id']} run function tarot_arcane:grant/{c['slug']}"
                 for c in CARDS)
    contents[ref]+=("\n".join(lines)+"\n").encode()
    for category,items in tags.items():
        if not items or any(not isinstance(item,str) for item in items):
            raise ValueError("Malformed tag "+category)
        contents[f"data/tarot/tags/{category}.json"]=dumped({
            "replace":False,"values":["minecraft:"+item for item in items]})
    total=sum(len(level["abilities"]) for c in catalog["individual"]+catalog["resonance"]
              for level in c["sequences"])
    contents["ARCANE_PREVIEW_STATUS.json"]=dumped({
        "status":"ALPHA / IN-GAME TESTING NOT RUN; DO NOT REPLACE MAIN SMP PACK",
        "document":"docs/HisyamOrigins.txt",
        "specified_entries":total,
        "compiled_entries":compiled,
        "resonance_forms_live":False,
        "primary_and_secondary_full_slots":1,
        "second_arcana_unlock_sequence":4,
        "portable_swap_sequence":3,
        "echo_sequence":2,
        "resonance_sequence":1,
        "deferred":"Remaining entries need strict Origins/KubeJS version verification and team-safe targeting."
    })
    outfile=root/"output"/f"The_Tarot_Club_Arcane_Preview_{variant.upper()}_1.18.2.zip"
    outfile.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(outfile,"w",ZIP_DEFLATED,compresslevel=9) as z:
        for path,data in sorted(contents.items()):z.writestr(path,data)
    return outfile

def build(root=None):
    root=Path(root or Path(__file__).resolve().parent.parent)
    catalog,templates=validate(root)
    tags=read_json(root/"arcane/tags.json")
    originals=build_all(root)
    return {name:make_variant(root,name,path,catalog,templates,tags)
            for name,path in originals.items()}

if __name__=="__main__":
    for variant,archive in build().items():
        print(variant,archive,archive.stat().st_size)
