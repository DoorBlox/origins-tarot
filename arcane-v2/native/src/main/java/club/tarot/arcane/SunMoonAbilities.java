package club.tarot.arcane;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.List;
import java.util.Random;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.block.BrewingStandBlock;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.block.entity.BrewingStandBlockEntity;
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
import net.minecraft.entity.mob.VexEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.potion.PotionUtil;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.tag.TagKey;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.Identifier;
import net.minecraft.util.TypedActionResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;

/** Sun / Moon / Eclipse low and middle sequence mechanics, no KubeJS. */
public final class SunMoonAbilities {
    private SunMoonAbilities(){}
    private static final Random RANDOM=new Random();
    private static final TagKey<EntityType<?>> UNDEAD=TagKey.of(
        Registry.ENTITY_TYPE_KEY,new Identifier("tarot","undead"));
    private static final TagKey<EntityType<?>> PASSIVE=TagKey.of(
        Registry.ENTITY_TYPE_KEY,new Identifier("tarot","passive"));
    private static final TagKey<net.minecraft.item.Item> MEAT=TagKey.of(
        Registry.ITEM_KEY,new Identifier("tarot","meat"));
    private static final UUID NIGHT_SPEED=UUID.fromString("1c98d1ac-883f-4c5e-b870-ec3d1391edb1");
    private static final Map<UUID,Revival> REVIVED=new HashMap<>();
    private static final Map<UUID,Long> TAMED=new HashMap<>();
    private record Revival(UUID owner,long expires) {}
    static boolean sun(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("sun",seq);
    }
    static boolean moon(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("moon",seq);
    }
    static boolean eclipse(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("eclipse",seq);
    }
    static boolean sunIdentity(ArcaneSave.Record r) {
        return r!=null&&r.originValid&&r.profile.identityActive("sun");
    }
    static boolean moonIdentity(ArcaneSave.Record r) {
        return r!=null&&r.originValid&&r.profile.identityActive("moon");
    }
    private static long time(ServerPlayerEntity p) {
        return p.getServer().getOverworld().getTime();
    }
    private static void effect(LivingEntity p,net.minecraft.entity.effect.StatusEffect e,
                               int ticks,int level){
        p.addStatusEffect(new StatusEffectInstance(e,ticks,level));
    }
    private static boolean undead(Entity target){return target.getType().isIn(UNDEAD);}
    private static boolean passive(Entity target){return target.getType().isIn(PASSIVE);}
    private static void speed(ServerPlayerEntity p,boolean enabled) {
        EntityAttributeInstance attr=p.getAttributeInstance(EntityAttributes.GENERIC_MOVEMENT_SPEED);
        if(attr==null)return;
        if(attr.getModifier(NIGHT_SPEED)!=null)attr.removeModifier(NIGHT_SPEED);
        if(enabled)attr.addTemporaryModifier(new EntityAttributeModifier(NIGHT_SPEED,
            "Sanguine Sight",.15,EntityAttributeModifier.Operation.MULTIPLY_TOTAL));
    }
    private static boolean night(ServerPlayerEntity p){return p.getWorld().isNight();}
    private static List<ServerPlayerEntity> allies(ServerPlayerEntity p,double radius){
        return p.getWorld().getEntitiesByClass(ServerPlayerEntity.class,
            new Box(p.getBlockPos()).expand(radius),x->x.isAlive()
            && x.squaredDistanceTo(p)<=radius*radius && HangedAbilities.ally(p,x));
    }
    private static void pacify(LivingEntity e,int ticks){
        if(e instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
        effect(e,StatusEffects.SLOWNESS,ticks,0);
    }
    public static void register(){
        UseItemCallback.EVENT.register((player,world,hand)->{
            ItemStack held=player.getStackInHand(hand);
            if(world.isClient || !(player instanceof ServerPlayerEntity p))
                return TypedActionResult.pass(held);
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return TypedActionResult.pass(held);
            if((moon(r,9)||moon(r,1)||eclipse(r,5))
                && held.isOf(Items.POTION)
                && PotionUtil.getPotionEffects(held).stream().anyMatch(x->
                    x.getEffectType()==StatusEffects.INSTANT_HEALTH)){
                r.moonPotionUntil=time(p)+60;
                ArcaneSave.get(p.getServer()).markDirty();
            }
            return TypedActionResult.pass(held);
        });
        UseEntityCallback.EVENT.register((player,world,hand,target,hit)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p)
                || hand!=Hand.MAIN_HAND || !(target instanceof LivingEntity e))
                return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            long now=time(p);
            if((sun(r,6)||eclipse(r,6)) && target instanceof PlayerEntity other
                && other!=p){
                r.witnessTarget=other.getUuid();r.witnessUntil=now+1200;
                ArcaneMod.info(p,"Witness: "+other.getName().getString()+" "+
                    Math.round(e.getHealth())+"/"+Math.round(e.getMaxHealth())+" HP.");
                state.markDirty();return ActionResult.SUCCESS;
            }
            if((moon(r,8)||eclipse(r,8)) && passive(e)
                && p.getMainHandStack().isOf(Items.BONE) &&
                r.ready("tame",now,1200)){
                TAMED.put(e.getUuid(),now+1200);
                effect(e,StatusEffects.SLOWNESS,1200,0);
                state.markDirty();return ActionResult.SUCCESS;
            }
            if(moon(r,3) && passive(e) && r.ready("summon",now,1200)){
                // APPROX: a bounded owner-guarded Vex is a temporary
                // combat proxy for a harmless animal that lacks attack AI.
                VexEntity minion=HangedAbilities.spawnMinion(p,200,false,0,0);
                if(minion==null)return ActionResult.PASS;
                state.markDirty();return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
        UseBlockCallback.EVENT.register((player,world,hand,hit)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p)
                || hand!=Hand.MAIN_HAND)return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            BlockPos pos=hit.getBlockPos();
            if((moon(r,6)||eclipse(r,6)) &&
                world.getBlockState(pos).getBlock() instanceof BrewingStandBlock &&
                world.getBlockEntity(pos) instanceof BrewingStandBlockEntity stand) {
                NbtCompound nbt=stand.createNbt();
                if(nbt.getShort("BrewTime")<=0 || !r.ready("brew",time(p),6000))
                    return ActionResult.PASS;
                nbt.putShort("BrewTime",(short)1);
                stand.readNbt(nbt);
                stand.markDirty();
                state.markDirty();
                ArcaneMod.info(p,"Instant Brew accelerated the current potion recipe.");
                return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
    }
    public static boolean blocksFood(ServerPlayerEntity p,ItemStack consumed){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return moonIdentity(r) && !consumed.isIn(MEAT);
    }
    public static boolean fireImmune(ServerPlayerEntity p,DamageSource damage){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && (sun(r,9)||eclipse(r,9)) && damage.isFire();
    }
    public static float potionHealingMultiplier(ServerPlayerEntity p,float heal){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return heal;
        long t=time(p);
        if(t>r.moonPotionUntil)return heal;
        float bonus=moon(r,1)?1.35f:moon(r,9)?1.25f:1f;
        if((moon(r,5)||eclipse(r,5)) && t<r.scarletUntil)bonus*=1.50f;
        return heal*bonus;
    }
    public static float outgoing(ServerPlayerEntity p,LivingEntity victim,
                                 DamageSource source,float amount){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null||!FoolAbilities.enemy(p,victim))return amount;
        if(undead(victim)){
            if(sun(r,4))amount*=1.50f;
            else if(sun(r,9)||eclipse(r,9))amount*=1.40f;
        }
        return amount;
    }
    public static void onTakenDamage(ServerPlayerEntity p,DamageSource source,float taken){
        if(taken<=0)return;
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        if(night(p) && (moon(r,9)||eclipse(r,9)) && RANDOM.nextDouble()<.1)
            p.removeStatusEffect(StatusEffects.WITHER);
        if((sun(r,7)||eclipse(r,7)) && source.getAttacker() instanceof LivingEntity attacker
            && undead(attacker) && FoolAbilities.enemy(p,attacker) && RANDOM.nextDouble()<.2)
            effect(attacker,StatusEffects.BLINDNESS,40,0);
    }
    public static void onSuccessfulHit(ServerPlayerEntity p,LivingEntity victim,
                                       DamageSource src){
        if(!FoolAbilities.enemy(p,victim))return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        if(src.getSource()==p && (moon(r,7)||eclipse(r,7)) &&
            r.ready("blood_drain",time(p),100))p.heal(1f);
        if(eclipse(r,4) && undead(victim) && src.getSource()==p) {
            p.heal(2f);
            victim.setOnFireFor(2);
        }
        state.markDirty();
    }
    public static void onAnyDeath(LivingEntity victim){
        if(!passive(victim) || victim.getScoreboardTags().contains("tarot_revived_life")
            || !(victim.getWorld() instanceof ServerWorld world))return;
        for(ServerPlayerEntity owner:world.getPlayers()){
            ArcaneSave state=ArcaneSave.get(owner.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(owner);
            if(r==null||!moon(r,2) || owner.squaredDistanceTo(victim)>64
                || !r.ready("life",time(owner),3600))continue;
            Entity duplicate=victim.getType().create(world);
            if(duplicate instanceof LivingEntity resurrected){
                resurrected.refreshPositionAndAngles(victim.getX(),victim.getY(),
                    victim.getZ(),0,0);
                resurrected.addScoreboardTag("tarot_revived_life");
                resurrected.addScoreboardTag("tarot_owner_"+owner.getUuidAsString());
                world.spawnEntity(resurrected);
                REVIVED.put(resurrected.getUuid(),new Revival(owner.getUuid(),time(owner)+400));
                state.markDirty();
                break;
            }
        }
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        long t=time(p);
        if(sunIdentity(r))effect(p,StatusEffects.GLOWING,60,0);
        if(sun(r,9)||eclipse(r,9)){
            effect(p,StatusEffects.NIGHT_VISION,260,0);
            if((sun(r,9)) && t%900==0){
                p.removeStatusEffect(StatusEffects.POISON);
                p.removeStatusEffect(StatusEffects.WEAKNESS);
            }
        }
        if(moon(r,9)||eclipse(r,9)){
            effect(p,StatusEffects.NIGHT_VISION,260,0);
            speed(p,night(p));
            if(night(p) && r.ready("bloods_renewal",t,600))
                p.heal(moon(r,4)?3f:1f);
        } else speed(p,false);
        if((sun(r,8)||eclipse(r,8))){
            if(p.isSneaking())r.sunCrouchTicks+=20;else r.sunCrouchTicks=0;
            if(r.sunCrouchTicks>=60 && r.ready("holy_light",t,600)){
                p.heal(2f);r.sunCrouchTicks=0;
            }
        }
        if(sun(r,1) && t%100==0)
            for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),20))
                effect(e,StatusEffects.GLOWING,100,0);
        if((sun(r,9)) && p.isOnGround() && !p.isSprinting() &&
            p.getVelocity().horizontalLengthSquared()<.001 &&
            p.getWorld().getLightLevel(p.getBlockPos())<=4){
            r.sunStillTicks+=20;
            if(r.sunStillTicks>=100 && t%100==0) {
                double radius=sun(r,3)?5:3;
                p.getWorld().spawnParticles(net.minecraft.particle.ParticleTypes.END_ROD,
                    p.getX(),p.getY()+1,p.getZ(),25,radius,2,radius,.015);
                effect(p,StatusEffects.NIGHT_VISION,200,0);
            }
        }else r.sunStillTicks=0;
        if(r.witnessTarget!=null && t<r.witnessUntil && t%100==0
            && (sun(r,6)||eclipse(r,6))){
            Entity target=p.getWorld().getEntity(r.witnessTarget);
            if(target instanceof LivingEntity e)
                ArcaneMod.info(p,"Witness: "+e.getName().getString()+" HP="+Math.round(e.getHealth()));
        }
        if(r.sanctifyUntil>t && (sun(r,2)||eclipse(r,2))){
            for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),5)){
                if(undead(e))e.damage(DamageSource.MAGIC,2f);
                if(eclipse(r,2) && night(p) && t%40==0){
                    e.damage(DamageSource.MAGIC,2f);p.heal(2f);
                }
            }
        }
        if(r.whiteAngelUntil>t && (sun(r,1)||eclipse(r,1))){
            p.getWorld().spawnParticles(net.minecraft.particle.ParticleTypes.END_ROD,
                p.getX(),p.getY()+1,p.getZ(),20,10,1,10,.01);
            if(t%20==0) {
                if(eclipse(r,1))p.heal(1f);
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),15))
                    if(undead(e))e.damage(DamageSource.MAGIC,eclipse(r,1)?6f:4f);
            }
            for(ServerPlayerEntity ally:allies(p,15))
                effect(ally,StatusEffects.REGENERATION,40,0);
        }
        Eclipse.tick(p,state,r);
        // Remove expiring tames and revived minions without touching vanilla mobs.
        if(t%100==0){
            TAMED.entrySet().removeIf(x->x.getValue()<=t);
            REVIVED.entrySet().removeIf(x->{
                if(x.getValue().expires()>t)return false;
                Entity entity=p.getWorld().getEntity(x.getKey());
                if(entity!=null && entity.getScoreboardTags().contains("tarot_revived_life"))
                    entity.discard();
                return true;
            });
        }
        state.markDirty();
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id){
        long now=time(p);
        switch(id){
            case "purify":case "purify_scarlet":{
                if(!(sun(r,5)||eclipse(r,5)))return false;
                int cd=eclipse(r,5)?1200:900;
                if(!r.ready("purify",now,cd))return false;
                p.removeStatusEffect(StatusEffects.POISON);
                p.removeStatusEffect(StatusEffects.WITHER);
                p.removeStatusEffect(StatusEffects.BLINDNESS);
                // Global ally rule: a Purify may also cleanse an eligible
                // nearby teammate, never a hostile player.
                for(ServerPlayerEntity ally:allies(p,4)){
                    ally.removeStatusEffect(StatusEffects.POISON);
                    ally.removeStatusEffect(StatusEffects.WITHER);
                    ally.removeStatusEffect(StatusEffects.BLINDNESS);
                }
                if(eclipse(r,5)){
                    r.scarletUntil=now+200;
                    effect(p,StatusEffects.REGENERATION,100,0);
                }
                break;
            }
            case "scarlet":{
                if(!moon(r,5)||!r.ready(id,now,1200))return false;
                r.scarletUntil=now+200;break;
            }
            case "sanctify":case "lunar_sanctuary":{
                if(!(sun(r,2)||eclipse(r,2)) || !r.ready("sanctify",now,3600))return false;
                r.sanctifyUntil=now+600;break;
            }
            case "white_angel":case "solar_drain":{
                if(!(sun(r,1)||eclipse(r,1)) || !r.ready("white_angel",now,3600))
                    return false;
                r.whiteAngelUntil=now+300;break;
            }
            case "beauty":{
                if(!moon(r,1)||!r.ready(id,now,2400))return false;
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),10))
                    pacify(e,160);
                for(ServerPlayerEntity ally:allies(p,8))
                    effect(ally,StatusEffects.REGENERATION,200,0);
                break;
            }
            case "the_eternal_day":case "the_scarlet_feast":case "the_eclipse":
                return Eclipse.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    public static void stopOnDisconnect(ServerPlayerEntity p) {
        Eclipse.stopOnDisconnect(p);
        speed(p,false);
        String owner="tarot_owner_"+p.getUuidAsString();
        for(UUID id:new java.util.ArrayList<>(REVIVED.keySet())) {
            Revival revive=REVIVED.get(id);
            if(revive!=null && revive.owner.equals(p.getUuid())){
                Entity e=p.getWorld().getEntity(id);
                if(e!=null && e.getScoreboardTags().contains("tarot_revived_life"))
                    e.discard();
                REVIVED.remove(id);
            }
        }
    }
}
