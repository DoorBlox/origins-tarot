"""Read-only, fail-closed Arcane Rev3 ZIP upgrade compatibility guard.

Compare a pull request's compiled ZIP with the ZIP compiled at the exact
base commit, not with a guessed old version. This statically checks IDs
that can be persisted in the world, player power-holder and scoreboard.

It does NOT migrate player saves or prove Minecraft 1.18.2 runtime
acceptance. Use a restorable backup and test upgrades on a world clone.
"""
import argparse
import json
import re
from pathlib import Path
from zipfile import ZipFile

from scripts.arcane_smp_preflight import compare_upgrade, inspect_pack

OBJECTIVE = re.compile(r"^scoreboard objectives add (\S+) (\S+)", re.M)
PLAYER_START = re.compile(
    r"^scoreboard players set @s (a_path|a_partner|a_seq|a_mode|a_s1) (\d+)$",
    re.M,
)
GRANT = re.compile(r"\bpower grant @s ([a-z0-9_]+:[a-z0-9_/-]+) ([a-z0-9_]+:[a-z0-9_/-]+)")
FUNCTION_PREFIX = "data/tarot_arcane/functions/"
ORIGIN_PREFIX = "data/tarot/origins/"
LOAD_FUNCTION = FUNCTION_PREFIX + "load.mcfunction"
LAYER = "data/origins/origin_layers/origin.json"
DESTRUCTIVE = re.compile(
    r"\bscoreboard objectives remove\b|"
    r"\bscoreboard players reset @(?:a|e)\b"
)


def snapshot(path):
    """Read only fixed metadata needed for compatibility; never execute packs."""
    info = inspect_pack(path)
    if info["family"] != "arcane_rev3" or info["issues"]:
        raise ValueError("Not a valid Arcane Rev3 1.18.2 datapack ZIP")
    with ZipFile(path) as z:
        names = set(z.namelist())
        if LOAD_FUNCTION not in names or LAYER not in names:
            raise ValueError("Arcane load function or origins layer missing")
        scripts = {
            name: z.read(name).decode("utf-8")
            for name in names
            if name.startswith(FUNCTION_PREFIX) and name.endswith(".mcfunction")
        }
        objectives = dict(OBJECTIVE.findall(scripts[LOAD_FUNCTION]))
        if not objectives:
            raise ValueError("No scoreboard objectives in Arcane load function")
        origin_ownership = {
            "tarot:" + name[len(ORIGIN_PREFIX):-5]: set(
                json.loads(z.read(name))["powers"])
            for name in names
            if name.startswith(ORIGIN_PREFIX) and name.endswith(".json")
            and "/" not in name[len(ORIGIN_PREFIX):]
        }
        initializers = {
            name: dict(PLAYER_START.findall(source))
            for name, source in scripts.items()
            if name.startswith(FUNCTION_PREFIX + "player/init/")
        }
        grants = set()
        for source in scripts.values():
            grants.update(GRANT.findall(source))
        layer = json.loads(z.read(LAYER))
        harmful_lines = [
            name for name, source in scripts.items()
            if any(DESTRUCTIVE.search(line.split("#", 1)[0])
                   for line in source.splitlines())
        ]
        return {
            "power_ids": set(info["power_ids"]),
            "origin_ids": set(info["origin_ids"]),
            "objectives": objectives,
            "functions": set(scripts),
            "origin_ownership": origin_ownership,
            "initializers": initializers,
            "grant_sources": grants,
            "layer_replace": layer.get("replace"),
            "layer_origins": set(layer.get("origins", [])),
            "destructive_function_ids": sorted(harmful_lines),
        }


def compare_arcane_zips(previous, candidate):
    """Compare static contracts; passing is necessary but not sufficient."""
    result = {
        "previous": Path(previous).name,
        "candidate": Path(candidate).name,
        "static_compatibility": False,
        "gameplay_accepted": False,
        "playerdata_migrated": False,
        "blockers": [],
        "details": {},
    }
    try:
        old = snapshot(previous)
        new = snapshot(candidate)
    except (ValueError, KeyError, OSError, UnicodeError, json.JSONDecodeError) as error:
        # No absolute paths or player details should leak into CI logs.
        result["blockers"] = ["invalid_arcane_archive"]
        return result

    def check(name, delta):
        if delta:
            result["blockers"].append(name)
            result["details"][name] = delta

    check("removed_power_ids", sorted(old["power_ids"] - new["power_ids"]))
    check("removed_origin_ids", sorted(old["origin_ids"] - new["origin_ids"]))
    check("function_id_removed", sorted(old["functions"] - new["functions"]))
    objective_changes = {
        key: {"before": value, "after": new["objectives"].get(key)}
        for key, value in old["objectives"].items()
        if new["objectives"].get(key) != value
    }
    check("scoreboard_objective_changed", objective_changes)
    check("pinned_origin_power_removed", {
        key: sorted(powers - new["origin_ownership"].get(key, set()))
        for key, powers in old["origin_ownership"].items()
        if powers - new["origin_ownership"].get(key, set())
    })
    check("player_initializer_changed", {
        key: {"before": values, "after": new["initializers"].get(key)}
        for key, values in old["initializers"].items()
        if new["initializers"].get(key) != values
    })
    check("grant_source_changed",
          sorted(old["grant_sources"] - new["grant_sources"]))
    check("origin_layer_changed",
          bool(old["layer_replace"] != new["layer_replace"] or
               old["layer_origins"] - new["layer_origins"]))
    check("destructive_scoreboard_command",
          new["destructive_function_ids"])
    result["static_compatibility"] = not result["blockers"]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = compare_arcane_zips(args.previous, args.candidate)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Static upgrade compatibility:", "PASS" if result["static_compatibility"] else "FAIL")
        for reason in result["blockers"]:
            print("BLOCKER:", reason)
        print("Minecraft/gameplay acceptance: NOT RUN")
        print("Playerdata migration: NOT VERIFIED")
    return 0 if result["static_compatibility"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
