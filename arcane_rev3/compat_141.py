"""Targeted, audited JSON compatibility corrections for Apoli 2.3.3 / Origins 1.4.1.

These transformations address *observed* errors from the owner's real
Minecraft 1.18.2 start log, not guesses about later Origins documentation.
Only the emitted dev ZIP is rewritten; the source catalog remains unchanged.
Every correction is counted and testable; unknown types fail on the next
actual server acceptance instead of being falsely called fully tested.
"""
import copy


REQUIRED_COOLDOWN_TYPES = frozenset({
    "origins:self_action_on_kill",
    "origins:attacker_action_when_hit",
    "origins:self_action_when_hit",
    "origins:target_action_on_hit",
    "origins:self_action_on_hit",
    "origins:action_on_hit",
    "origins:action_when_hit",
    "origins:action_when_damage_taken",
    "origins:self_action_when_hit",
})
UNSUPPORTED = frozenset({
    "origins:random_teleport", "origins:submerged", "origins:not",
})


def _context_for_key(key, current):
    if key in ("condition", "entity_condition"):
        return "item_condition" if current == "item_condition" else "entity_condition"
    if key == "item_condition":
        return "item_condition"
    if key == "block_condition":
        return "block_condition"
    if key == "damage_condition":
        return "damage_condition"
    if key in ("entity_action", "action", "rising_action", "falling_action",
               "bientity_action", "actor_action", "target_action"):
        return "entity_action"
    if key in ("actions", "conditions", "action_on_item"):
        return current
    return current


def adapt_141(power):
    """Return (deep-copied power, chance predicates, adaptation counters).

    Minecraft random-chance loot predicates are evaluated per server event;
    unlike a scoreboard time-slot, these do not give a predictable
    20-tick exploit window for a prevent-death power. They are invoked only
    inside server-side Origins entity-condition fields.
    """
    chances = set()
    changes = []

    def walk(value, context):
        if isinstance(value, list):
            return [walk(x, context) for x in value]
        if not isinstance(value, dict):
            return value
        item = copy.deepcopy(value)
        kind = item.get("type")
        if kind == "origins:not" and context == "item_condition":
            child = item.get("condition")
            if not isinstance(child, dict):
                raise ValueError("Invalid item NOT without condition")
            converted = walk(child, "item_condition")
            converted["inverted"] = not converted.get("inverted", False)
            changes.append("item_condition:not_to_inverted")
            return converted
        if kind == "origins:chance" and context == "entity_condition":
            chance = item.get("chance")
            if not isinstance(chance, (int, float)) or not 0 < chance <= 1:
                raise ValueError("Invalid random chance condition")
            basis = round(chance * 1000000)
            if not 1 <= basis <= 1000000 or abs(basis / 1000000 - chance) > 1e-8:
                raise ValueError("Unrepresentable 1.18.2 random predicate chance")
            chances.add(basis)
            changes.append("entity_condition:chance_to_vanilla_predicate")
            return {"type": "origins:predicate",
                    "predicate": f"tarot_arcane:chance/{basis}"}
        if kind == "origins:submerged" and context == "entity_condition":
            item["type"] = "origins:submerged_in"
            item.setdefault("fluid", "minecraft:water")
            changes.append("entity_condition:submerged_in_water")
        if kind == "origins:random_teleport" and context == "entity_action":
            width = item.get("area_width", 8)
            if isinstance(width, bool) or not isinstance(width, (int, float)):
                raise ValueError("Unbounded teleport fallback")
            if not 1 <= width <= 16 or int(width) != width:
                raise ValueError("Teleport fallback requires 1..16-block range")
            # The server's 1.4.1 action registry does not contain the
            # modern random_teleport entity action. /spreadplayers is vanilla
            # 1.18.2. Restrict it to the Overworld and a small local radius.
            # It is a SURFACE blink, not a loaded-chunk-safe 3D teleport.
            changes.append("entity_action:bounded_overworld_surface_blink")
            return {
                "type": "origins:execute_command",
                "permission_level": 2,
                "command": ("execute at @s if dimension minecraft:overworld "
                            f"run spreadplayers ~ ~ 0 {int(width)} false @s"),
            }
        if kind == "origins:ingredient" and context == "item_condition":
            ing = item.get("ingredient")
            if isinstance(ing, dict) and isinstance(ing.get("items"), list):
                names = ing["items"]
                if not names or any(not isinstance(x, str)
                                    or not x.startswith("minecraft:")
                                    for x in names):
                    raise ValueError("Invalid multi-item ingredient")
                changes.append("item_condition:ingredient_items_to_or")
                common = {k: v for k, v in item.items()
                          if k not in ("type", "ingredient")}
                return {
                    **common, "type": "origins:or",
                    "conditions": [
                        {"type": "origins:ingredient", "ingredient": {"item": x}}
                        for x in names],
                }

        for key, subvalue in list(item.items()):
            if isinstance(subvalue, (list, dict)):
                item[key] = walk(subvalue, _context_for_key(key, context))
        if kind in REQUIRED_COOLDOWN_TYPES and context == "power" and "cooldown" not in item:
            # An explicit one-second minimum prevents unbounded event spam.
            item["cooldown"] = 20
            changes.append("power:missing_cooldown_20_ticks")
        if kind == "origins:invisibility" and context == "power" and "render_armor" not in item:
            item["render_armor"] = False
            changes.append("power:missing_render_armor_false")
        return item

    result = walk(power, "power")
    return result, chances, changes


def chance_predicate(basis):
    if not isinstance(basis, int) or not 1 <= basis <= 1000000:
        raise ValueError("Invalid chance basis")
    # Minecraft Java 1.18.2 loot predicates use the 'condition' field.
    return {"condition": "minecraft:random_chance",
            "chance": basis / 1000000}
