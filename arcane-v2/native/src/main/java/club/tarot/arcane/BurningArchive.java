package club.tarot.arcane;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/** Timed Hermit/Chariot endgame powers and their combined Burning Archive Resonance. */
public final class BurningArchive {
    private BurningArchive() {}
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static final class Active {
        final String name;
        final long until;
        final net.minecraft.server.world.ServerWorld world;
        boolean criticalConsumed;
        UUID criticalArrow;
        Active(String name,ServerPlayerEntity owner,int ticks) {
            this.name=name;
            this.world=owner.getWorld();
            this.until=owner.getServer().getOverworld().getTime()+ticks;
        }
    }
    private static long time(ServerPlayerEntity p) {
        return p.getServer().getOverworld().getTime();
    }
    public static boolean active(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return a!=null && time(p)<a.until && a.world==p.getWorld();
    }
    public static boolean combatCap(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return active(p) && (a.name.equals("the_battlefield")
            || a.name.equals("the_burning_archive"));
    }
    public static boolean immortalDash(ServerPlayerEntity p) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && time(p)<r.meteorImmuneUntil;
    }
    public static float outgoing(ServerPlayerEntity p,LivingEntity target,
                                 DamageSource source,float amount) {
        if(!FoolAbilities.enemy(p,target))return amount;
        Active a=ACTIVE.get(p.getUuid());
        if(a==null || !active(p))return amount;
        if(combatCap(p))amount*=1.30f;
        if(source.isProjectile() && !a.criticalConsumed &&
            (a.name.equals("the_unseen") || a.name.equals("the_burning_archive"))) {
            amount*=2f; a.criticalConsumed=true;
            if(source.getSource()!=null)a.criticalArrow=source.getSource().getUuid();
        }
        return amount;
    }
    public static void onTakenDamage(ServerPlayerEntity p,DamageSource source,float taken) {
        // All current capstones preserve ordinary damage vulnerability;
        // temporary meteor dash is the only immunity.
    }
    public static void onSuccessfulHit(ServerPlayerEntity p,LivingEntity target,
                                       DamageSource source,ArcaneSave.Record r) {
        if(!FoolAbilities.enemy(p,target))return;
        if(combatCap(p) && source.getSource()==p)target.setOnFireFor(5);
        if(active(p) && source.isProjectile() && ACTIVE.get(p.getUuid()).criticalArrow!=null
            && source.getSource()!=null
            && ACTIVE.get(p.getUuid()).criticalArrow.equals(source.getSource().getUuid())
            && ACTIVE.get(p.getUuid()).name.equals("the_burning_archive")) {
            for(LivingEntity enemy:HangedAbilities.enemies(p,target.getPos(),10))
                enemy.setOnFireFor(5);
        }
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity victim,
                              ArcaneSave state,ArcaneSave.Record r) {
        if(!combatCap(p))return;
        if(ACTIVE.get(p.getUuid()).name.equals("the_burning_archive"))
            r.burnStacks=Math.min(5,r.burnStacks+1);
        state.markDirty();
    }

    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        Active a=ACTIVE.get(p.getUuid());
        if(a==null)return;
        long now=time(p);
        if(now>=a.until || a.world!=p.getWorld() || !p.isAlive()) {
            ACTIVE.remove(p.getUuid());
            if(a.name.equals("the_burning_archive") && r.burnStacks>=5) {
                for(LivingEntity target:HangedAbilities.enemies(p,p.getPos(),15)) {
                    target.damage(DamageSource.ON_FIRE,6f);
                    target.setOnFireFor(5);
                }
            }
            r.burnStacks=0;
            state.markDirty();
            return;
        }
        if(now%40==0 && !a.name.equals("the_battlefield")) {
            for(PlayerEntity other:p.getWorld().getEntitiesByClass(PlayerEntity.class,
                 new Box(p.getBlockPos()).expand(100),e->e!=p && e.squaredDistanceTo(p)<=10000))
                other.addStatusEffect(new StatusEffectInstance(StatusEffects.GLOWING,60,0));
            p.addStatusEffect(new StatusEffectInstance(StatusEffects.NIGHT_VISION,220,0));
            // APPROX: visibility of nearby structures is represented by private region/biome intel.
            ArcaneMod.info(p,"Celestial map: nearby coordinates "+p.getBlockPos()+
                " (full structure detection needs a dedicated world index)");
        }
        if(combatCap(p)) {
            for(LivingEntity opponent:HangedAbilities.enemies(p,p.getPos(),20)) {
                if(opponent instanceof MobEntity hostile) {
                    LivingEntity alternate=HangedAbilities.enemies(p,opponent.getPos(),10)
                        .stream().filter(e->e!=opponent && e instanceof MobEntity)
                        .min(Comparator.comparingDouble(opponent::squaredDistanceTo)).orElse(null);
                    if(alternate!=null)hostile.setTarget(alternate);
                } else if(opponent instanceof PlayerEntity) {
                    opponent.addStatusEffect(new StatusEffectInstance(StatusEffects.GLOWING,40,0));
                    // Cannot compel human PvP targeting; use visual hostility mark.
                }
            }
        }
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,
                               ArcaneSave.Record r,String name) {
        boolean permitted=switch(name) {
            case "the_unseen" -> HermitChariotAbilities.hermit(r,0);
            case "the_battlefield" -> HermitChariotAbilities.chariot(r,0);
            case "the_burning_archive" -> HermitChariotAbilities.archive(r,0);
            default -> false;
        };
        long now=time(p);
        if(!permitted || active(p) || !r.ready(name,now,
            name.equals("the_battlefield")?18000:24000))return false;
        ACTIVE.put(p.getUuid(),new Active(name,p,900));
        ArcaneMod.info(p,"Capstone "+name+" active for 45 seconds.");
        state.markDirty();
        return true;
    }
    public static void stopOnDisconnect(ServerPlayerEntity p) {
        ACTIVE.remove(p.getUuid());
    }
}
