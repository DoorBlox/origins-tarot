package club.tarot.arcane;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/** Source-scoped native domain, social pacification and movement policies. */
public final class BenevolentCrown {
    private BenevolentCrown() {}
    private static final Map<UUID,Active> DOMAINS=new HashMap<>();
    private static final Map<UUID,Pact> COINS=new HashMap<>();
    private static final class Active {
        final String ability;
        final ServerWorld dimension;
        final long started;
        final long until;
        final Set<UUID> allowed=new HashSet<>();
        final Set<UUID> challenged=new HashSet<>();
        UUID consort;
        Active(ServerPlayerEntity p,String id,long start,int ticks){
            ability=id;dimension=p.getWorld();started=start;until=start+ticks;
        }
        boolean emperor(){return ability.equals("the_emperors_domain");}
        boolean garden(){return ability.equals("the_garden");}
        boolean crown(){return ability.equals("the_benevolent_crown");}
    }
    private static final class Pact {
        final UUID owner;
        final ServerWorld dimension;
        final long until;
        Pact(ServerPlayerEntity caster,long until){
            this.owner=caster.getUuid();this.dimension=caster.getWorld();this.until=until;
        }
    }
    private static long time(ServerPlayerEntity p){return p.getServer().getOverworld().getTime();}
    private static Active valid(ServerPlayerEntity p){
        Active a=DOMAINS.get(p.getUuid());
        if(a==null)return null;
        if(a.dimension!=p.getWorld() || time(p)>=a.until || !p.isAlive())return null;
        return a;
    }
    private static boolean close(ServerPlayerEntity caster,Entity target,double dist){
        return caster.getWorld()==target.getWorld() &&
            caster.squaredDistanceTo(target)<=dist*dist;
    }
    public static boolean domainOf(ServerPlayerEntity p,String id){
        Active a=valid(p);return a!=null && a.ability.equals(id);
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id){
        boolean can=switch(id){
            case "the_emperors_domain" -> EmperorLoversAbilities.emperor(r,0);
            case "the_garden" -> EmperorLoversAbilities.lovers(r,0);
            case "the_benevolent_crown" -> EmperorLoversAbilities.crown(r,0);
            default -> false;
        };
        if(!can || valid(p)!=null)return false;
        long now=time(p);
        int duration=id.equals("the_garden")?1800:1200;
        int cooldown=id.equals("the_garden")?24000:18000;
        if(!r.ready(id,now,cooldown))return false;
        DOMAINS.put(p.getUuid(),new Active(p,id,now,duration));
        ArcaneMod.info(p,"Activated "+id+" for "+duration+" ticks.");
        state.markDirty();return true;
    }
    public static boolean allow(ServerPlayerEntity owner,ServerPlayerEntity target){
        Active a=valid(owner);
        if(a==null || a.garden())return false;
        a.allowed.add(target.getUuid());
        ArcaneMod.info(owner,"Domain movement allowed for "+target.getGameProfile().getName()+".");
        return true;
    }
    public static boolean consort(ServerPlayerEntity owner,ServerPlayerEntity target){
        Active a=valid(owner);
        if(a==null||!a.crown()||target==owner || !close(owner,target,15)
            || !HangedAbilities.ally(owner,target))return false;
        a.consort=target.getUuid();
        ArcaneMod.info(owner,"Consort appointed: "+target.getGameProfile().getName()+".");
        return true;
    }
    public static boolean consortDamage(ServerPlayerEntity subject){
        for(UUID ownerId:new ArrayList<>(DOMAINS.keySet())){
            ServerPlayerEntity owner=subject.getServer().getPlayerManager().getPlayer(ownerId);
            if(owner==null)continue;
            Active a=valid(owner);
            if(a!=null && a.crown() && subject.getUuid().equals(a.consort)
                && close(owner,subject,15))return true;
        }
        return false;
    }
    public static boolean allySpeed(ServerPlayerEntity owner,ServerPlayerEntity other){
        Active a=valid(owner);
        if(a!=null && (a.crown()||a.garden()) && close(owner,other,15))
            return true;
        ArcaneSave.Record r=ArcaneMod.profile(owner);
        return r!=null && EmperorLoversAbilities.crown(r,2)
            && time(owner)<r.decreeUntil && close(owner,other,8);
    }
    public static boolean linkedCrownShield(ServerPlayerEntity victim){
        for(ServerPlayerEntity caster:victim.getServer().getPlayerManager().getPlayerList()){
            if(caster==victim || !close(caster,victim,8)
                || !HangedAbilities.ally(caster,victim))continue;
            ArcaneSave.Record record=ArcaneMod.profile(caster);
            if(record!=null && EmperorLoversAbilities.crown(record,4)
                && EmperorLoversAbilities.shield(caster))return true;
        }
        return false;
    }
    /** Movement restriction applies to everyone, except owner/explicit allow. */
    public static boolean maySprintOrJump(ServerPlayerEntity subject){
        for(UUID ownerId:new ArrayList<>(DOMAINS.keySet())){
            ServerPlayerEntity owner=subject.getServer().getPlayerManager().getPlayer(ownerId);
            if(owner==null)continue;
            Active a=valid(owner);
            if(a==null || a.garden() || !close(owner,subject,15))continue;
            if(CrownRules.blockMovement(true,subject==owner,
                a.allowed.contains(subject.getUuid())))return false;
        }
        return true;
    }
    /** Passive mobs cannot take any damage inside Garden or fused Crown. */
    public static boolean protectsPassive(LivingEntity target){
        if(!EmperorLoversAbilities.passive(target) ||
            !(target.getWorld() instanceof ServerWorld world))return false;
        for(ServerPlayerEntity caster:world.getPlayers()){
            Active a=valid(caster);
            if(a!=null && (a.garden()||a.crown()) && close(caster,target,15))
                return true;
        }
        return false;
    }
    /** Coin prevents a pacified enemy player attacking the specific caster. */
    public static void pacify(ServerPlayerEntity caster,LivingEntity target,int duration){
        COINS.put(target.getUuid(),new Pact(caster,time(caster)+duration));
        if(target instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
        target.addStatusEffect(new StatusEffectInstance(StatusEffects.SLOWNESS,duration,0));
        target.addStatusEffect(new StatusEffectInstance(StatusEffects.WEAKNESS,duration,0));
    }
    private static boolean challenged(Active a,LivingEntity attacker){return a.challenged.contains(attacker.getUuid());}
    /** Called before vanilla damage applies; does not suppress friendly consensual combat. */
    public static boolean preventAttack(LivingEntity victim,DamageSource source){
        if(!(source.getAttacker() instanceof LivingEntity attacker) ||
            !(victim instanceof ServerPlayerEntity subject))return false;
        Pact pact=COINS.get(attacker.getUuid());
        if(pact!=null && pact.dimension==subject.getWorld() && time(subject)<pact.until
            && subject.getUuid().equals(pact.owner)
            && FoolAbilities.enemy(subject,attacker))return true;
        for(ServerPlayerEntity owner:subject.getServer().getPlayerManager().getPlayerList()){
            Active domain=valid(owner);
            if(domain==null || !domain.garden() || !close(owner,subject,15)
                || !HangedAbilities.ally(owner,subject))continue;
            if(FoolAbilities.enemy(owner,attacker) && !challenged(domain,attacker)
                && close(owner,attacker,15))return true;
        }
        return false;
    }
    /** Attacking a garden visitor ends their pacification for that garden only. */
    public static void onSuccessfulHit(LivingEntity victim,DamageSource source){
        if(!(source.getAttacker() instanceof ServerPlayerEntity attacker))return;
        for(ServerPlayerEntity owner:attacker.getServer().getPlayerManager().getPlayerList()){
            Active a=valid(owner);
            if(a!=null && a.garden() && close(owner,victim,15) &&
                HangedAbilities.ally(owner,attacker) && FoolAbilities.enemy(owner,victim))
                a.challenged.add(victim.getUuid());
        }
    }
    public static void onAnyDeath(LivingEntity victim){
        if(!(victim instanceof PlayerEntity player) ||
            !(victim.getWorld() instanceof ServerWorld world))return;
        for(ServerPlayerEntity owner:world.getPlayers()){
            Active a=valid(owner);
            if(a==null||!a.crown()||!close(owner,victim,15)
                || !HangedAbilities.ally(owner,player))continue;
            for(ServerPlayerEntity ally:world.getPlayers())
                if(ally.isAlive() && close(owner,ally,15)
                    && HangedAbilities.ally(owner,ally))ally.heal(4f);
        }
    }
    public static void tick(ServerPlayerEntity caster,ArcaneSave state,ArcaneSave.Record r){
        Active a=DOMAINS.get(caster.getUuid());
        if(a==null)return;
        long now=time(caster);
        if(valid(caster)==null){
            DOMAINS.remove(caster.getUuid());
            return;
        }
        for(LivingEntity victim:HangedAbilities.enemies(caster,caster.getPos(),15)){
            if(a.emperor() || a.crown()){
                if(victim.squaredDistanceTo(caster)<9) {
                    Vec3d direction=victim.getPos().subtract(caster.getPos());
                    if(direction.lengthSquared()<.001)direction=new Vec3d(1,0,0);
                    direction=direction.normalize().multiply(.5);
                    victim.addVelocity(direction.x,.1,direction.z);
                }
            }
            if((a.crown() && now-a.started<100)
                || (a.garden() && !challenged(a,victim))){
                if(victim instanceof MobEntity mob){
                    mob.setTarget(null);mob.getNavigation().stop();
                }
                victim.addStatusEffect(new StatusEffectInstance(StatusEffects.SLOWNESS,40,0));
            }
        }
        if(a.garden()||a.crown()){
            for(ServerPlayerEntity friend:caster.getWorld().getPlayers()){
                if(!friend.isAlive() || !close(caster,friend,15)
                    || !HangedAbilities.ally(caster,friend))continue;
                friend.addStatusEffect(new StatusEffectInstance(StatusEffects.REGENERATION,60,1));
            }
        }
        if(COINS.size()>2000)
            COINS.entrySet().removeIf(e->e.getValue().until<now);
        state.markDirty();
    }
    public static void stopOnDisconnect(ServerPlayerEntity player){
        DOMAINS.remove(player.getUuid());
        COINS.entrySet().removeIf(e->player.getUuid().equals(e.getValue().owner));
    }
}
