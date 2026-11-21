package club.tarot.arcane;

import java.util.Comparator;
import java.util.List;
import java.util.Random;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.minecraft.block.BedBlock;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Items;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.tag.TagKey;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;
import java.util.UUID;

/** Star, Empress and fused early-game passives. No KubeJS hooks. */
public final class StarEmpressAbilities {
    private StarEmpressAbilities(){}
    private static final Random RNG=new Random();
    private static final UUID WITCH_SPEED=UUID.fromString("a2116e73-0a78-4bc5-8bf2-fd0f5b83bac1");
    private static final UUID NIGHT_SPEED=UUID.fromString("a2116e73-0a78-4bc5-8bf2-fd0f5b83bac2");
    private static final TagKey<EntityType<?>> UNDEAD=TagKey.of(
        Registry.ENTITY_TYPE_KEY,new Identifier("tarot","undead"));
    private static final TagKey<EntityType<?>> PASSIVE=TagKey.of(
        Registry.ENTITY_TYPE_KEY,new Identifier("tarot","passive"));

    static boolean star(ArcaneSave.Record r,int s){
        return r!=null&&r.originValid&&r.profile.active("star",s);
    }
    static boolean empress(ArcaneSave.Record r,int s){
        return r!=null&&r.originValid&&r.profile.active("empress",s);
    }
    static boolean poison(ArcaneSave.Record r,int s){
        return r!=null&&r.originValid&&r.profile.active("starless_poison",s);
    }
    static boolean starIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("star");
    }
    static boolean empressIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("empress");
    }
    private static long time(ServerPlayerEntity p){
        return p.getServer().getOverworld().getTime();
    }
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect what,
                               int duration,int amplifier){
        e.addStatusEffect(new StatusEffectInstance(what,duration,amplifier));
    }
    private static void mod(ServerPlayerEntity p,UUID id,String label,double value,boolean active){
        EntityAttributeInstance attr=p.getAttributeInstance(EntityAttributes.GENERIC_MOVEMENT_SPEED);
        if(attr==null)return;
        if(attr.getModifier(id)!=null)attr.removeModifier(id);
        if(active)attr.addTemporaryModifier(new EntityAttributeModifier(
            id,label,value,EntityAttributeModifier.Operation.MULTIPLY_TOTAL));
    }
    private static boolean dark(ServerPlayerEntity p,int limit){
        return p.getWorld().getLightLevel(p.getBlockPos())<=limit;
    }
    static boolean sun(ServerPlayerEntity p){
        return p.getWorld().isDay() && p.getWorld().isSkyVisible(p.getBlockPos())
            && p.getWorld().getLightLevel(p.getBlockPos())>=12;
    }
    private static boolean nightBuff(ServerPlayerEntity p,ArcaneSave.Record r){
        return (p.getWorld().isNight() || (star(r,4) && dark(p,7)));
    }
    public static void register(){
        UseBlockCallback.EVENT.register((player,world,hand,hit)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p)
                || hand!=Hand.MAIN_HAND)return ActionResult.PASS;
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            if(starIdentity(r) && world.getBlockState(hit.getBlockPos()).getBlock()
                instanceof BedBlock){
                // This prevents sleeping but retains the ordinary respawn goal.
                p.setSpawnPoint(world.getRegistryKey(),hit.getBlockPos(),p.getYaw(),false,true);
                ArcaneMod.info(p,"True Sleeplessness: spawn set, but you cannot sleep.");
                return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
        UseEntityCallback.EVENT.register((player,world,hand,target,hit)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p)
                || hand!=Hand.MAIN_HAND || !(target instanceof LivingEntity victim))
                return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            long now=time(p);
            if(p.isSneaking() && (empress(r,8)||poison(r,8)) &&
                target.getType().isIn(PASSIVE) &&
                r.ready("witch_whisper",now,1200)){
                // Passive animals don't have attack goals: move toward a nearby
                // non-owner player, never change team data or cause forced PvP.
                PlayerEntity nearest=p.getWorld().getEntitiesByClass(PlayerEntity.class,
                    new Box(victim.getBlockPos()).expand(12),v->v!=p && v.isAlive())
                    .stream().min(Comparator.comparingDouble(victim::squaredDistanceTo))
                    .orElse(null);
                if(nearest!=null && victim instanceof MobEntity mob){
                    mob.getNavigation().startMovingTo(nearest,1.3);
                    effect(victim,StatusEffects.SPEED,200,0);
                }
                state.markDirty();return ActionResult.SUCCESS;
            }
            if(target instanceof PlayerEntity && FoolAbilities.enemy(p,target) &&
                (empress(r,6)||poison(r,6)) && r.ready("thread",now,400)){
                effect(victim,StatusEffects.SLOWNESS,40,0);
                state.markDirty();return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
    }
    public static float incoming(ServerPlayerEntity victim,DamageSource source,float value){
        ArcaneSave.Record r=ArcaneMod.profile(victim);
        if(r==null)return value;
        if(empressIdentity(r) && sun(victim))
            value*=StarEmpressRules.exposedArrowMultiplier(true,source.isProjectile());
        if(StarlessPoison.mirrorImmune(victim))return 0f;
        return value;
    }
    public static float outgoing(ServerPlayerEntity owner,LivingEntity victim,
                                 DamageSource source,float value){
        ArcaneSave.Record r=ArcaneMod.profile(owner);
        if(r==null || !FoolAbilities.enemy(owner,victim))return value;
        if((star(r,9)||poison(r,9)) && victim.getType().isIn(UNDEAD)
            && nightBuff(owner,r))value*=1.15f;
        if(poison(r,4) && nightBuff(owner,r) && victim.hasStatusEffect(StatusEffects.POISON))
            value*=1.15f;
        return StarlessPoison.outgoing(owner,victim,source,value);
    }
    public static void onTakenDamage(ServerPlayerEntity p,DamageSource source,float taken){
        if(taken<=0)return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        if((star(r,6)||poison(r,6)) && nightBuff(p,r) && RNG.nextDouble()<.1)
            effect(p,StatusEffects.RESISTANCE,40,0);
        if((empress(r,9)) && dark(p,15)==false &&
            source.getAttacker() instanceof LivingEntity enemy &&
            FoolAbilities.enemy(p,enemy) && r.ready("reflected_beauty",time(p),400))
            effect(enemy,StatusEffects.NAUSEA,40,0);
        if(poison(r,2) && source.getAttacker() instanceof LivingEntity enemy &&
            FoolAbilities.enemy(p,enemy) && r.ready("shadow_whisper",time(p),400)){
            enemy.damage(DamageSource.MAGIC,2f);
            effect(enemy,StatusEffects.BLINDNESS,20,0);
            effect(enemy,StatusEffects.POISON,40,0);
            effect(p,StatusEffects.SPEED,40,0);
        }
        state.markDirty();
    }
    public static void onSuccessfulHit(ServerPlayerEntity p,LivingEntity target,DamageSource src){
        if(!FoolAbilities.enemy(p,target))return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        long now=time(p);
        if(src.getSource()==p && (empress(r,9)||poison(r,5))
            && r.ready("witch_venom",now,240)){
            effect(target,StatusEffects.POISON,empress(r,5)||poison(r,5)?80:60,0);
            if(empress(r,5)||poison(r,5))effect(target,StatusEffects.HUNGER,40,0);
        }
        if(src.getSource()==p && (empress(r,7)||poison(r,7)) && RNG.nextDouble()<.1)
            target.setOnFireFor(1);
        if(poison(r,3) && p.hasStatusEffect(StatusEffects.INVISIBILITY)
            && r.ready("poison_conceal",now,200)){
            effect(target,StatusEffects.POISON,80,1);
            effect(target,StatusEffects.GLOWING,40,0);
        }
        StarlessPoison.onSuccessfulHit(p,target,src,r);
        state.markDirty();
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity dead){
        if(!FoolAbilities.enemy(p,dead))return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        if((star(r,7)||poison(r,7)) && nightBuff(p,r) && RNG.nextDouble()<.20)
            p.addExperience(1);
        StarlessPoison.onKill(p,dead,state,r);
        state.markDirty();
    }
    public static float exhaustion(ServerPlayerEntity player,float value){
        ArcaneSave.Record r=ArcaneMod.profile(player);
        if(r==null)return value;
        if((star(r,9)||poison(r,9)) && player.getWorld().isNight())value*=.80f;
        if(empress(r,3) && (player.isSprinting()||player.isFallFlying()))
            value=Math.max(0,value-1f);
        return value;
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        long now=time(p);
        if(star(r,9)||empress(r,9)||poison(r,9)){
            if(star(r,9)||poison(r,9))effect(p,StatusEffects.NIGHT_VISION,260,0);
            if(empress(r,9)||poison(r,9))p.removeStatusEffect(StatusEffects.POISON);
        }
        if(empress(r,9) && p.isSneaking() && dark(p,7) && !sun(p))
            effect(p,StatusEffects.INVISIBILITY,40,0);
        if((star(r,8)||poison(r,8))){
            if(p.isSneaking())r.starSneakTicks+=20;else r.starSneakTicks=0;
            if(r.starSneakTicks>=60 && r.ready("lullaby",now,1200)){
                for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),5))
                    effect(enemy,StatusEffects.SLOWNESS,60,0);
                r.starSneakTicks=0;
            }
        }
        if(empress(r,1)){
            if(p.isSneaking())r.empressSneakTicks+=20;else r.empressSneakTicks=0;
            if(r.empressSneakTicks>=60 && r.ready("petrifying_gaze",now,1200)){
                for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),6))
                    effect(enemy,StatusEffects.SLOWNESS,60,1);
                r.empressSneakTicks=0;
            }
        }
        if(star(r,2) && r.ready("conceal",now,3600))
            effect(p,StatusEffects.INVISIBILITY,100,0);
        if((empress(r,4)||poison(r,4)) && now%40==0 && RNG.nextDouble()<.10)
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),5)){
                if(enemy instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
                effect(enemy,StatusEffects.SLOWNESS,40,0);
                if(poison(r,4))effect(enemy,StatusEffects.POISON,60,0);
            }
        double witch=(empress(r,9)||poison(r,9))?.10:0;
        double night=(star(r,9)||poison(r,9)) && nightBuff(p,r)?.15:0;
        mod(p,WITCH_SPEED,"Witch's Grace",witch,witch>0);
        mod(p,NIGHT_SPEED,"Nightwatch",night,night>0);
        StarlessPoison.tick(p,state,r);
        state.markDirty();
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id){
        long now=time(p);
        switch(id){
            case "haunt":case "haunting_plague":{
                if(!(star(r,5)||poison(r,5)))return false;
                LivingEntity victim=HangedAbilities.enemies(p,p.getPos(),6).stream()
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(victim==null || !r.ready("haunt",now,900))return false;
                effect(victim,StatusEffects.BLINDNESS,60,0);
                if(poison(r,5))effect(victim,StatusEffects.POISON,60,0);
                break;
            }
            case "misfortune":{
                if(!star(r,1)||!r.ready("misfortune",now,1800))return false;
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),10)){
                    effect(e,StatusEffects.SLOWNESS,160,1);
                    effect(e,StatusEffects.WEAKNESS,160,1);
                    effect(e,StatusEffects.BLINDNESS,60,0);
                }
                break;
            }
            case "mirror_passage":{
                if(!empress(r,2))return false;
                BlockPos dest=null;boolean crossed=false;
                for(int step=1;step<=10;step++){
                    BlockPos candidate=p.getBlockPos().offset(p.getHorizontalFacing(),step);
                    if(p.getWorld().getBlockState(candidate).isOf(net.minecraft.block.Blocks.GLASS))
                        crossed=true;
                    else if(crossed && p.getWorld().getBlockState(candidate).isAir()
                        && p.getWorld().getBlockState(candidate.up()).isAir()
                        && p.getWorld().getWorldBorder().contains(candidate)) {
                        dest=candidate;break;
                    }
                }
                if(dest==null || !r.ready("mirror_passage",now,3600))return false;
                p.requestTeleport(dest.getX()+.5,dest.getY(),dest.getZ()+.5);
                break;
            }
            case "apocalypses_herald":case "midnight_apocalypse":
                return StarlessPoison.castMeteor(p,state,r,id);
            case "the_starless_sky":case "the_mirror_world":case "the_starless_poison":
                return StarlessPoison.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    public static void stopOnDisconnect(ServerPlayerEntity p){
        StarlessPoison.stopOnDisconnect(p);
        mod(p,WITCH_SPEED,"Witch's Grace",0,false);
        mod(p,NIGHT_SPEED,"Nightwatch",0,false);
    }
}
