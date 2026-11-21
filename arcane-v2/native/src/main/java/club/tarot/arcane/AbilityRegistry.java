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
        path("hanged_man", 9, "shadow_of_degeneration", "sin_bearing", "graze_the_soul", "weight_of_sin");
        path("hanged_man", 8, "shadow_whisper");
        path("hanged_man", 7, "shadow_cloak");
        path("hanged_man", 6, "flesh_creek");
        path("hanged_man", 5, "burden_bearer");
        path("hanged_man", 4, "dark_blade");
        path("hanged_man", 3, "trinity");
        path("hanged_man", 2, "profane_aura");
        path("hanged_man", 1, "sin_overflow", "depraved_dependent");
        path("hanged_man", 0, "weight_of_sin_made_manifest");
        path("paper_martyr", 9, "burdened_beginning");
        path("paper_martyr", 8, "shadow_step");
        path("paper_martyr", 7, "suffering_sight");
        path("paper_martyr", 6, "borrowed_sacrifice");
        path("paper_martyr", 5, "gathering_of_martyrs");
        path("paper_martyr", 4, "burdened_trickster");
        path("paper_martyr", 3, "suffering_sight_ii");
        path("paper_martyr", 2, "sacrificial_gathering");
        path("paper_martyr", 1, "martyrs_substitute");
        path("paper_martyr", 0, "the_paper_martyr");
        path("world", 9, "cold_precision", "marked_prey", "hunters_tempo", "predators_patience", "terrifying_reputation");
        path("world", 8, "paper_dagger");
        path("world", 7, "air_cannon");
        path("world", 6, "borrowed_face");
        path("world", 5, "puppet_string");
        path("world", 4, "historical_recall");
        path("world", 3, "small_miracle");
        path("world", 2, "mystery_step");
        path("world", 1, "hunters_substitution", "cold_precision_ii");
        path("world", 0, "the_perfect_prey");
        path("justice", 9, "patient_observation", "emotional_recoil", "calming_presence", "therapists_presence", "compassionate_restraint");
        path("justice", 8, "mind_read");
        path("justice", 7, "calm");
        path("justice", 6, "suggestion");
        path("justice", 5, "dream_step");
        path("justice", 4, "emotional_push");
        path("justice", 3, "shared_dream");
        path("justice", 2, "discern");
        path("justice", 1, "authors_edit", "compassionate_restraint_ii");
        path("justice", 0, "the_mindscape");
        path("marked_verdict", 9, "cold_judgment");
        path("marked_verdict", 8, "paper_sentence");
        path("marked_verdict", 7, "hunters_calm");
        path("marked_verdict", 6, "silent_witness");
        path("marked_verdict", 5, "puppets_sentence");
        path("marked_verdict", 4, "marked_judgment");
        path("marked_verdict", 3, "hunters_stillness");
        path("marked_verdict", 2, "the_verdict");
        path("marked_verdict", 1, "swift_judgment");
        path("marked_verdict", 0, "the_marked_verdict");
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
    /** Check native event permission against the actual equipped Sequence kit. */
    public static boolean isActive(SlotModel.Profile profile,String ability) {
        if("resonance".equals(profile.mode())) {
            for(int seq=0;seq<=9;seq++)
                for(String power:forSequence(profile.resonance(),seq))
                    if(power.endsWith("_"+ability)) return true;
            return false;
        }
        for(SlotModel.Choice slot:profile.slots()) {
            if(slot==null) continue;
            for(String power:forSequence(slot.pathway,slot.sequence))
                if(power.endsWith("_"+ability)) return true;
        }
        return false;
    }
    public static boolean has(String fullId) {
        return POWERS.values().stream().flatMap(map -> map.values().stream())
            .flatMap(List::stream).anyMatch(fullId::equals);
    }
}
