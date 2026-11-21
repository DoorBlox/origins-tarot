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
        path("hermit", 9, "mystery_prying", "astral_calculation", "prepared_investigator", "forbidden_knowledge");
        path("hermit", 8, "combat_insight");
        path("hermit", 7, "hex");
        path("hermit", 6, "scroll");
        path("hermit", 5, "star_read");
        path("hermit", 4, "forbidden_insight");
        path("hermit", 3, "omen");
        path("hermit", 2, "sages_counsel");
        path("hermit", 1, "emperors_library", "prying_eyes");
        path("hermit", 0, "the_unseen");
        path("chariot", 9, "hunters_momentum", "war_rush", "pyromaniac", "trail_of_embers", "extinguished_fury");
        path("chariot", 8, "taunt");
        path("chariot", 7, "flame_burst");
        path("chariot", 6, "plot");
        path("chariot", 5, "reap");
        path("chariot", 4, "iron_skin");
        path("chariot", 3, "rally");
        path("chariot", 2, "storm_call");
        path("chariot", 1, "meteor", "burning_wrath");
        path("chariot", 0, "the_battlefield");
        path("burning_archive", 9, "scholars_fire");
        path("burning_archive", 8, "combat_insight");
        path("burning_archive", 7, "astrologers_trail");
        path("burning_archive", 6, "recorded_plot");
        path("burning_archive", 5, "star_read_reaper");
        path("burning_archive", 4, "scholars_momentum");
        path("burning_archive", 3, "insightful_flame");
        path("burning_archive", 2, "reapers_library");
        path("burning_archive", 1, "burning_lecture");
        path("burning_archive", 0, "the_burning_archive");
        path("death", 9, "soul_harvest", "grave_affinity", "reapers_touch", "grave_whisper", "severed_vitality");
        path("death", 8, "grave_dirt");
        path("death", 7, "spirit_sense");
        path("death", 6, "guide");
        path("death", 5, "gate");
        path("death", 4, "undying");
        path("death", 3, "ferry");
        path("death", 2, "consul");
        path("death", 1, "reap", "grave_affinity_ii");
        path("death", 0, "the_final_harvest");
        path("tower", 9, "ruin_proof", "cracked_foundations", "unstable_strike", "unstable_ground", "falling_tower");
        path("tower", 8, "charge");
        path("tower", 7, "fault_line");
        path("tower", 6, "foundation");
        path("tower", 5, "collapse");
        path("tower", 4, "impact");
        path("tower", 3, "shockwave");
        path("tower", 2, "cataclysm");
        path("tower", 1, "falling_tower", "ruin_proof_ii");
        path("tower", 0, "the_fall");
        path("crumbling_reaper", 9, "grave_ruin");
        path("crumbling_reaper", 8, "grave_dirt_fault_line");
        path("crumbling_reaper", 7, "spirit_shockwave");
        path("crumbling_reaper", 6, "guides_foundation");
        path("crumbling_reaper", 5, "gate_collapse");
        path("crumbling_reaper", 4, "falling_harvest");
        path("crumbling_reaper", 3, "collapse_of_the_living");
        path("crumbling_reaper", 2, "unstable_souls");
        path("crumbling_reaper", 1, "falling_towers_reap");
        path("crumbling_reaper", 0, "the_crumbling_reaper");
        path("magician", 9, "travelers_body", "wayfarers_instinct", "threshold_step", "full_moon_ravings");
        path("magician", 8, "sleight_of_hand");
        path("magician", 7, "star_chart");
        path("magician", 6, "recorded_step");
        path("magician", 5, "doorstep");
        path("magician", 4, "sealed_room");
        path("magician", 3, "shortcut");
        path("magician", 2, "planar_step");
        path("magician", 1, "waypoint", "astral_lock");
        path("magician", 0, "all_paths_converge");
        path("strength", 9, "giants_grip", "quarry_hands", "steel_frame", "grounded_slam", "the_giant_sinks");
        path("strength", 8, "iron_fist");
        path("strength", 7, "masters_grip");
        path("strength", 6, "dawnlight");
        path("strength", 5, "bulwark");
        path("strength", 4, "hunters_bane");
        path("strength", 3, "silver_blade");
        path("strength", 2, "twilight_blade");
        path("strength", 1, "divine_hand", "unyielding");
        path("strength", 0, "the_giants_decay");
        path("impossible_fist", 9, "travelers_might");
        path("impossible_fist", 8, "sleight_of_fist");
        path("impossible_fist", 7, "star_chart_grip");
        path("impossible_fist", 6, "recorded_dawnlight");
        path("impossible_fist", 5, "doorstep_slam");
        path("impossible_fist", 4, "doorstep_punch");
        path("impossible_fist", 3, "sealed_slam");
        path("impossible_fist", 2, "giants_shortcut");
        path("impossible_fist", 1, "divine_door");
        path("impossible_fist", 0, "the_impossible_fist");
        path("emperor", 9, "sovereigns_plate", "distorted_authority", "imperial_presence", "decree_of_the_sovereign", "weight_of_the_crown");
        path("emperor", 8, "unbound");
        path("emperor", 7, "coin");
        path("emperor", 6, "corrupt_ground");
        path("emperor", 5, "decree");
        path("emperor", 4, "fallen_aura");
        path("emperor", 3, "frenzy");
        path("emperor", 2, "entropy_field");
        path("emperor", 1, "abolish", "iron_decree");
        path("emperor", 0, "the_emperors_domain");
        path("lovers", 9, "linked_hearts", "fertile_hands", "shared_refuge", "separation_anxiety");
        path("lovers", 8, "triage");
        path("lovers", 7, "blessing");
        path("lovers", 6, "symbiosis");
        path("lovers", 5, "natures_grasp");
        path("lovers", 4, "transmute");
        path("lovers", 3, "requiem");
        path("lovers", 2, "withering");
        path("lovers", 1, "natures_step", "shared_refuge_ii");
        path("lovers", 0, "the_garden");
        path("benevolent_crown", 9, "sovereigns_care");
        path("benevolent_crown", 8, "unbound_symbiosis");
        path("benevolent_crown", 7, "coins_blessing");
        path("benevolent_crown", 6, "corrupt_symbiosis");
        path("benevolent_crown", 5, "decree_of_nature");
        path("benevolent_crown", 4, "linked_crown");
        path("benevolent_crown", 3, "shared_domain");
        path("benevolent_crown", 2, "emperors_hymn");
        path("benevolent_crown", 1, "triage_decree");
        path("benevolent_crown", 0, "the_benevolent_crown");
        path("devil", 9, "hellborn", "corrupting_claws", "desperate_malice", "infernal_vitality", "sacred_rejection");
        path("devil", 8, "fallen_grace");
        path("devil", 7, "predator");
        path("devil", 6, "devils_mark");
        path("devil", 5, "desire");
        path("devil", 4, "demon_form");
        path("devil", 3, "blather");
        path("devil", 2, "blood_price");
        path("devil", 1, "chaos_unleashed", "infernal_vitality_ii");
        path("devil", 0, "descent");
        path("judgement", 9, "laws_weight", "retaliatory_sentence", "hold_the_line", "verdicts_weight", "no_unlawful_escape");
        path("judgement", 8, "posse");
        path("judgement", 7, "question");
        path("judgement", 6, "verdict");
        path("judgement", 5, "discipline");
        path("judgement", 4, "imperative");
        path("judgement", 3, "chaos_hunter");
        path("judgement", 2, "balance");
        path("judgement", 1, "order", "laws_weight_ii");
        path("judgement", 0, "the_absolute_law");
        path("binding_contract", 9, "hellborn_verdict");
        path("binding_contract", 8, "fallen_question");
        path("binding_contract", 7, "predators_calm");
        path("binding_contract", 6, "devils_verdict");
        path("binding_contract", 5, "desires_discipline");
        path("binding_contract", 4, "infernal_verdict");
        path("binding_contract", 3, "law_of_hell");
        path("binding_contract", 2, "contract_enforcement");
        path("binding_contract", 1, "chaos_law");
        path("binding_contract", 0, "the_binding_contract");
        path("star", 9, "sleepless", "nightwatch", "evernights_patience", "sleepless_vigil", "true_sleeplessness");
        path("star", 8, "lullaby");
        path("star", 7, "nightmare");
        path("star", 6, "soul_shield");
        path("star", 5, "haunt");
        path("star", 4, "nightwatch_ii");
        path("star", 3, "terror");
        path("star", 2, "conceal");
        path("star", 1, "misfortune", "sleepless_vigil_ii");
        path("star", 0, "the_starless_sky");
        path("empress", 9, "witchs_venom", "mirror_veil", "witchs_grace", "reflected_beauty", "exposed_reflection");
        path("empress", 8, "whisper");
        path("empress", 7, "black_fire");
        path("empress", 6, "thread");
        path("empress", 5, "plague_touch");
        path("empress", 4, "aura_of_despair");
        path("empress", 3, "ageless");
        path("empress", 2, "mirror_passage");
        path("empress", 1, "apocalypses_herald", "petrifying_gaze");
        path("empress", 0, "the_mirror_world");
        path("starless_poison", 9, "sleepless_grace");
        path("starless_poison", 8, "lullaby_whisper");
        path("starless_poison", 7, "nightmare_fire");
        path("starless_poison", 6, "soul_thread");
        path("starless_poison", 5, "haunting_plague");
        path("starless_poison", 4, "night_venom");
        path("starless_poison", 3, "poison_conceal");
        path("starless_poison", 2, "shadow_whisper");
        path("starless_poison", 1, "midnight_apocalypse");
        path("starless_poison", 0, "the_starless_poison");
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
