package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.block.BlockState;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttribute;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.projectile.PersistentProjectileEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.tag.TagKey;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.Identifier;
import net.minecraft.util.TypedActionResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Direction;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;

/** Native server handlers for Magician, Strength and the early Impossible Fist kits. */
public final class MagicianStrengthAbilities {
    private MagicianStrengthAbilities() {}
    private static final Random RNG=new Random();
    private static final UUID WALK=UUID.fromString("83d4a799-3e44-4092-80a1-c8d0d4ea131f");
    private static final UUID ARMOR=UUID.fromString("fc385a03-a3ef-4fcb-8d1c-b0ab1e580999");
    private static final UUID KB=UUID.fromString("eaf01490-48cc-40e8-84e8-6fe008b8c04a");
    private static final UUID SWIM=UUID.fromString("a5182e6f-3408-472e-9ad4-8c67ff08230a");
    private static final TagKey<net.minecraft.entity.EntityType<?>> UNDEAD=
        TagKey.of(Registry.ENTITY_TYPE_KEY,new Identifier("tarot","undead"));
    private static final TagKey<net.minecraft.block.Block> STONE=
        TagKey.of(Registry.BLOCK_KEY,new Identifier("tarot","natural_stone"));
    static boolean magician(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("magician",seq);
    }
    static boolean strength(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("strength",seq);
    }
    static boolean fist(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("impossible_fist",seq);
    }
    static boolean strengthIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("strength");
    }
    static boolean magicianIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("magician");
    }
    private static long time(ServerPlayerEntity p){return p.getServer().getOverworld().getTime();}
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect effect,int duration,int level){
        e.addStatusEffect(new StatusEffectInstance(effect,duration,level));
    }
    private static void attribute(ServerPlayerEntity p,EntityAttribute which,UUID key,
                                  String name,double value,boolean enabled){
        EntityAttributeInstance instance=p.getAttributeInstance(which);
        if(instance==null)return;
        EntityAttributeModifier old=instance.getModifier(key);
        if(old!=null)instance.removeModifier(key);
        if(enabled)instance.addTemporaryModifier(
            new EntityAttributeModifier(key,name,value,EntityAttributeModifier.Operation.ADDITION));
    }
    public static void register(){
        UseBlockCallback.EVENT.register((player,world,hand,hit)->{
            if(world.isClient||!(player instanceof ServerPlayerEntity p)||hand!=Hand.MAIN_HAND ||
                !player.isSneaking())return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null || !(magician(r,6)||fist(r,6)))return ActionResult.PASS;
            long t=time(p);
            if(r.recordedStep==null || t>r.recordedStepUntil ||
                !p.getWorld().getRegistryKey().getValue().toString().equals(r.recordedStepDimension)){
                r.recordedStep=hit.getBlockPos();
                r.recordedStepDimension=p.getWorld().getRegistryKey().getValue().toString();
                r.recordedStepUntil=t+1200;
                ArcaneMod.info(p,"Recorded block position for next 1200 ticks.");
                state.markDirty();return ActionResult.SUCCESS;
            }
            if(p.squaredDistanceTo(Vec3d.ofCenter(r.recordedStep))>900)return ActionResult.PASS;
            BlockPos dest=r.recordedStep.up();
            if(!safe(p,dest) || !r.ready("recorded_step",t,1200))return ActionResult.PASS;
            p.requestTeleport(dest.getX()+.5,dest.getY(),dest.getZ()+.5);
            r.recordedStep=null;r.recordedStepDimension="";
            state.markDirty();return ActionResult.SUCCESS;
        });
        UseItemCallback.EVENT.register((player,world,hand)->{
            ItemStack item=player.getStackInHand(hand);
            if(world.isClient||!(player instanceof ServerPlayerEntity p))
                return TypedActionResult.pass(item);
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r!=null && strengthIdentity(r) &&
                (item.isOf(Items.BOW)||item.isOf(Items.CROSSBOW)) &&
                !(strength(r,7)||fist(r,7))) {
                ArcaneMod.error(p,"The Giant Sinks: bows are prohibited until Master's Grip.");
                return TypedActionResult.fail(item);
            }
            return TypedActionResult.pass(item);
        });
        PlayerBlockBreakEvents.AFTER.register((world,player,pos,prior,entity)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p))return;
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null || !magician(r,3) || RNG.nextDouble()>=.1)return;
            BlockPos other=pos.offset(p.getHorizontalFacing().getOpposite());
            if(prior.isOf(world.getBlockState(other).getBlock()))
                p.interactionManager.tryBreakBlock(other);
        });
    }
    private static boolean safe(ServerPlayerEntity p,BlockPos dest){
        return p.getWorld().getBlockState(dest).isAir()
            && p.getWorld().getBlockState(dest.up()).isAir()
            && p.getWorld().getBlockState(dest.down()).getMaterial().isSolid()
            && p.getWorld().getWorldBorder().contains(dest);
    }
    public static float breakSpeed(ServerPlayerEntity p,BlockState target){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null&&target.isIn(STONE) && (strength(r,9)||fist(r,9))?1.35f:1f;
    }
    public static float jumpMultiplier(ServerPlayerEntity p){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && !p.isSubmergedInWater() &&
            (magician(r,9)||fist(r,9))?1.20f:1f;
    }
    public static float incoming(ServerPlayerEntity p,DamageSource source,float amount){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return amount;
        if(source==DamageSource.FALL && (magician(r,9)||fist(r,9)))
            amount*=.30f;
        if(time(p)<r.bulwarkUntil && (strength(r,5)||fist(r,0)))
            amount*=.70f;
        return amount;
    }
    /** Atomic fall-save roll/cooldown, invoked on the native fall-damage path. */
    public static boolean fallSave(ServerPlayerEntity p,DamageSource src){
        if(src!=DamageSource.FALL)return false;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return false;
        double chance=magician(r,8)||fist(r,8)?.30:magician(r,9)?.20:0;
        if(chance==0 || RNG.nextDouble()>=chance)return false;
        long now=time(p);
        if(!r.ready("fall_save_used",now,100))return false;
        BlockPos origin=p.getBlockPos();
        BlockPos choice=origin.offset(p.getHorizontalFacing(),2);
        if(safe(p,choice))p.requestTeleport(choice.getX()+.5,choice.getY(),choice.getZ()+.5);
        if(magician(r,4))for(LivingEntity enemy:HangedAbilities.enemies(p,
            Vec3d.ofCenter(origin),3))effect(enemy,StatusEffects.BLINDNESS,20,0);
        state.markDirty();return true;
    }
    public static float outgoing(ServerPlayerEntity p,LivingEntity victim,DamageSource source,float damage){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !FoolAbilities.enemy(p,victim))return damage;
        boolean melee=source.getSource()==p;
        if(source.getSource() instanceof PersistentProjectileEntity &&
            (strength(r,7)||fist(r,7)))damage*=.75f;
        if(melee){
            boolean unarmed=p.getMainHandStack().isEmpty();
            if(strength(r,9) && !unarmed)damage*=1.18f;
            if((strength(r,8)||fist(r,8)) && unarmed)damage+=2f;
            if(fist(r,4) && unarmed)damage*=1.15f;
            if(strength(r,4) && victim.getType().isIn(UNDEAD))damage*=1.15f;
            if(r.slamUntil>time(p)){
                damage*=fist(r,4)?1.15f:1.10f;
                effect(victim,StatusEffects.SLOWNESS,20,0);
                r.slamUntil=0;
            }
            if(r.divineHitUntil>time(p)){
                damage*=1.50f;r.divineHitUntil=0;
            }
            if(strength(r,2) && r.ready("twilight_blade",time(p),3600)){
                effect(victim,StatusEffects.SLOWNESS,100,1);
                effect(victim,StatusEffects.WEAKNESS,100,0);
            }
        }
        return ImpossibleFist.outgoing(p,victim,source,damage);
    }
    public static void onLand(ServerPlayerEntity p,float distance){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null||distance<3f)return;
        if(strength(r,9))r.slamUntil=time(p)+100;
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        long now=time(p);
        if(magicianIdentity(r) && now%1200==0 && p.getWorld().isSkyVisible(p.getBlockPos()))
            effect(p,StatusEffects.NAUSEA,100,0);
        double walking=(magician(r,9)||fist(r,9))?.12f:0f;
        double resistance=(strength(r,1) && p.getHealth()<8)?1f:
            strength(r,9)?.55f:0f;
        double armor=fist(r,9)?3f:strength(r,9)?2f:0f;
        attribute(p,EntityAttributes.GENERIC_MOVEMENT_SPEED,WALK,
            "Arcane Traveler Speed",walking*.1,walking>0);
        attribute(p,EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE,KB,
            "Arcane Giant Resistance",resistance,resistance>0);
        attribute(p,EntityAttributes.GENERIC_ARMOR,ARMOR,
            "Arcane Giant Frame",armor,armor>0);
        attribute(p,EntityAttributes.GENERIC_MOVEMENT_SPEED,SWIM,
            "The Giant Sinks",-.045,strengthIdentity(r)&&p.isSubmergedInWater());

        if(strength(r,6)||fist(r,6)){
            if(p.isSneaking() && p.isOnGround())r.dawnCrouchTicks+=20;
            else r.dawnCrouchTicks=0;
            if(r.dawnCrouchTicks>=60 && r.ready("dawnlight",now,1200)){
                p.getWorld().spawnParticles(ParticleTypes.END_ROD,p.getX(),p.getY()+1,p.getZ(),
                    32,3,2,3,.015);
                effect(p,StatusEffects.NIGHT_VISION,200,0);
                r.dawnCrouchTicks=0;
            }
        }
        if(now<r.bulwarkUntil && strength(r,5))
            effect(p,StatusEffects.SLOWNESS,40,255);
        ImpossibleFist.tick(p,state,r);
        state.markDirty();
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id){
        long now=time(p);
        switch(id){
            case "star_chart":case "star_chart_grip":{
                if(!(magician(r,7)||fist(r,7))||!p.isSneaking() ||
                    p.getWorld().isDay() || !r.ready(id,now,1200))return false;
                Vec3d dir=p.getRotationVec(1).normalize();
                for(int i=1;i<12;i++)p.getWorld().spawnParticles(ParticleTypes.END_ROD,
                    p.getX()+dir.x*i,p.getY()+1+dir.y*i,p.getZ()+dir.z*i,
                    1,.02,.02,.02,.01);
                ArcaneMod.info(p,"Star Chart visual approximation only: not a confirmed nearest structure.");
                break;
            }
            case "doorstep":case "doorstep_slam":{
                if(!(magician(r,5)||fist(r,5)))return false;
                BlockPos target=safeForward(p,8);
                if(target==null||!r.ready(id,now,300))return false;
                p.requestTeleport(target.getX()+.5,target.getY(),target.getZ()+.5);
                if(fist(r,5))r.slamUntil=now+60;
                break;
            }
            case "planar_step":{
                if(!magician(r,2))return false;
                BlockPos pos=planarExit(p,4);
                if(pos==null||!r.ready(id,now,3600))return false;
                p.requestTeleport(pos.getX()+.5,pos.getY(),pos.getZ()+.5);
                break;
            }
            case "bulwark":{
                if(!strength(r,5) || !r.ready(id,now,2400))return false;
                r.bulwarkUntil=now+100;
                break;
            }
            case "divine_hand":case "divine_door":{
                if(!(strength(r,1)||fist(r,1)))return false;
                LivingEntity enemy=HangedAbilities.enemies(p,p.getPos(),15).stream()
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(enemy==null || !r.ready(id,now,1800))return false;
                Vec3d toward=p.getPos().subtract(enemy.getPos()).normalize().multiply(1.4);
                enemy.addVelocity(toward.x,.25,toward.z);
                effect(enemy,StatusEffects.SLOWNESS,60,255);
                r.divineHitUntil=now+100;
                break;
            }
            case "sealed_slam":{
                if(!fist(r,3))return false;
                LivingEntity enemy=HangedAbilities.enemies(p,p.getPos(),8).stream()
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(enemy==null)return false;
                BlockPos adjacent=enemy.getBlockPos().offset(p.getHorizontalFacing().getOpposite());
                if(!safe(p,adjacent) || !r.ready(id,now,900))return false;
                p.requestTeleport(adjacent.getX()+.5,adjacent.getY(),adjacent.getZ()+.5);
                enemy.damage(DamageSource.MAGIC,4);
                Vec3d knock=enemy.getPos().subtract(p.getPos()).normalize().multiply(3);
                enemy.addVelocity(knock.x,.25,knock.z);
                break;
            }
            case "all_paths_converge":case "the_giants_decay":case "the_impossible_fist":
                return ImpossibleFist.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    private static BlockPos safeForward(ServerPlayerEntity p,int length){
        Vec3d vec=p.getRotationVec(1);
        for(int step=length;step>=1;step--){
            BlockPos candidate=new BlockPos(p.getX()+vec.x*step,p.getY(),p.getZ()+vec.z*step);
            if(safe(p,candidate))return candidate;
        }
        return null;
    }
    private static BlockPos planarExit(ServerPlayerEntity p,int maxSolid){
        Direction dir=p.getHorizontalFacing();
        int solids=0;
        for(int step=1;step<=maxSolid+3;step++){
            BlockPos location=p.getBlockPos().offset(dir,step);
            if(p.getWorld().getBlockState(location).getMaterial().isSolid()){
                solids++;
                if(solids>maxSolid)return null;
            } else if(solids>0 && safe(p,location))return location;
        }
        return null;
    }
}
