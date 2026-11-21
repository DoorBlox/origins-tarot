package club.tarot.arcane;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.boss.dragon.EnderDragonEntity;
import net.minecraft.entity.boss.WitherEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/**
 * Death + Tower capstones. Players' health removal always capped at half of
 * current health per 60 ticks; boss tick damage is capped likewise.
 * No block destruction or world-wide weather changes.
 */
public final class CrumblingReaper {
    private CrumblingReaper() {}
    private record Active(String name,ServerWorld world,long until) {}
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static long time(ServerPlayerEntity p) {return p.getServer().getOverworld().getTime();}
    static boolean active(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return a!=null && time(p)<a.until && a.world==p.getWorld();
    }
    static boolean unstable(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return active(p) && (a.name.equals("the_fall") || a.name.equals("the_crumbling_reaper"));
    }
    static boolean harvesting(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return active(p) && (a.name.equals("the_final_harvest") || a.name.equals("the_crumbling_reaper"));
    }
    public static boolean cast(ServerPlayerEntity player,ArcaneSave state,ArcaneSave.Record r,String id) {
        if(!switch(id){
            case "the_final_harvest"->DeathTowerAbilities.death(r,0);
            case "the_fall"->DeathTowerAbilities.tower(r,0);
            case "the_crumbling_reaper"->DeathTowerAbilities.reaper(r,0);
            default->false;
        })return false;
        if(active(player) || !r.ready(id,time(player),24000))return false;
        ACTIVE.put(player.getUuid(),new Active(id,player.getWorld(),time(player)+600));
        ArcaneMod.info(player,"Activated "+id+" for 30 seconds (600 ticks).");
        state.markDirty();
        return true;
    }
    static void tick(ServerPlayerEntity player,ArcaneSave state,ArcaneSave.Record r) {
        Active a=ACTIVE.get(player.getUuid());
        if(a==null)return;
        long now=time(player);
        if(now>=a.until||a.world!=player.getWorld()||!player.isAlive()) {
            ACTIVE.remove(player.getUuid());
            return;
        }
        if(harvesting(player)&&now%60==0)harvest(player,r,state);
        if(unstable(player)&&now%20==0)unstableGround(player,r,state);
    }
    static void onKill(ServerPlayerEntity owner,LivingEntity killed,ArcaneSave state,ArcaneSave.Record r) {
        if(!harvesting(owner))return;
        if(!FoolAbilities.enemy(owner,killed))return;
        float cap=DeathTowerAbilities.reaper(r,0)?30f:20f;
        grantAbsorption(owner,state,r,cap,1200);
    }
    static void grantAbsorption(ServerPlayerEntity owner,ArcaneSave state,
                                ArcaneSave.Record r,float cap,int ticks) {
        r.arcaneAbsorption=Math.min(cap,Math.max(0f,r.arcaneAbsorption)+2f);
        r.arcaneAbsorptionUntil=time(owner)+ticks;
        owner.setAbsorptionAmount(Math.max(owner.getAbsorptionAmount(),r.arcaneAbsorption));
        state.markDirty();
    }
    private static void harvest(ServerPlayerEntity owner,ArcaneSave.Record r,ArcaneSave state) {
        LivingEntity target=HangedAbilities.enemies(owner,owner.getPos(),10).stream()
            .filter(e->e.isAlive() && e.getMaxHealth()>0)
            .min(Comparator.comparingDouble(LivingEntity::getHealth)).orElse(null);
        if(target==null)return;
        float available=target.getHealth();
        // Player and boss are never executed by a single automatic pulse.
        float damage=target instanceof PlayerEntity || target instanceof WitherEntity
            || target instanceof EnderDragonEntity ? available*.5f : available+1f;
        if(damage<=0)return;
        boolean hit=target.damage(DamageSource.MAGIC,damage);
        if(hit && !target.isAlive())onKill(owner,target,state,r);
        // Vanilla onDeath has no player attacker for MAGIC. Credit confirmed aura kills.
    }
    private static void unstableGround(ServerPlayerEntity owner,ArcaneSave.Record r,ArcaneSave state) {
        Box box=new Box(owner.getBlockPos()).expand(15);
        for(LivingEntity entity:owner.getWorld().getEntitiesByClass(LivingEntity.class,box,
            x->x.isAlive() && x.isOnGround() && x.squaredDistanceTo(owner)<=225
                && owner.getWorld().getBlockState(x.getBlockPos().down()).getMaterial().isSolid())) {
            // The Fall explicitly hits every entity on solid ground, including owner and allies.
            boolean hit=entity.damage(DamageSource.MAGIC,4f);
            if(hit && !entity.isAlive() && FoolAbilities.enemy(owner,entity))
                onKill(owner,entity,state,r);
        }
        // Instability also tosses hostile mobs and enemy players upward.
        for(LivingEntity enemy:HangedAbilities.enemies(owner,owner.getPos(),15))
            enemy.addVelocity(0,.25,0);
    }
    public static void maintenance(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long now=time(p);
        if(r.arcaneAbsorption>0 && now>=r.arcaneAbsorptionUntil) {
            // The value is recorded for migration/diagnostics. Do not set the
            // absorption amount to zero: another mod may own part of it.
            // Exact source-specific expiry requires a distinct guarded modifier.
            r.arcaneAbsorption=0;
            state.markDirty();
        }
    }
    public static void stopOnDisconnect(ServerPlayerEntity p) {
        ACTIVE.remove(p.getUuid());
    }
}
