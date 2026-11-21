package club.tarot.arcane;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Only runtime-implemented powers go here. No forged placeholder grants.
 * Native server-side handlers are in FoolAbilities; passive/active JSONs live
 * at the corresponding data/tarot/powers paths in the bundled datapack.
 */
public final class AbilityRegistry {
    private AbilityRegistry() { }
    private static final Map<String, Map<Integer, List<String>>> POWERS = new LinkedHashMap<>();

    static {
        path("fool", 9, "spirit_vision", "clowns_mischief",
            "spiritual_overload", "full_faceless_disguise");
        path("fool", 8, "tricksters_favor");
        path("fool", 7, "stage_magician");
        path("fool", 6, "borrowed_face");
        path("fool", 5, "puppet_string");
        path("fool", 4, "tricksters_escape");
        path("fool", 3, "fools_bounty");
        path("fool", 2, "fools_gathering");
        path("fool", 1, "history_substitution", "paper_figurine_substitute");
        path("fool", 0, "legend_of_the_fool");
    }

    private static void path(String name, int sequence, String... ids) {
        List<String> full = new ArrayList<>();
        for (String id : ids) full.add("tarot:" + name + "/" + sequence + "_" + id);
        POWERS.computeIfAbsent(name, k -> new LinkedHashMap<>()).put(sequence, List.copyOf(full));
    }
    public static List<String> forSequence(String pathway, int sequence) {
        return POWERS.getOrDefault(pathway, Map.of()).getOrDefault(sequence, List.of());
    }
    public static boolean implemented(String pathway, int sequence) {
        return POWERS.containsKey(pathway) && POWERS.get(pathway).containsKey(sequence);
    }
    public static boolean has(String fullId) {
        return POWERS.values().stream().flatMap(map -> map.values().stream())
            .flatMap(List::stream).anyMatch(fullId::equals);
    }
}
