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
                record.sin = Math.max(0f,n.getFloat("sin"));
                record.lastSinDamage = n.getLong("sinDamageTick");
                record.killedForRegen = n.getBoolean("killedForRegen");
                record.healingPotionUntil = n.getLong("healingPotionUntil");
                record.darkStillUntil = n.getLong("darkStillUntil");
                record.darkStillTicks = n.getInt("darkStillTicks");
                if(n.contains("markedEntity",NbtElement.INT_ARRAY_TYPE))
                    record.markedEntity=n.getUuid("markedEntity");
                record.markedUntil=n.getLong("markedUntil");
                record.provokedUntil=n.getLong("provokedUntil");
                record.actingMarks=n.getInt("actingMarks");
                record.nextActA=!n.contains("nextActA") || n.getBoolean("nextActA");
                record.onlineTicks=n.getLong("onlineTicks");
                record.lastActingTick=n.contains("lastActingTick")
                    ?n.getLong("lastActingTick"):-2400;
                record.hadActingItem=n.getBoolean("hadActingItem");
                record.lastTradeCount=n.getInt("lastTradeCount");
                record.xpRemainder=n.getFloat("xpRemainder");
                record.reapUntil=n.getLong("reapUntil");
                record.libraryUntil=n.getLong("libraryUntil");
                record.stormUntil=n.getLong("stormUntil");
                record.meteorImmuneUntil=n.getLong("meteorImmuneUntil");
                record.lastBookStudy=n.getLong("lastBookStudy");
                record.burnStacks=n.getInt("burnStacks");
                record.spiritSenseTicks=n.getInt("spiritSenseTicks");
                record.reaperFallUntil=n.getLong("reaperFallUntil");
                record.arcaneAbsorption=n.getFloat("arcaneAbsorption");
                record.arcaneAbsorptionUntil=n.getLong("arcaneAbsorptionUntil");
                record.slamUntil=n.getLong("slamUntil");
                record.divineHitUntil=n.getLong("divineHitUntil");
                record.bulwarkUntil=n.getLong("bulwarkUntil");
                record.dawnCrouchTicks=n.getInt("dawnCrouchTicks");
                record.recordedStepUntil=n.getLong("recordedStepUntil");
                record.recordedStepDimension=n.getString("recordedStepDimension");
                if(n.contains("recordedStepX") && n.contains("recordedStepY") && n.contains("recordedStepZ"))
                    record.recordedStep=new net.minecraft.util.math.BlockPos(
                        n.getInt("recordedStepX"),n.getInt("recordedStepY"),n.getInt("recordedStepZ"));
                record.restoreFlightPending = n.getBoolean("restoreFlightPending");
                record.legendPriorMayFly = n.getBoolean("legendPriorMayFly");
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
            n.putFloat("sin",record.sin);
            n.putLong("sinDamageTick",record.lastSinDamage);
            n.putBoolean("killedForRegen",record.killedForRegen);
            n.putLong("healingPotionUntil",record.healingPotionUntil);
            n.putLong("darkStillUntil",record.darkStillUntil);
            n.putInt("darkStillTicks",record.darkStillTicks);
            if(record.markedEntity!=null)n.putUuid("markedEntity",record.markedEntity);
            n.putLong("markedUntil",record.markedUntil);
            n.putLong("provokedUntil",record.provokedUntil);
            n.putInt("actingMarks",record.actingMarks);
            n.putBoolean("nextActA",record.nextActA);
            n.putLong("onlineTicks",record.onlineTicks);
            n.putLong("lastActingTick",record.lastActingTick);
            n.putBoolean("hadActingItem",record.hadActingItem);
            n.putInt("lastTradeCount",record.lastTradeCount);
            n.putFloat("xpRemainder",record.xpRemainder);
            n.putLong("reapUntil",record.reapUntil);
            n.putLong("libraryUntil",record.libraryUntil);
            n.putLong("stormUntil",record.stormUntil);
            n.putLong("meteorImmuneUntil",record.meteorImmuneUntil);
            n.putLong("lastBookStudy",record.lastBookStudy);
            n.putInt("burnStacks",record.burnStacks);
            n.putInt("spiritSenseTicks",record.spiritSenseTicks);
            n.putLong("reaperFallUntil",record.reaperFallUntil);
            n.putFloat("arcaneAbsorption",record.arcaneAbsorption);
            n.putLong("arcaneAbsorptionUntil",record.arcaneAbsorptionUntil);
            n.putLong("slamUntil",record.slamUntil);
            n.putLong("divineHitUntil",record.divineHitUntil);
            n.putLong("bulwarkUntil",record.bulwarkUntil);
            n.putInt("dawnCrouchTicks",record.dawnCrouchTicks);
            n.putLong("recordedStepUntil",record.recordedStepUntil);
            n.putString("recordedStepDimension",record.recordedStepDimension);
            if(record.recordedStep!=null){
                n.putInt("recordedStepX",record.recordedStep.getX());
                n.putInt("recordedStepY",record.recordedStep.getY());
                n.putInt("recordedStepZ",record.recordedStep.getZ());
            }
            n.putBoolean("restoreFlightPending",record.restoreFlightPending);
            n.putBoolean("legendPriorMayFly",record.legendPriorMayFly);
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
        /** Transient security gate, recalculated using the current Origins selection. */
        public boolean originValid;
        public boolean originChecked;
        public float sin;
        public long lastSinDamage;
        public boolean killedForRegen;
        public long healingPotionUntil;
        public long darkStillUntil;
        public int darkStillTicks;
        public UUID markedEntity;
        public long markedUntil;
        public long provokedUntil;
        public int bowStillTicks;
        public net.minecraft.util.math.BlockPos lastWorldPosition;
        public boolean wasSleeping;
        public int crouchTicks;
        public int actingMarks;
        public boolean nextActA=true;
        public long onlineTicks;
        public long lastActingTick=-2400;
        public boolean hadActingItem;
        public int lastTradeCount;
        public float xpRemainder;
        public long reapUntil;
        public long libraryUntil;
        public long stormUntil;
        public long meteorImmuneUntil;
        public long lastBookStudy;
        public int burnStacks;
        public int spiritSenseTicks;
        public long reaperFallUntil;
        public float arcaneAbsorption;
        public long arcaneAbsorptionUntil;
        public net.minecraft.util.math.BlockPos chargePosition;
        public long chargeUntil;
        public float lastAirFall;
        public boolean wasAirborne;
        public long slamUntil;
        public long divineHitUntil;
        public long bulwarkUntil;
        public int dawnCrouchTicks;
        public net.minecraft.util.math.BlockPos recordedStep;
        public String recordedStepDimension="";
        public long recordedStepUntil;
        /** Crash recovery for temporary capstone flight; only ours is restored. */
        public boolean restoreFlightPending;
        public boolean legendPriorMayFly;
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
