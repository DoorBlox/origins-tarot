package club.tarot.arcane;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.nbt.NbtElement;
import net.minecraft.nbt.NbtList;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.PersistentState;

/** Authoritative, world-persistent per-UUID state; survives respawns and relogs. */
public final class ArcaneSave extends PersistentState {
    public static final String STORAGE_KEY = "tarot_arcane_v2";
    public final Map<UUID, Record> players = new HashMap<>();

    public static ArcaneSave get(MinecraftServer server) {
        return server.getOverworld().getPersistentStateManager()
            .getOrCreate(ArcaneSave::readNbt, ArcaneSave::new, STORAGE_KEY);
    }
    public static ArcaneSave readNbt(NbtCompound root) {
        ArcaneSave state = new ArcaneSave();
        NbtList records = root.getList("players", NbtElement.COMPOUND_TYPE);
        for (int i = 0; i < records.size(); i++) {
            NbtCompound n = records.getCompound(i);
            try {
                String primary = n.getString("primary");
                if (!SlotModel.PAIRS.containsKey(primary)) continue;
                Record record = new Record(new SlotModel.Profile(primary));
                int sequence = n.getInt("sequence");
                if (sequence >= 0 && sequence <= 9) record.profile.onSequenceChange(sequence);
                NbtList slots = n.getList("slots", NbtElement.COMPOUND_TYPE);
                List<SlotModel.Choice> choices = new ArrayList<>();
                for (int j = 0; j < slots.size(); j++) {
                    NbtCompound sn = slots.getCompound(j);
                    choices.add(sn.getBoolean("filled")
                        ? new SlotModel.Choice(sn.getString("pathway"), sn.getInt("sequence")) : null);
                }
                record.profile.restoreSlots(choices);
                NbtCompound cooldowns = n.getCompound("cooldowns");
                for (String key : cooldowns.getKeys()) record.cooldowns.put(key, cooldowns.getLong(key));
                record.combatUntil = n.getLong("combatUntil");
                record.foodRemainder = n.getFloat("foodRemainder");
                record.primaryBinding = n.contains("bindPrimary") ? n.getString("bindPrimary") : "full_faceless_disguise";
                record.secondaryBinding = n.contains("bindSecondary") ? n.getString("bindSecondary") : "spirit_vision";
                state.players.put(n.getUuid("uuid"), record);
            } catch (RuntimeException ignored) {
                // Reject only malformed per-player records, never wipe other players.
            }
        }
        return state;
    }
    @Override public NbtCompound writeNbt(NbtCompound root) {
        NbtList records = new NbtList();
        for (Map.Entry<UUID, Record> entry : players.entrySet()) {
            Record record = entry.getValue();
            NbtCompound n = new NbtCompound();
            n.putUuid("uuid", entry.getKey());
            n.putString("primary", record.profile.primary());
            n.putInt("sequence", record.profile.sequence());
            NbtList slots = new NbtList();
            for (SlotModel.Choice c : record.profile.slots()) {
                NbtCompound sn = new NbtCompound();
                sn.putBoolean("filled", c != null);
                if (c != null) {
                    sn.putString("pathway", c.pathway);
                    sn.putInt("sequence", c.sequence);
                }
                slots.add(sn);
            }
            n.put("slots", slots);
            NbtCompound cds = new NbtCompound();
            record.cooldowns.forEach(cds::putLong);
            n.put("cooldowns", cds);
            n.putLong("combatUntil", record.combatUntil);
            n.putFloat("foodRemainder", record.foodRemainder);
            n.putString("bindPrimary",record.primaryBinding);
            n.putString("bindSecondary",record.secondaryBinding);
            records.add(n);
        }
        root.put("players", records);
        return root;
    }
    public Record enroll(UUID uuid, String pathway) {
        return players.computeIfAbsent(uuid, k -> {
            markDirty();
            return new Record(new SlotModel.Profile(pathway));
        });
    }
    public Record getPlayer(UUID uuid) { return players.get(uuid); }

    public static final class Record {
        public final SlotModel.Profile profile;
        public final Map<String, Long> cooldowns = new HashMap<>();
        public long combatUntil;
        public float foodRemainder;
        public String primaryBinding="full_faceless_disguise";
        public String secondaryBinding="spirit_vision";
        private Record(SlotModel.Profile profile) { this.profile = profile; }

        public boolean ready(String key, long now, int ticks) {
            long last = cooldowns.getOrDefault(key, Long.MIN_VALUE / 2);
            if (last > now) last = 0; // handles world-time reset/restore
            if (now - last < ticks) return false;
            cooldowns.put(key, now);
            return true;
        }
        public boolean inCombat(long now) { return now < combatUntil; }
        public void combat(long now) { combatUntil = Math.max(combatUntil, now + 200); }
    }
}
