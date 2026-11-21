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
import net.minecraft.item.ItemStack;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Vec3d;

/** Timed visual/combat capstones for Star, Empress and Starless Poison. */
public final class StarlessPoison {
    private StarlessPoison(){}
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static final Map<UUID,Meteor> METEORS=new HashMap<>();
    private static final class Active {
        final String type;
        final ServerWorld world;
        final BlockPos entry;
        final long expires;
        final Set<UUID> poisoned=new HashSet<>();
        Active(ServerPlayerEntity p,String name,int duration){
            type=name;world=p.getWorld();entry=p.getBlockPos();
            expires=time(p)+duration;
        }
        boolean poison(){return "the_starless_poison".equals(type);}
        boolean mirror(){return "the_mirror_world".equals(type);}
        boolean sky(){return "the_starless_sky".equals(type);}
    }
    private static final class Meteor {
        final String type;
        final ServerWorld world;
        int left=5;
        long next;
        Meteor(ServerPlayerEntity p,String type){
            this.type=type;world=p.getWorld();next=time(p);
        }
    }
    private static long time(ServerPlayerEntity p){
        return p.getServer().getOverworld().getTime();
    }
    private static Active valid(ServerPlayerEntity p){
        Active a=ACTIVE.get(p.getUuid());
        return a!=null && p.isAlive() && a.world==p.getWorld()
            && time(p)<a.expires?a:null;
    }
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect what,
                               int ticks,int amp){
        e.addStatusEffect(new StatusEffectInstance(what,ticks,amp));
    }
    public static void recoverFlight(ServerPlayerEntity p){
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=state.getPlayer(p.getUuid());
        if(r!=null && r.mirrorRestorePending && valid(p)==null) {
            p.getAbilities().allowFlying=r.mirrorOldMayFly;
            p.getAbilities().flying=r.mirrorOldFlying && r.mirrorOldMayFly;
            p.sendAbilitiesUpdate();
            r.mirrorRestorePending=false;
            state.markDirty();
        }
    }
    private static void beginFlight(ServerPlayerEntity p,ArcaneSave state,
                                    ArcaneSave.Record r){
        r.mirrorOldMayFly=p.getAbilities().allowFlying;
        r.mirrorOldFlying=p.getAbilities().flying;
        r.mirrorRestorePending=true;
        p.getAbilities().allowFlying=true;
        p.sendAbilitiesUpdate();
        state.markDirty();
    }
    private static boolean safe(ServerPlayerEntity p,BlockPos at) {
        return p.getWorld().getBlockState(at).isAir()
            && p.getWorld().getBlockState(at.up()).isAir()
            && p.getWorld().getWorldBorder().contains(at);
    }
    private static void end(ServerPlayerEntity p,Active a,boolean regular) {
        if(a==null)return;
        if(a.mirror()){
            if(p.getWorld()==a.world) {
                if(p.getPos().squaredDistanceTo(Vec3d.ofCenter(a.entry))>900 ||
                    !safe(p,p.getBlockPos())){
                    BlockPos back=a.entry;
                    if(safe(p,back))p.requestTeleport(back.getX()+.5,back.getY(),back.getZ()+.5);
                }
                if(regular)for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),8)){
                    effect(enemy,StatusEffects.POISON,100,1);
                    effect(enemy,StatusEffects.WITHER,100,1);
                }
            }
            recoverFlight(p);
        }
        if(a.poison() && regular && p.getWorld()==a.world) {
            for(UUID id:a.poisoned) {
                Entity e=a.world.getEntity(id);
                if(e instanceof LivingEntity victim && victim.isAlive() &&
                    victim.hasStatusEffect(StatusEffects.POISON) &&
                    FoolAbilities.enemy(p,victim)){
                    victim.damage(DamageSource.MAGIC,6f);
                    effect(victim,StatusEffects.WITHER,100,0);
                }
            }
            effect(p,StatusEffects.INVISIBILITY,100,0);
        }
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,
                               ArcaneSave.Record r,String name) {
        boolean supported=switch(name) {
            case "the_starless_sky" -> StarEmpressAbilities.star(r,0);
            case "the_mirror_world" -> StarEmpressAbilities.empress(r,0);
            case "the_starless_poison" -> StarEmpressAbilities.poison(r,0);
            default -> false;
        };
        if(!supported || valid(p)!=null)return false;
        int duration=name.equals("the_mirror_world")?500:800;
        int cooldown=name.equals("the_mirror_world")?18000:24000;
        if(!r.ready(name,time(p),cooldown))return false;
        Active a=new Active(p,name,duration);
        ACTIVE.put(p.getUuid(),a);
        if(a.mirror())beginFlight(p,state,r);
        state.markDirty();
        ArcaneMod.info(p,name+" active for "+duration+" ticks.");
        return true;
    }
    public static boolean castMeteor(ServerPlayerEntity p,ArcaneSave state,
                                     ArcaneSave.Record r,String name){
        boolean can=name.equals("apocalypses_herald")
            ?StarEmpressAbilities.empress(r,1)
            :StarEmpressAbilities.poison(r,1);
        if(!can || METEORS.containsKey(p.getUuid()) ||
            !r.ready("apocalypse_meteors",time(p),3600))return false;
        METEORS.put(p.getUuid(),new Meteor(p,name));
        if(name.equals("midnight_apocalypse"))
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),15))
                effect(enemy,StatusEffects.BLINDNESS,60,0);
        state.markDirty();
        return true;
    }
    public static boolean mirrorImmune(ServerPlayerEntity p){
        Active a=valid(p);return a!=null && a.mirror();
    }
    public static float outgoing(ServerPlayerEntity p,LivingEntity victim,
                                 DamageSource src,float amount){
        Active a=valid(p);
        if(a==null || !FoolAbilities.enemy(p,victim))return amount;
        if(a.sky() || a.poison())amount*=1.20f;
        if(a.poison() && victim.hasStatusEffect(StatusEffects.POISON))
            amount*=1.25f;
        return amount;
    }
    public static void onSuccessfulHit(ServerPlayerEntity p,LivingEntity victim,
                                       DamageSource src,ArcaneSave.Record r) {
        Active a=valid(p);
        if(a==null || !FoolAbilities.enemy(p,victim))return;
        if(a.poison() && src.getSource()==p) {
            // Enemy only, and a critical melee hit is allowed to reveal the caster.
            if(p.fallDistance>0 && !p.isOnGround())
                effect(p,StatusEffects.GLOWING,40,0);
            a.poisoned.add(victim.getUuid());
        }
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity killed,
                              ArcaneSave state,ArcaneSave.Record r){
        Active a=valid(p);
        if(a==null || !a.poison() || !a.poisoned.contains(killed.getUuid()))return;
        for(LivingEntity other:HangedAbilities.enemies(p,killed.getPos(),3)){
            if(other!=killed){
                effect(other,StatusEffects.POISON,100,0);
                a.poisoned.add(other.getUuid());
            }
        }
        a.world.spawnParticles(ParticleTypes.WITCH,
            killed.getX(),killed.getY()+.5,killed.getZ(),20,1,1,1,.04);
        state.markDirty();
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        long now=time(p);
        Active a=ACTIVE.get(p.getUuid());
        if(a!=null) {
            if(valid(p)==null){
                ACTIVE.remove(p.getUuid());end(p,a,p.isAlive() && a.world==p.getWorld());
            }else {
                if(a.mirror()){
                    effect(p,StatusEffects.INVISIBILITY,40,0);
                    // Never let client flight state leak past the capstone timer.
                    p.getAbilities().allowFlying=true;
                    if(now%100==0)p.sendAbilitiesUpdate();
                }
                if(a.sky() || a.poison()){
                    effect(p,StatusEffects.INVISIBILITY,40,0);
                    effect(p,StatusEffects.SPEED,40,1);
                    for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),30)){
                        effect(enemy,StatusEffects.BLINDNESS,40,0);
                        effect(enemy,StatusEffects.SLOWNESS,40,0);
                        if(a.poison() && now%60==0) {
                            effect(enemy,StatusEffects.POISON,80,1);
                            a.poisoned.add(enemy.getUuid());
                        }
                    }
                    // APPROX: server particle/darkness rather than breaking
                    // light-source blocks in a 30-block radius.
                    if(now%100==0)a.world.spawnParticles(ParticleTypes.SMOKE,
                        p.getX(),p.getY()+1,p.getZ(),50,15,3,15,.01);
                }
            }
        }
        Meteor meteor=METEORS.get(p.getUuid());
        if(meteor!=null) {
            if(p.getWorld()!=meteor.world || !p.isAlive() || meteor.left<=0) {
                METEORS.remove(p.getUuid());
            }else if(now>=meteor.next) {
                meteor.next=now+40;
                meteor.left--;
                int dx=p.getRandom().nextInt(21)-10, dz=p.getRandom().nextInt(21)-10;
                Vec3d impact=p.getPos().add(dx,0,dz);
                meteor.world.spawnParticles(ParticleTypes.FLAME,
                    impact.x,impact.y+5,impact.z,30,2,3,2,.1);
                meteor.world.spawnParticles(ParticleTypes.EXPLOSION,
                    impact.x,impact.y+.5,impact.z,4,.6,.5,.6,.01);
                for(LivingEntity enemy:HangedAbilities.enemies(p,impact,4)){
                    enemy.damage(DamageSource.MAGIC,6f);
                    enemy.setOnFireFor(3);
                    if(meteor.type.equals("midnight_apocalypse")){
                        effect(enemy,StatusEffects.POISON,60,1);
                        effect(enemy,StatusEffects.BLINDNESS,60,0);
                    }
                }
                if(meteor.left==0)METEORS.remove(p.getUuid());
            }
        }
    }
    public static boolean exitMirror(ServerPlayerEntity p) {
        Active a=valid(p);
        if(a==null || !a.mirror())return false;
        ACTIVE.remove(p.getUuid());
        end(p,a,true);
        return true;
    }
    public static void stopOnDisconnect(ServerPlayerEntity p) {
        METEORS.remove(p.getUuid());
        Active a=ACTIVE.remove(p.getUuid());
        if(a!=null)end(p,a,false);
        recoverFlight(p);
    }
}
