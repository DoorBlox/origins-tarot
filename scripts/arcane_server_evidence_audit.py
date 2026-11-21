"""Read-only Fabric 1.18.2 server-evidence audit; NEVER mutates server files.

Accepts raw latest.log OR markdown/html-escaped log extracts plus the two
owner-provided JSON5 configs. This is a launch blocker/reporting aid only;
no datapack/runtime gameplay compatibility is implied by a clean report.
"""
import argparse
import html
import json
import re
from pathlib import Path


REQUIRED = (
    'minecraft', 'fabricloader', 'origins', 'fabric-api',
    'fabric-permissions-api-v0', 'luckperms', 'remorphed', 'skinshifter',
    'pehkui', 'extrakeybinds', 'commandaliases', 'craftedcore', 'walkers',
)


def normalize_log(text):
    """Handle ordinary latest.log and ChatGPT markdown-exported snippets."""
    return (html.unescape(text).replace(r'\-', '-')
            .replace(r'\|', '|').replace(r'\:', ':')
            .replace(r'\*', '*'))


def extract_versions(log):
    text = normalize_log(log)
    mods, within = {}, False
    for line in text.splitlines():
        if re.search(r'Loading\s+\d+\s+mods:', line):
            within = True
            continue
        if not within:
            continue
        if 'SpongePowered MIXIN' in line:
            break
        if ']:**' in line:
            line = line.split(']:**', 1)[-1]
        elif ']: ' in line:
            line = line.split(']: ', 1)[-1]
        clean = line.strip().strip('*').strip()
        match = re.match(r'^(?:-+|\|--|\+--)\s+([a-z][a-z0-9_-]+)\s+(\S+)', clean)
        if match:
            mods[match.group(1)] = match.group(2)
    return mods


def read_json5_subset(path):
    """Only permits JSON + full-line // comments, matching supplied configs.

    No JS evaluation, object keys coercion, dynamic execution or network.
    Refuse unsupported JSON5 features instead of silently misparsing them.
    """
    content = Path(path).read_text(encoding='utf-8')
    clean = '\n'.join(
        line for line in content.splitlines()
        if not line.lstrip().startswith('//')
    )
    data = json.loads(clean)
    if not isinstance(data, dict):
        raise ValueError('Config root must be an object')
    return data


def audit(log, remorphed=None, skinshifter=None):
    text = normalize_log(log)
    versions = extract_versions(log)
    alerts = []

    def warn(level, key, finding):
        alerts.append({'severity': level, 'id': key, 'finding': finding})

    done = bool(re.search(r'\bDone\s*\(\d+(?:\.\d+)?s\)!', text))
    if not done:
        warn('blocker', 'startup_incomplete', 'No Minecraft Done startup line in the supplied log excerpt')
    missing = [name for name in REQUIRED if name not in versions]
    if missing:
        warn('warning', 'required_mods_not_in_log', 'Missing from the captured Fabric mod list: ' + ', '.join(missing))
    if 'OutOfMemoryError' in text:
        warn('blocker', 'heap_oom', 'Java heap exhausted during startup/world generation; do not stress-test the datapack yet')
    if 'OFFLINE/INSECURE MODE' in text:
        warn('blocker', 'unauthenticated_server', 'Minecraft server has online authentication disabled; secure public direct access or verify protected proxy topology')
    if 'Please update your Java runtime to at least Java 21' in text:
        warn('warning', 'via_java_21', 'ViaVersion warns that Java 17 may become unsupported; verify full modpack before changing Java')
    if 'Reference map' in text and 'could not be read' in text:
        warn('info', 'reference_map', 'Missing development refmap warning; not proven fatal by this log')
    if 'Ambiguity between arguments' in text:
        warn('info', 'brigadier_ambiguity', 'Brigadier command ambiguity warnings observed; successful registration is not gameplay acceptance')
    if "Couldn't get patreons" in text or 'UpdateChecker' in text:
        warn('info', 'external_update_fetch', 'Optional mod remote metadata/update checks failed; startup continued')
    if remorphed is not None:
        if 'usePermissions' not in remorphed and versions.get('remorphed', '').startswith('4.2'):
            warn('warning', 'remorphed_legacy_permissions', 'ReMorphed 4.2 config lacks usePermissions; do not apply newer 7.1+ LuckPerms nodes to this installed version')
        if remorphed.get('creativeUnlockAll') is True:
            warn('info', 'creative_morph_all', 'Creative mode unlocks all ReMorphed shapes under current config')
    if skinshifter is not None:
        if skinshifter.get('selfCommandOPLevel') == 0 and skinshifter.get('changeName') is True:
            warn('warning', 'public_self_disguise', 'SkinShifter 1.3 permits level-zero self commands and visual name changes; decide whether unrestricted self-disguise fits the SMP')
        if skinshifter.get('baseCommandOPLevel') != 2:
            warn('warning', 'skinshifter_admin_gate', 'SkinShifter base command is not configured to OP level 2')
    power_match = re.search(r'Finished loading powers from data files\. Registry contains\s+(\d+)\s+powers', text)
    origin_match = re.search(r'Finished loading origins from data files\. Registry contains\s+(\d+)\s+origins', text)
    return {
        'startup_completed': done,
        'log_contains_arcane_datapack_proof': False,
        'versions': versions,
        'required_missing_from_log': missing,
        'baseline_origins_registry': {
            'powers': int(power_match.group(1)) if power_match else None,
            'origins': int(origin_match.group(1)) if origin_match else None,
        },
        'alerts': alerts,
        'ready_for_arcane_load_test': done and not missing and not any(x['severity'] == 'blocker' for x in alerts),
        'arcane_gameplay_verified': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True, help='latest.log or markdown log extract')
    parser.add_argument('--remorphed', type=Path, help='config/remorphed.json5')
    parser.add_argument('--skinshifter', type=Path, help='config/skinshifter.json5')
    parser.add_argument('--json', action='store_true', help='machine-readable output, no secrets echoed')
    args = parser.parse_args(argv)
    report = audit(
        args.log.read_text(encoding='utf-8', errors='replace'),
        read_json5_subset(args.remorphed) if args.remorphed else None,
        read_json5_subset(args.skinshifter) if args.skinshifter else None,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print('Startup:', 'DONE' if report['startup_completed'] else 'NOT CONFIRMED')
        print('Required mod IDs absent:', ', '.join(report['required_missing_from_log']) or 'none')
        print('Registered baseline:', report['baseline_origins_registry'])
        for a in report['alerts']:
            print(a['severity'].upper() + ' [' + a['id'] + ']: ' + a['finding'])
        print('Safe to begin Arcane load test:', report['ready_for_arcane_load_test'])
        print('Arcane gameplay verified: False')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
