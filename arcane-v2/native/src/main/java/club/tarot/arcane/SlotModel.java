package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/**
 * Pure, testable Rev 3 state machine. No Minecraft APIs are used here.
 * A slot grants an entire Sequence kit, never an individual ability.
 */
public final class SlotModel {
    private SlotModel() { }

    public static final Map<String, String> PAIRS = new HashMap<>();
    public static final Map<String, String> RESONANCES = new HashMap<>();
    static {
        pair("fool", "hanged_man", "paper_martyr");
        pair("world", "justice", "marked_verdict");
        pair("hermit", "chariot", "burning_archive");
        pair("death", "tower", "crumbling_reaper");
        pair("magician", "strength", "impossible_fist");
        pair("emperor", "lovers", "benevolent_crown");
        pair("devil", "judgement", "binding_contract");
        pair("star", "empress", "starless_poison");
        pair("sun", "moon", "eclipse");
        pair("temperance", "hierophant", "walking_sanctuary");
        pair("high_priestess", "wheel_of_fortune", "loaded_dice");
    }

    private static void pair(String a, String b, String resonance) {
        PAIRS.put(a, b);
        PAIRS.put(b, a);
        RESONANCES.put(a, resonance);
        RESONANCES.put(b, resonance);
    }

    public static String paired(String origin) { return PAIRS.get(origin); }
    public static String resonance(String origin) { return RESONANCES.get(origin); }

    public static final class Choice {
        public final String pathway;
        public final int sequence;
        public Choice(String pathway, int sequence) {
            this.pathway = Objects.requireNonNull(pathway);
            this.sequence = sequence;
        }
        @Override public boolean equals(Object other) {
            if (!(other instanceof Choice)) return false;
            Choice c = (Choice) other;
            return pathway.equals(c.pathway) && sequence == c.sequence;
        }
        @Override public int hashCode() { return Objects.hash(pathway, sequence); }
        @Override public String toString() { return pathway + " " + sequence; }
    }

    public static final class Profile {
        private final String primary;
        private int sequence;
        private final List<Choice> slots = new ArrayList<>();

        public Profile(String primary) {
            if (!PAIRS.containsKey(primary)) throw new IllegalArgumentException("Unknown Arcana: " + primary);
            this.primary = primary;
            this.sequence = 9;
            this.slots.add(new Choice(primary, 9));
        }
        public String primary() { return primary; }
        public String secondary() { return sequence <= 4 ? PAIRS.get(primary) : null; }
        public String resonance() { return RESONANCES.get(primary); }
        public int sequence() { return sequence; }
        public String mode() { return sequence <= 1 ? "resonance" : (sequence <= 4 ? "slot" : "single"); }
        public int maxSlots() { return sequence <= 1 ? 0 : 10 - sequence; }
        public List<Choice> slots() { return Collections.unmodifiableList(slots); }

        public boolean active(String pathway, int abilitySequence) {
            if (abilitySequence < 0 || abilitySequence > 9) return false;
            if ("resonance".equals(mode())) return resonance().equals(pathway);
            return slots.contains(new Choice(pathway, abilitySequence));
        }

        /** Called by the actual progression/sequence-up handler, never from a client packet. */
        public void onSequenceChange(int next) {
            if (next < 0 || next > sequence) throw new IllegalArgumentException("Sequence must descend 9 to 0");
            if (next == sequence) return;
            final int previous = sequence;
            sequence = next;
            if (sequence <= 1) {
                slots.clear();
                return;
            }
            if (sequence >= 5) {
                slots.clear();
                for (int s = 9; s >= sequence; --s) slots.add(new Choice(primary, s));
                return;
            }
            if (previous > 4) {
                // At 5 -> 4, preserve exactly the five equipped primary kits.
                slots.clear();
                for (int s = 9; s >= 5; --s) slots.add(new Choice(primary, s));
            }
            while (slots.size() < maxSlots()) slots.add(null);
            while (slots.size() > maxSlots()) slots.remove(slots.size() - 1);
        }

        public void setSlot(int oneBasedIndex, String pathway, int seq) {
            requireSlotMode();
            int index = oneBasedIndex - 1;
            checkIndex(index);
            if (!primary.equals(pathway) && !PAIRS.get(primary).equals(pathway))
                throw new IllegalArgumentException("Pathway is not one of your registered pair");
            if (seq < sequence || seq > 9)
                throw new IllegalArgumentException("You have not unlocked that Sequence");
            Choice choice = new Choice(pathway, seq);
            if (slots.contains(choice) && !choice.equals(slots.get(index)))
                throw new IllegalArgumentException("Sequence kit already assigned to another slot");
            slots.set(index, choice);
        }
        public void clearSlot(int oneBasedIndex) {
            requireSlotMode(); checkIndex(oneBasedIndex - 1); slots.set(oneBasedIndex - 1, null);
        }
        public void swap(int a, int b) {
            requireSlotMode(); checkIndex(a - 1); checkIndex(b - 1);
            Collections.swap(slots, a - 1, b - 1);
        }
        public void auto() {
            requireSlotMode();
            slots.clear();
            // Highest available = lowest numbered unlocked Sequence first.
            for (int s = sequence; s <= 9 && slots.size() < maxSlots(); ++s)
                slots.add(new Choice(primary, s));
            while (slots.size() < maxSlots()) slots.add(null);
        }
        public void reset() {
            requireSlotMode();
            slots.clear();
            for (int s = 9; s >= sequence && slots.size() < maxSlots(); --s)
                slots.add(new Choice(primary, s));
            while (slots.size() < maxSlots()) slots.add(null);
        }
        public void restoreSlots(List<Choice> saved) {
            if (!"slot".equals(mode())) return;
            slots.clear();
            Set<Choice> seen = new HashSet<>();
            for (int i = 0; i < maxSlots(); ++i) {
                Choice c = i < saved.size() ? saved.get(i) : null;
                boolean valid = c != null && (c.pathway.equals(primary)
                    || c.pathway.equals(secondary())) && c.sequence >= sequence
                    && c.sequence <= 9 && seen.add(c);
                slots.add(valid ? c : null);
            }
        }
        private void requireSlotMode() {
            if (!"slot".equals(mode())) throw new IllegalStateException("Slots are editable only at Sequence 4-2");
        }
        private void checkIndex(int index) {
            if (index < 0 || index >= maxSlots()) throw new IllegalArgumentException("Slot outside 1.." + maxSlots());
        }
    }
}
