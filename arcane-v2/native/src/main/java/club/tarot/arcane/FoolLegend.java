package club.tarot.arcane;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;

/**
 * Server-only no-KubeJS capstone controller for the Fool.
 * Individual Seq0 is retained by Rev2, but Rev3 normally replaces it with
 * Resonance at Seq1. Activation is only possible if the Sequence kit is equipped.
 */
public final class FoolLegend {
    private FoolLegend() { }
    private static final Map<UUID, Active> ACTIVE = new HashMap<>();

    private static final class Active {
        final ServerWorld world;
        final double x,y,z;
        final float yaw,pitch;
        final long expires;
        final boolean priorMayFly;
        long lastDecoy;
        final boolean isPaper;
        Active(ServerPlayerEntity p,long now,boolean paper) {
            isPaper=paper;
            world=p.getWorld();
            x=p.getX(); y=p.getY(); z=p.getZ();
            yaw=p.getYaw(); pitch=p.getPitch();
            expires=now+700; lastDecoy=now;
            priorMayFly=p.getAbilities().allowFlying;
        }
    }

    public static void register() {
        ServerPlayerEvents.ALLOW_DEATH.register((player,source,damage) -> {
            Active a=ACTIVE.remove(player.getUuid());
            if(a!=null) restoreFlight(player,a);
            return true; // Death during the window never rewinds or heals.
        });
    }

    public static boolean active(ServerPlayerEntity player) {
        Active a=ACTIVE.get(player.getUuid());
        return a!=null && a.world==player.getWorld() && player.getWorld().getTime()<a.expires;
    }

    public static boolean cast(ServerPlayerEntity player,ArcaneSave state,ArcaneSave.Record record) {
        boolean isPaper=record.profile.active("paper_martyr",0);
        if(!isPaper && !record.profile.active("fool",0)) return false;
        long now=player.getWorld().getTime();
        if(ACTIVE.containsKey(player.getUuid())) return false;
        int cooldown=player.getHealth()<6f?12000:18000;
        if(!record.ready(isPaper?"the_paper_martyr":"legend_of_the_fool",now,cooldown)) return false;
        Active a=new Active(player,now,isPaper);
        record.restoreFlightPending=true;
        record.legendPriorMayFly=a.priorMayFly;
        ACTIVE.put(player.getUuid(),a);
        player.getAbilities().allowFlying=true;
        player.sendAbilitiesUpdate();
        player.addStatusEffect(new StatusEffectInstance(StatusEffects.FIRE_RESISTANCE,700,0));
        // Exact -75% incoming / +50% outgoing applies in the native damage mixin.
        if(isPaper)PaperMartyr.spawnDecoy(player,3,3,3,100,false);
        else FoolAbilities.decoy(player);
        state.markDirty();
        return true;
    }

    public static void tick(ServerPlayerEntity player) {
        Active a=ACTIVE.get(player.getUuid());
        if(a==null) return;
        long now=player.getWorld().getTime();
        if(now>=a.expires || player.getWorld()!=a.world) {
            ACTIVE.remove(player.getUuid());
            expire(player,a);
            return;
        }
        ArcaneSave.Record profile=ArcaneMod.profile(player);
        if(a.isPaper && profile!=null)PaperMartyr.capstoneTick(player,profile,now);
        if(now-a.lastDecoy>=100) {
            if(a.isPaper)PaperMartyr.spawnDecoy(player,3,3,3,100,false);
            else FoolAbilities.decoy(player);
            a.lastDecoy=now;
        }
    }

    /** Debuff a hostile mob or enemy player that is actually struck by a Legend holder. */
    public static void afterSuccessfulHit(LivingEntity victim,DamageSource source) {
        Entity attacker=source.getAttacker();
        if(!(attacker instanceof ServerPlayerEntity)) return;
        ServerPlayerEntity player=(ServerPlayerEntity)attacker;
        if(!active(player) || !FoolAbilities.enemy(player,victim)) return;
        victim.addStatusEffect(new StatusEffectInstance(StatusEffects.SLOWNESS,80,1));
        victim.addStatusEffect(new StatusEffectInstance(StatusEffects.WEAKNESS,80,0));
    }

    /** Fire and fall are fully immune while Legend runs, before incoming damage. */
    public static boolean immuneToDamage(LivingEntity victim,DamageSource source) {
        return victim instanceof ServerPlayerEntity
            && active((ServerPlayerEntity)victim)
            && (source.isFire() || source==DamageSource.FALL);
    }

    public static void stopOnDisconnect(ServerPlayerEntity player) {
        Active a=ACTIVE.remove(player.getUuid());
        if(a!=null) restoreFlight(player,a);
    }

    private static void expire(ServerPlayerEntity player,Active a) {
        restoreFlight(player,a);
        ArcaneSave.Record r=ArcaneMod.profile(player);
        if(a.isPaper && r!=null)PaperMartyr.capstoneExpire(player,r);
        if(!player.isAlive()) return;
        player.teleport(a.world,a.x,a.y,a.z,a.yaw,a.pitch);
        player.setHealth(20f);
        player.getHungerManager().setFoodLevel(20);
        player.getHungerManager().setSaturationLevel(20f);
        player.clearStatusEffects();
        player.addStatusEffect(new StatusEffectInstance(StatusEffects.REGENERATION,200,1));
        player.addStatusEffect(new StatusEffectInstance(StatusEffects.SPEED,200,1));
    }
    public static void recoverStaleFlight(ServerPlayerEntity player) {
        ArcaneSave state=ArcaneSave.get(player.getServer());
        ArcaneSave.Record r=state.getPlayer(player.getUuid());
        if(r==null || !r.restoreFlightPending || ACTIVE.containsKey(player.getUuid()))return;
        player.getAbilities().allowFlying=r.legendPriorMayFly;
        if(!r.legendPriorMayFly)player.getAbilities().flying=false;
        player.sendAbilitiesUpdate();
        r.restoreFlightPending=false;
        state.markDirty();
        LOG_RECOVERY(player);
    }
    private static void LOG_RECOVERY(ServerPlayerEntity player) {
        ArcaneMod.LOG.warn("Recovered stale Tarot capstone flight for {}",player.getUuidAsString());
    }
    private static void restoreFlight(ServerPlayerEntity player,Active a) {
        ArcaneSave state=ArcaneSave.get(player.getServer());
        ArcaneSave.Record r=state.getPlayer(player.getUuid());
        if(r!=null){r.restoreFlightPending=false;state.markDirty();}
        player.getAbilities().allowFlying=a.priorMayFly;
        if(!a.priorMayFly) player.getAbilities().flying=false;
        player.sendAbilitiesUpdate();
    }
}
