package club.tarot.arcane;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.tag.TagKey;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;

/** Sun fixed zone + Moon moving aura, combined at Sequence1 Eclipse. */
public final class Eclipse {
    private Eclipse(){}
    private static final TagKey<EntityType<?>> UNDEAD=TagKey.of(
        Registry.ENTITY_TYPE_KEY,new Identifier("tarot","undead"));
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static final class Active {
        final String id;
        final ServerWorld world;
        final Vec3d sunCenter;
        final long begins;
        final long end;
        float healed;
        boolean finalPulse;
        Active(ServerPlayerEntity p,String id,int duration){
            this.id=id;this.world=p.getWorld();this.sunCenter=p.getPos();
            this.begins=time(p);this.end=begins+duration;
        }
        boolean sun(){return id.equals("the_eternal_day") || id.equals("the_eclipse");}
        boolean moon(){return id.equals("the_scarlet_feast") || id.equals("the_eclipse");}
        boolean fused(){return id.equals("the_eclipse");}
    }
    private static long time(ServerPlayerEntity p){return p.getServer().getOverworld().getTime();}
    private static Active valid(ServerPlayerEntity p){
        Active a=ACTIVE.get(p.getUuid());
        if(a==null||a.world!=p.getWorld()||time(p)>=a.end||!p.isAlive())return null;
        return a;
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,
                               ArcaneSave.Record r,String skill){
        boolean allowed=switch(skill){
            case "the_eternal_day" -> SunMoonAbilities.sun(r,0);
            case "the_scarlet_feast" -> SunMoonAbilities.moon(r,0);
            case "the_eclipse" -> SunMoonAbilities.eclipse(r,0);
            default -> false;
        };
        if(!allowed || valid(p)!=null)return false;
        long now=time(p);
        if(!r.ready(skill,now,24000))return false;
        int duration=skill.equals("the_eternal_day")?2400:
            skill.equals("the_scarlet_feast")?600:1200;
        ACTIVE.put(p.getUuid(),new Active(p,skill,duration));
        state.markDirty();
        ArcaneMod.info(p,skill+" active for "+duration+" ticks.");
        return true;
    }
    private static boolean undead(Entity entity){return entity.getType().isIn(UNDEAD);}
    private static void effect(LivingEntity entity,net.minecraft.entity.effect.StatusEffect what,
                               int ticks,int level){
        entity.addStatusEffect(new StatusEffectInstance(what,ticks,level));
    }
    private static boolean ally(ServerPlayerEntity owner,PlayerEntity other){
        return HangedAbilities.ally(owner,other);
    }
    /** At most 30 HP total across all recipients during this one capstone. */
    private static void distributeHealing(ServerPlayerEntity owner,Active a,float amount,double radius){
        float allowed=Math.min(Math.max(0,30f-a.healed),amount);
        if(allowed<=0)return;
        for(ServerPlayerEntity friend:owner.getWorld().getEntitiesByClass(ServerPlayerEntity.class,
            new Box(owner.getBlockPos()).expand(radius),
            p->p.isAlive() && ally(owner,p) && p.squaredDistanceTo(owner)<=radius*radius)){
            float missing=Math.max(0,friend.getMaxHealth()-friend.getHealth());
            float given=Math.min(missing,allowed);
            if(given>0){
                friend.heal(given);a.healed+=given;allowed-=given;
                if(allowed<=0)break;
            }
        }
    }
    private static void sunPulse(ServerPlayerEntity caster,Active a,long t){
        Vec3d center=a.sunCenter;
        Box region=new Box(center,center).expand(30);
        for(LivingEntity entity:a.world.getEntitiesByClass(LivingEntity.class,region,
            e->e.isAlive() && e.squaredDistanceTo(center)<=900)){
            if(undead(entity)){
                entity.damage(DamageSource.MAGIC,SunMoonRules.fixedSunPulse(true,false));
                if(a.fused() && entity.isAlive())entity.setOnFireFor(2);
            }else if(entity instanceof PlayerEntity other) {
                if(other!=caster && FoolAbilities.enemy(caster,other))
                    entity.damage(DamageSource.MAGIC,SunMoonRules.fixedSunPulse(false,true));
                else if(ally(caster,other)){
                    effect(entity,StatusEffects.REGENERATION,60,0);
                    effect(entity,StatusEffects.NIGHT_VISION,260,0);
                    if(t%200==0)entity.heal(2f);
                }
            }
            // Discard only newly spawned tagged hostiles in the fixed zone.
            // Existing hostile mobs still receive their ordinary damage.
            if(entity instanceof MobEntity mob && FoolAbilities.enemy(caster,mob)
                && mob.age<=20)
                mob.discard();
        }
        a.world.spawnParticles(ParticleTypes.END_ROD,
            center.x,center.y+2,center.z,15,15,2,15,.01);
    }
    private static void moonPulse(ServerPlayerEntity p,Active a,long t){
        float total=0f;
        for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),15)){
            if(enemy instanceof PlayerEntity && t%60!=0)continue;
            float damage=Math.min(2f,Math.max(0,enemy.getHealth()));
            if(damage<=0 || !enemy.damage(DamageSource.MAGIC,damage))continue;
            total+=damage;
            if(a.fused() && undead(enemy))enemy.setOnFireFor(2);
        }
        if(total>0)distributeHealing(p,a,total,15);
        a.world.spawnParticles(ParticleTypes.WITCH,p.getX(),p.getY()+1,p.getZ(),
            15,8,2,8,.02);
    }
    private static void finalPulse(ServerPlayerEntity caster,Active a){
        a.finalPulse=true;
        for(LivingEntity entity:a.world.getEntitiesByClass(LivingEntity.class,
            new Box(a.sunCenter,a.sunCenter).expand(30),
            e->e.isAlive() && e.squaredDistanceTo(a.sunCenter)<=900)){
            if(undead(entity))entity.damage(DamageSource.MAGIC,10f);
            if(entity instanceof PlayerEntity player){
                if(ally(caster,player))player.heal(10f);
                else if(FoolAbilities.enemy(caster,player))
                    effect(player,StatusEffects.BLINDNESS,300,0);
            }
        }
        a.world.spawnParticles(ParticleTypes.FLASH,a.sunCenter.x,a.sunCenter.y+2,
            a.sunCenter.z,1,0,0,0,0);
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        Active a=ACTIVE.get(p.getUuid());
        if(a==null)return;
        long t=time(p);
        if(valid(p)==null){ACTIVE.remove(p.getUuid());return;}
        if(a.fused() && !a.finalPulse && t>=a.begins+1180)finalPulse(p,a);
        if(t%20==0){
            if(a.sun())sunPulse(p,a,t);
            if(a.moon())moonPulse(p,a,t);
        }
        state.markDirty();
    }
    public static void stopOnDisconnect(ServerPlayerEntity p){
        ACTIVE.remove(p.getUuid());
    }
}
