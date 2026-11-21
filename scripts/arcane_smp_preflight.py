"""Read-only Tarot datapack identification, collision and upgrade preflight.

Minecraft Java 1.18.2 / Origins 1.4.1. Never edits a world, packs, save or
scoreboard. A passing result only permits further isolated TESTING; it cannot
authorize installation on a production SMP or certify player-data migration.

Usage:
  python -m scripts.arcane_smp_preflight --world /path/to/world --json
  python -m scripts.arcane_smp_preflight --world /path/to/world \\
      --previous-pack old.zip --candidate-pack new.zip --json
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile


ARCANE_LOAD = "data/tarot_arcane/functions/load.mcfunction"
ORIGIN_PREFIX = "data/tarot/origins/"
POWER_PREFIX = "data/tarot/powers/"


def inspect_pack(path):
    """Inspect file signatures, not misleading filenames. Nothing is unpacked."""
    path = Path(path)
    output = {
        "filename": path.name,
        "family": "invalid",
        "is_arcane_rev3": False,
        "pack_format": None,
        "power_ids": [],
        "origin_ids": [],
        "issues": [],
    }
    try:
        if path.is_file():
            with ZipFile(path) as archive:
                files = set(archive.namelist())
                def read(name):
                    return archive.read(name)
                _inspect_contents(output, files, read)
                if archive.testzip():
                    output["issues"].append("crc_error")
        elif path.is_dir():
            # Minecraft also supports an unpacked folder as a datapack.
            # Read only; never recursively follow untrusted symlinks.
            files = {
                p.relative_to(path).as_posix()
                for p in path.rglob("*")
                if p.is_file() and not p.is_symlink()
            }
            def read(name):
                return (path / name).read_bytes()
            _inspect_contents(output, files, read)
        else:
            output["issues"].append("not_a_pack")
    except (BadZipFile, OSError, ValueError, UnicodeError, json.JSONDecodeError, KeyError) as error:
        output["issues"].append("unreadable_archive_or_metadata")
        # Do not print absolute paths, ZIP member data or server player details.
    if output["issues"]:
        output["is_arcane_rev3"] = False
    return output


def _inspect_contents(output, files, read):
    nested_zip = any(name.endswith(".zip") for name in files)
    if "pack.mcmeta" not in files:
        output["family"] = "outer_artifact" if nested_zip else "invalid"
        output["issues"].append(
            "extract_outer_actions_artifact_first" if nested_zip
            else "missing_root_pack_mcmeta")
        return
    pack = json.loads(read("pack.mcmeta").decode("utf-8"))
    value = pack.get("pack", {}).get("pack_format")
    output["pack_format"] = value
    if value != 9:
        output["issues"].append("wrong_minecraft_pack_format")
    origins = {
        name[len(ORIGIN_PREFIX):-5] for name in files
        if name.startswith(ORIGIN_PREFIX)
        and name.endswith(".json")
        and "/" not in name[len(ORIGIN_PREFIX):]
    }
    powers = {
        "tarot:" + name[len(POWER_PREFIX):-5]
        for name in files
        if name.startswith(POWER_PREFIX) and name.endswith(".json")
    }
    output["origin_ids"] = sorted("tarot:" + name for name in origins)
    output["power_ids"] = sorted(powers)
    if ARCANE_LOAD in files and origins:
        output["family"] = "arcane_rev3"
        output["is_arcane_rev3"] = not output["issues"]
    elif origins or powers:
        # V2 and old V3 may share the tarot: namespace but not progression.
        output["family"] = "legacy_tarot"
    else:
        output["family"] = "unrelated"


def audit_world(world):
    """Fail closed if a wrong, duplicate or unextracted pack is present."""
    datapacks = Path(world) / "datapacks"
    blockers = []
    packs = []
    if not datapacks.is_dir():
        blockers.append("datapacks_directory_missing")
    else:
        for candidate in sorted(datapacks.iterdir(), key=lambda p: p.name):
            if candidate.is_symlink():
                continue
            if candidate.is_file() and candidate.suffix.lower() != ".zip":
                continue
            if candidate.is_dir() and not (candidate / "pack.mcmeta").exists():
                continue
            packs.append(inspect_pack(candidate))
    tarot = [p for p in packs if p["family"] in ("arcane_rev3", "legacy_tarot")]
    arcane = [p for p in tarot if p["family"] == "arcane_rev3"]
    legacy = [p for p in tarot if p["family"] == "legacy_tarot"]
    if not arcane:
        blockers.append("arcane_missing")
    if legacy:
        blockers.append("legacy_tarot_present")
    if len(tarot) > 1:
        blockers.append("multiple_tarot_packs")
    if any(p["issues"] for p in arcane):
        blockers.append("arcane_invalid")
    if any(p["family"] == "outer_artifact" for p in packs):
        blockers.append("outer_artifact_uploaded")
    if any(p["family"] == "invalid" for p in packs):
        blockers.append("unreadable_or_invalid_zip")
    test_eligible = not blockers
    return {
        "world_pack_directory_exists": datapacks.is_dir(),
        "pack_family": arcane[0]["family"] if len(arcane) == 1 else None,
        "packs": packs,
        "blockers": blockers,
        "can_test_arcane": test_eligible,
        "ready_for_smp": False,
        "notice": "Even test-eligible source has no new verified 1.18.2 gameplay/upgrade acceptance.",
    }


def compare_upgrade(previous_pack, candidate_pack):
    """Report static ID compatibility, never claim scoreboard or NBT migration."""
    old = inspect_pack(previous_pack)
    new = inspect_pack(candidate_pack)
    missing_powers = sorted(set(old["power_ids"]) - set(new["power_ids"]))
    missing_origins = sorted(set(old["origin_ids"]) - set(new["origin_ids"]))
    blockers = []
    if old["family"] != new["family"] or old["family"] not in ("arcane_rev3",):
        blockers.append("cross_family_migration_unsupported")
    if old["issues"] or new["issues"]:
        blockers.append("unusable_source_archive")
    if missing_powers:
        blockers.append("removed_existing_power_ids")
    if missing_origins:
        blockers.append("removed_existing_origin_ids")
    return {
        "previous_family": old["family"],
        "candidate_family": new["family"],
        "removed_power_ids": missing_powers,
        "removed_origin_ids": missing_origins,
        "blockers": blockers,
        "id_continuity": not blockers,
        "playerdata_migration_verified": False,
        "scoreboard_migration_verified": False,
        "requires_full_backup_and_gameplay_test": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", type=Path, required=True)
    parser.add_argument("--previous-pack", type=Path)
    parser.add_argument("--candidate-pack", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if bool(args.previous_pack) != bool(args.candidate_pack):
        parser.error("--previous-pack and --candidate-pack must be supplied together")
    report = audit_world(args.world)
    if args.previous_pack:
        report["upgrade"] = compare_upgrade(args.previous_pack, args.candidate_pack)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Arcane isolated test eligible:", report["can_test_arcane"])
        print("Tarot packs:", ", ".join(
            f"{pack['filename']} [{pack['family']}]" for pack in report["packs"]))
        for reason in report["blockers"]:
            print("BLOCKER:", reason)
        if args.previous_pack:
            print("Upgrade ID continuity:", report["upgrade"]["id_continuity"])
            print("Upgrade migration: NOT VERIFIED")
        print("Production SMP ready: NO (gameplay and migration not verified)")
    return 0 if report["can_test_arcane"] and (
        not args.previous_pack or report["upgrade"]["id_continuity"]
    ) else 2


if __name__ == "__main__":
    raise SystemExit(main())
