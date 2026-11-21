package club.tarot.arcane;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.Comparator;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.projectile.PersistentProjectileEntity;
import net.minecraft.entity.projectile.ProjectileEntity;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/** Sequence-0 active abilities and high-tier World+Justice / Marked Verdict mechanics. */
public final class MarkedVerdict {
    private MarkedVerdict() { }
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static final Map<UUID,UUID> HOMING_PROJECTILES=new HashMap<>();
    private static final class Active {
        final UUID owner;
        final UUID target;
        final ServerWorld world;
        final String mode;
        final long until;
        UUID firstArrow;
        boolean firstShotUsed;
        Active(ServerPlayerEntity p,ServerPlayerEntity target,String mode,int duration) {
            this.owner=p.getUuid();
            this.target=target==null?null:target.getUuid();
            this.world=p.getWorld();
            this.mode=mode;
            this.until=WorldJusticeAbilities.now(p)+duration;
        }
    }
    private static boolean live(Active a) {return a!=null&&a.world.getTime()<a.until;}
    public static boolean active(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return live(a) && a.world==p.getWorld();
    }
    public static float scaleOutgoing(ServerPlayerEntity p,LivingEntity victim,DamageSource source,float amount) {
        Active a=ACTIVE.get(p.getUuid());
        if(!live(a)||a.target==null||!victim.getUuid().equals(a.target)
            || !FoolAbilities.enemy(p,victim))return amount;
        if(a.mode.equals("mindscape"))return amount; // canceled at damage interception
        if(a.mode.equals("perfect_prey") && source.isProjectile())return amount*2f;
        if(a.mode.equals("marked_verdict"))return amount*2f;
        return amount;
    }
    /** Freeze controls are server-enforced every tick, including on opponents without Tarot Origin. */
    public static boolean canSprint(ServerPlayerEntity p) {
        return !isMovementForbidden(p);
    }
    public static boolean canJump(ServerPlayerEntity p) {
        return !isMovementForbidden(p);
    }
    private static boolean isMovementForbidden(ServerPlayerEntity player) {
        for(Active a:ACTIVE.values())if(live(a)&&a.world==player.getWorld()) {
            if(a.mode.equals("mindscape") && a.world.getServer().getPlayerManager().getPlayer(a.owner)!=null) {
                ServerPlayerEntity p=a.world.getPlayerByUuid(a.owner);
                if(p.squaredDistanceTo(player)<=400)return true;
            }
            if(a.mode.equals("marked_verdict") && player.getUuid().equals(a.target))return true;
        }
        return false;
    }
    public static void enforceMovement(ServerPlayerEntity player) {
        if(!canSprint(player))player.setSprinting(false);
        for(Active a:ACTIVE.values())if(live(a)&&a.world==player.getWorld()
            && a.mode.equals("mindscape")&&a.world.getPlayerByUuid(a.owner)!=null) {
            ServerPlayerEntity holder=a.world.getPlayerByUuid(a.owner);
            if(holder!=null && holder!=player && holder.squaredDistanceTo(player)<=400 &&
                FoolAbilities.enemy(holder,player)) {
                WorldJusticeAbilities.effect(player,StatusEffects.SLOWNESS,25,255);
                WorldJusticeAbilities.effect(player,StatusEffects.WEAKNESS,25,255);
            }
        }
    }
    public static boolean cancelDamage(LivingEntity victim,DamageSource source) {
        for(Active a:ACTIVE.values()) {
            if(!live(a) || !a.mode.equals("mindscape") || a.world!=victim.getWorld())continue;
            ServerPlayerEntity owner=a.world.getPlayerByUuid(a.owner);
            if(owner==null)continue;
            Entity attacker=source.getAttacker();
            boolean victimFrozen=FoolAbilities.enemy(owner,victim)
                && victim.squaredDistanceTo(owner)<=400;
            boolean attackerFrozen=attacker instanceof LivingEntity e &&
                FoolAbilities.enemy(owner,e) && attacker.squaredDistanceTo(owner)<=400;
            if(victimFrozen && attacker==owner || victim==owner && attackerFrozen
                || attackerFrozen)return true;
        }
        return false;
    }
    public static void tick(ServerPlayerEntity owner,ArcaneSave state,ArcaneSave.Record r) {
        Active a=ACTIVE.get(owner.getUuid());
        long now=WorldJusticeAbilities.now(owner);
        if(a==null)return;
        if(now>=a.until || a.world!=owner.getWorld() || !owner.isAlive()) {
            ACTIVE.remove(owner.getUuid());
            HOMING_PROJECTILES.entrySet().removeIf(e->e.getValue().equals(owner.getUuid()));
            return;
        }
        if(a.target!=null && now%40==0) {
            ServerPlayerEntity target=owner.getServer().getPlayerManager().getPlayer(a.target);
            if(target!=null && target.getWorld()==owner.getWorld())
                ArcaneMod.info(owner,"[Tracker] "+target.getName().getString()+" at "+target.getBlockPos());
        }
        if(a.mode.equals("mindscape")) {
            for(LivingEntity e:HangedAbilities.enemies(owner,owner.getPos(),20)) {
                WorldJusticeAbilities.effect(e,StatusEffects.SLOWNESS,25,255);
                WorldJusticeAbilities.effect(e,StatusEffects.WEAKNESS,25,255);
                if(e instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
            }
        }
    }

    /**
     * Retarget only the FIRST projectile after capstone starts. No blocks are bypassed.
     * Client-side prediction may jitter; this is an explicitly documented approximation.
     */
    public static void projectileTick(ProjectileEntity projectile) {
        if(projectile.getWorld().isClient || !(projectile instanceof PersistentProjectileEntity arrow))return;
        if(!(projectile.getOwner() instanceof ServerPlayerEntity owner))return;
        Active a=ACTIVE.get(owner.getUuid());
        if(!live(a) || !a.world.equals(projectile.getWorld())
            || a.target==null || a.mode.equals("mindscape"))return;
        if(a.firstShotUsed && !projectile.getUuid().equals(a.firstArrow))return;
        if(a.firstArrow==null) {
            a.firstArrow=projectile.getUuid();
            a.firstShotUsed=true;
            HOMING_PROJECTILES.put(a.firstArrow,owner.getUuid());
        }
        if(!a.firstArrow.equals(projectile.getUuid()))return;
        ServerPlayerEntity target=owner.getServer().getPlayerManager().getPlayer(a.target);
        if(target==null||target.getWorld()!=a.world||!target.isAlive()
            || projectile.squaredDistanceTo(target)>3600)return;
        Vec3d direction=target.getPos().add(0,target.getHeight()*.65,0)
            .subtract(projectile.getPos()).normalize();
        if(direction.lengthSquared()<.001)return;
        double speed=Math.max(1.8,projectile.getVelocity().length());
        projectile.setNoGravity(true);
        projectile.setVelocity(direction.multiply(speed));
    }
    public static void onSuccessfulHit(ServerPlayerEntity attacker,LivingEntity victim,
                                       DamageSource source,ArcaneSave.Record r) {
        Active a=ACTIVE.get(attacker.getUuid());
        if(!live(a) || a.target==null || !a.target.equals(victim.getUuid()))return;
        if(source.isProjectile()) {
            WorldJusticeAbilities.effect(victim,StatusEffects.SLOWNESS,100,1);
            if(a.mode.equals("marked_verdict")) {
                WorldJusticeAbilities.effect(victim,StatusEffects.SLOWNESS,60,255);
                for(LivingEntity e:HangedAbilities.enemies(attacker,victim.getPos(),15)) {
                    WorldJusticeAbilities.effect(e,StatusEffects.SLOWNESS,100,255);
                    WorldJusticeAbilities.effect(e,StatusEffects.WEAKNESS,100,255);
                    if(e instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
                }
            }
        } else if(a.mode.equals("marked_verdict"))
            WorldJusticeAbilities.effect(victim,StatusEffects.SLOWNESS,80,1);
    }
    public static void onKill(ServerPlayerEntity killer,LivingEntity victim,
                              ArcaneSave state,ArcaneSave.Record r) {
        Active a=ACTIVE.get(killer.getUuid());
        if(!live(a) || a.target==null || !victim.getUuid().equals(a.target))return;
        WorldJusticeAbilities.effect(killer,StatusEffects.SPEED,600,1);
        WorldJusticeAbilities.effect(killer,StatusEffects.REGENERATION,600,0);
        if(a.mode.equals("marked_verdict")) {
            for(PlayerEntity ally:killer.getWorld().getEntitiesByClass(PlayerEntity.class,
                 new Box(killer.getBlockPos()).expand(10),
                 e->e.squaredDistanceTo(killer)<=100 && HangedAbilities.ally(killer,e)))
                WorldJusticeAbilities.effect(ally,StatusEffects.ABSORPTION,200,1);
        }
        ACTIVE.remove(killer.getUuid());
        state.markDirty();
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String ability) {
        long now=WorldJusticeAbilities.now(p);
        switch(ability) {
            case "the_perfect_prey":
            case "the_marked_verdict": {
                boolean pair=ability.equals("the_marked_verdict");
                if(pair?!WorldJusticeAbilities.verdict(r,0):!WorldJusticeAbilities.world(r,0))return false;
                ServerPlayerEntity target=nearestEnemyPlayer(p,50);
                if(target==null || ACTIVE.containsKey(p.getUuid())
                    || !r.ready(ability,now,24000))return false;
                ACTIVE.put(p.getUuid(),new Active(p,target,pair?"marked_verdict":"perfect_prey",900));
                ArcaneMod.info(p,"Marked "+target.getName().getString()+" for 45 seconds.");
                break;
            }
            case "the_mindscape": {
                if(!WorldJusticeAbilities.justice(r,0) || ACTIVE.containsKey(p.getUuid())
                    || !r.ready(ability,now,24000))return false;
                ACTIVE.put(p.getUuid(),new Active(p,null,"mindscape",600));
                ArcaneMod.info(p,"The Mindscape freezes opponents for 30 seconds.");
                break;
            }
            case "puppets_sentence": {
                if(!WorldJusticeAbilities.verdict(r,5) || !p.isSneaking()
                    || !r.ready(ability,now,400))return false;
                LivingEntity victim=HangedAbilities.enemies(p,p.getPos(),8).stream()
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(victim==null)return false;
                WorldJusticeAbilities.effect(victim,StatusEffects.SLOWNESS,
                    victim instanceof PlayerEntity?40:80,1);
                if(victim instanceof PlayerEntity)
                    ArcaneMod.info(p,"Puppet's Sentence target at "+victim.getBlockPos());
                else WorldJusticeAbilities.effect(victim,StatusEffects.GLOWING,80,0);
                break;
            }
            case "silent_witness": {
                if(!WorldJusticeAbilities.verdict(r,6)||r.inCombat(now)
                    || !r.ready(ability,now,2400))return false;
                WorldJusticeAbilities.effect(p,StatusEffects.INVISIBILITY,600,0);
                ServerPlayerEntity target=nearestEnemyPlayer(p,16);
                if(target!=null)
                    ArcaneMod.info(p,"Silent Witness: "+target.getName().getString()
                        +" HP "+Math.round(target.getHealth()));
                break;
            }
            default:return false;
        }
        state.markDirty();return true;
    }
    private static ServerPlayerEntity nearestEnemyPlayer(ServerPlayerEntity p,double radius) {
        return p.getWorld().getEntitiesByClass(ServerPlayerEntity.class,
            new Box(p.getBlockPos()).expand(radius),
            e->e.isAlive() && e!=p && FoolAbilities.enemy(p,e) && e.squaredDistanceTo(p)<=radius*radius)
            .stream().min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
    }
    public static void stopOnDisconnect(ServerPlayerEntity p) {
        ACTIVE.remove(p.getUuid());
        HOMING_PROJECTILES.entrySet().removeIf(e->e.getValue().equals(p.getUuid()));
    }
}
