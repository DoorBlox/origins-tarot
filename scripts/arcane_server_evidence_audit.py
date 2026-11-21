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


def audit(log, remorphed=None, skinshifter=None, *,
          acknowledge_worldgen_oom=False, intentional_offline_mode=False):
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
    # Explicit owner acknowledgements change the DEVELOPMENT smoke-test gate,
    # not the underlying observation, authentication risk or release policy.
    oom_observed = 'OutOfMemoryError' in text
    offline_observed = 'OFFLINE/INSECURE MODE' in text
    if oom_observed:
        accepted = acknowledge_worldgen_oom and done
        warn('warning' if accepted else 'blocker', 'heap_oom',
             'Java heap exhausted during startup/world generation. ' +
             ('Owner accepted one-time fresh-world generation risk; monitor '
              'subsequent chunk generation and abort on repeated OOM.' if accepted
              else 'Requires acknowledgement or investigation before development smoke test.'))
    if offline_observed:
        warn('warning' if intentional_offline_mode else 'blocker',
             'unauthenticated_server',
             'Server intentionally operates offline per owner; usernames '
             'are not authenticated and public/direct access remains spoofable.'
             if intentional_offline_mode else
             'Minecraft server authentication disabled; verify whether this '
             'is deliberate and protect against username spoofing.')
    if 'Please update your Java runtime to at least Java 21' in text:
        warn('warning', 'via_java_21', 'ViaVersion warns that Java 17 may become unsupported; verify full modpack before changing Java')
    if 'Reference map' in text and 'could not be read' in text:
        warn('info', 'reference_map', 'Missing development refmap warning; not proven fatal by this log')
    if 'Ambiguity between arguments' in text:
        warn('info', 'brigadier_ambiguity', 'Brigadier command ambiguity warnings observed; successful registration is not gameplay acceptance')
    if "Couldn't get patreons" in text or 'UpdateChecker' in text:
        warn('info', 'external_update_fetch', 'Optional mod remote metadata/update checks failed; startup continued')
    # Actual SMP user report: the server ran V2 after Arcane was removed.
    # Neither a "Done" line nor mod-registry counts establish Arcane validity.
    missing_arcane = bool(re.search(
        r'Missing data pack file/Arcane_Rev3_[^\\s]+\\.zip', text))
    loaded_arcane = bool(re.search(
        r'Found new data pack file/Arcane_Rev3_[^\\s]+\\.zip', text))
    loaded_legacy = bool(re.search(
        r'Found new data pack file/The_Tarot_Club_[^\\s]+\\.zip', text))
    if missing_arcane and not loaded_arcane:
        warn('blocker', 'arcane_datapack_missing',
             'World references Arcane Rev3, but its archive is missing; use the Arcane-specific build artifact, not the legacy V2 action.')
    if loaded_legacy:
        warn('blocker', 'legacy_tarot_pack_loaded',
             'Legacy Tarot V2/V3 detected in this Arcane test; never mix it with Rev3.')
    if re.search(r'There was a problem reading power file tarot:[^\\n]+\\(skipping\\)', text):
        warn('blocker', 'tarot_power_decoder_error',
             'At least one tarot power failed Apoli decoding; inspect the private log for the exact JSON error.')
    if re.search(r'Origin \\"tarot:[^\\n]+contained unregistered power:', text):
        warn('blocker', 'tarot_unregistered_power',
             'An Arcana Origin references a skipped or missing power definition.')
    if re.search(
            r'Error while reading power holder data: Could not get power type from id [\\\'\\"]tarot:', text):
        warn('blocker', 'saved_power_missing',
             'Saved player data references a power not currently registered. Preserve backup; do not delete playerdata.')
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
        'owner_acknowledged_conditions': {
            'first_worldgen_heap_oom': bool(oom_observed and acknowledge_worldgen_oom and done),
            'intentional_offline_mode': bool(offline_observed and intentional_offline_mode),
        },
        'ready_for_arcane_load_test': done and not missing and not any(x['severity'] == 'blocker' for x in alerts),
        'arcane_gameplay_verified': False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True, help='latest.log or markdown log extract')
    parser.add_argument('--remorphed', type=Path, help='config/remorphed.json5')
    parser.add_argument('--skinshifter', type=Path, help='config/skinshifter.json5')
    parser.add_argument('--acknowledge-worldgen-oom', action='store_true',
                        help='Owner accepts first-world generation OOM risk for a dev smoke test;'
                             ' NOT a claim it cannot recur')
    parser.add_argument('--intentional-offline-mode', action='store_true',
                        help='Owner confirms offline authentication mode is intentional;'
                             ' does NOT provide identity security')
    parser.add_argument('--json', action='store_true', help='machine-readable output, no secrets echoed')
    args = parser.parse_args(argv)
    report = audit(
        args.log.read_text(encoding='utf-8', errors='replace'),
        read_json5_subset(args.remorphed) if args.remorphed else None,
        read_json5_subset(args.skinshifter) if args.skinshifter else None,
        acknowledge_worldgen_oom=args.acknowledge_worldgen_oom,
        intentional_offline_mode=args.intentional_offline_mode,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print('Startup:', 'DONE' if report['startup_completed'] else 'NOT CONFIRMED')
        print('Required mod IDs absent:', ', '.join(report['required_missing_from_log']) or 'none')
        print('Registered baseline:', report['baseline_origins_registry'])
        for a in report['alerts']:
            print(a['severity'].upper() + ' [' + a['id'] + ']: ' + a['finding'])
        print('Owner-acknowledged development conditions:', report['owner_acknowledged_conditions'])
        print('Development smoke-test preflight:', report['ready_for_arcane_load_test'])
        print('Arcane gameplay verified: False')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
