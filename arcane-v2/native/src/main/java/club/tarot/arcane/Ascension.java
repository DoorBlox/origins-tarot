package club.tarot.arcane;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.block.Blocks;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.stat.Stats;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.registry.Registry;

/**
 * Optional no-KubeJS, survival-friendly acting and ritual bridge based on the
 * existing repository's V3 Path of Ascension economy. Rev3's sequence timing
 * and pair/slot rules always override V3. No player needs OP to ascend.
 */
public final class Ascension {
    private Ascension() {}
    private record Objective(Item item,EntityType<?> victimType,boolean trade) {}
    private record Offering(Item item,int count) {}
    private static final Map<String,Objective> ACTS=Map.of(
        "fool",new Objective(Items.COMPASS,EntityType.SPIDER,false),
        "hanged_man",new Objective(Items.KELP,EntityType.DROWNED,false),
        "world",new Objective(Items.CROSSBOW,EntityType.PILLAGER,false),
        "justice",new Objective(Items.HONEY_BOTTLE,null,true),
        "hermit",new Objective(Items.LAPIS_LAZULI,null,true),
        "chariot",new Objective(Items.FLINT_AND_STEEL,EntityType.BLAZE,false),
        "death",new Objective(Items.BONE,EntityType.SKELETON,false),
        "tower",new Objective(Items.TNT,EntityType.CREEPER,false)
    );
    private static final Map<Integer,List<Offering>> OFFERINGS=new HashMap<>();
    static {
        OFFERINGS.put(9,List.of(new Offering(Items.AMETHYST_SHARD,6),
            new Offering(Items.LAPIS_LAZULI,8)));
        OFFERINGS.put(8,List.of(new Offering(Items.COPPER_INGOT,12),
            new Offering(Items.GLOW_INK_SAC,2)));
        OFFERINGS.put(7,List.of(new Offering(Items.GOLD_INGOT,8),
            new Offering(Items.ENDER_PEARL,2)));
        OFFERINGS.put(6,List.of(new Offering(Items.BLAZE_POWDER,6),
            new Offering(Items.GHAST_TEAR,1)));
        OFFERINGS.put(5,List.of(new Offering(Items.DIAMOND,4),
            new Offering(Items.AMETHYST_SHARD,16)));
        OFFERINGS.put(4,List.of(new Offering(Items.NETHERITE_SCRAP,1),
            new Offering(Items.ENDER_EYE,2)));
        OFFERINGS.put(3,List.of(new Offering(Items.ANCIENT_DEBRIS,2),
            new Offering(Items.PHANTOM_MEMBRANE,4)));
        OFFERINGS.put(2,List.of(new Offering(Items.NETHER_STAR,1),
            new Offering(Items.ENDER_PEARL,8)));
        OFFERINGS.put(1,List.of(new Offering(Items.NETHER_STAR,2),
            new Offering(Items.ENCHANTED_GOLDEN_APPLE,1)));
    }
    private static boolean has(ServerPlayerEntity p,Item item) {
        for(int i=0;i<p.getInventory().size();i++)
            if(p.getInventory().getStack(i).isOf(item))return true;
        return false;
    }
    private static int inventoryCount(ServerPlayerEntity p,Item item) {
        int count=0;
        for(int i=0;i<p.getInventory().size();i++) {
            ItemStack stack=p.getInventory().getStack(i);
            if(stack.isOf(item))count+=stack.getCount();
        }
        return count;
    }
    private static boolean affordable(ServerPlayerEntity p,List<Offering> required) {
        for(Offering offer:required) if(inventoryCount(p,offer.item)<offer.count)return false;
        return true;
    }
    private static void consume(ServerPlayerEntity p,List<Offering> required) {
        for(Offering offer:required) {
            int remaining=offer.count;
            for(int i=0;i<p.getInventory().size() && remaining>0;i++) {
                ItemStack stack=p.getInventory().getStack(i);
                if(!stack.isOf(offer.item))continue;
                int used=Math.min(stack.getCount(),remaining);
                stack.decrement(used);
                remaining-=used;
            }
            if(remaining!=0)throw new IllegalStateException("Ingredients changed during ritual");
        }
        p.getInventory().markDirty();
    }
    public static void registerNew(ServerPlayerEntity p,ArcaneSave.Record r) {
        r.lastTradeCount=trades(p);
        Objective act=ACTS.get(r.profile.primary());
        r.hadActingItem=act!=null && has(p,act.item);
    }
    private static int trades(ServerPlayerEntity p) {
        return p.getStatHandler().getStat(Stats.CUSTOM.getOrCreateStat(Stats.TRADED_WITH_VILLAGER));
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        if(!r.originValid)return;
        r.onlineTicks+=20; // Only ticks while this player is connected, not server uptime.
        Objective objective=ACTS.get(r.profile.primary());
        if(objective==null)return;
        boolean itemPresent=has(p,objective.item);
        if(!r.hadActingItem && itemPresent && r.nextActA)credit(p,state,r,true);
        r.hadActingItem=itemPresent;
        int currentTradeCount=trades(p);
        if(!r.nextActA && objective.trade && currentTradeCount>r.lastTradeCount)
            credit(p,state,r,false);
        r.lastTradeCount=currentTradeCount;
        state.markDirty();
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity killed) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null||r.nextActA)return;
        Objective objective=ACTS.get(r.profile.primary());
        if(objective==null || objective.trade || objective.victimType!=killed.getType())return;
        credit(p,state,r,false);
    }
    private static boolean credit(ServerPlayerEntity p,ArcaneSave state,
                                  ArcaneSave.Record r,boolean actionA) {
        if(actionA!=r.nextActA || r.actingMarks>=20 ||
            r.onlineTicks-r.lastActingTick<2400)return false;
        r.actingMarks++;
        r.nextActA=!actionA;
        r.lastActingTick=r.onlineTicks;
        state.markDirty();
        ArcaneMod.info(p,"Acting "+(actionA?"A":"B")+" completed. "+
            r.actingMarks+" marks banked. Next: "+(r.nextActA?"A":"B")+".");
        return true;
    }
    private static boolean altar(ServerPlayerEntity p) {
        if(!p.isOnGround() || p.isFallFlying())return false;
        BlockPos below=p.getBlockPos().down();
        return p.getWorld().getBlockState(below).isOf(Blocks.LECTERN)
            && p.getWorld().getBlockState(below.down()).isOf(Blocks.CRYING_OBSIDIAN);
    }
    public static int status(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        int seq=r.profile.sequence();
        ArcaneMod.info(p,"Sequence "+seq+" / Acting "+r.actingMarks+"/20 / next "+
            (r.nextActA?"A":"B")+" / remaining acting cooldown "+
            Math.max(0,(2400-r.onlineTicks+r.lastActingTick)/20)+" seconds");
        if(seq>0) {
            ArcaneMod.info(p,"Ascension requires "+AscensionRules.marksToAscend(seq)+
                " acting marks and a lectern on crying obsidian.");
            for(Offering o:OFFERINGS.get(seq))
                ArcaneMod.info(p,Registry.ITEM.getId(o.item)+": "+
                    inventoryCount(p,o.item)+"/"+o.count);
        }
        return 1;
    }
    public static int ascend(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        int old=r.profile.sequence();
        if(old<=0){ArcaneMod.error(p,"Already at Sequence 0.");return 0;}
        List<Offering> needs=OFFERINGS.get(old);
        boolean safe=!r.inCombat(WorldJusticeAbilities.now(p)) && p.isOnGround() && !p.isFallFlying();
        if(!AscensionRules.eligible(r.actingMarks,altar(p),safe,affordable(p,needs),old)) {
            ArcaneMod.error(p,"Missing Acting marks, offerings, a valid ritual altar, or out of combat.");
            status(p,state,r);return 0;
        }
        if(!ArcaneMod.onSequenceChange(p,old,old-1))return 0;
        consume(p,needs);
        r.actingMarks-=AscensionRules.marksToAscend(old);
        state.markDirty();
        ArcaneMod.info(p,"Ascension complete: Sequence "+old+" -> "+(old-1)+".");
        return 1;
    }
}
