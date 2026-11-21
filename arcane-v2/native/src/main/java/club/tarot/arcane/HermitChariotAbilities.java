package club.tarot.arcane;

import java.util.Comparator;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.math.BlockPos;

/**
 * Hermit and Chariot native server abilities and the base Burning Archive passives.
 * Each event is server-authorized and checked against a whole Sequence kit.
 */
public final class HermitChariotAbilities {
    private HermitChariotAbilities() {}
    private static final Random RNG=new Random();
    private static final UUID IRON_ARMOR=UUID.fromString("1d150557-770d-4b57-8307-5d27c32d7d0d");
    private static final UUID BATTLE_SPEED=UUID.fromString("3ec27be1-bd4e-4e41-8963-6553d69d99e6");

    static boolean hermit(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("hermit",seq);
    }
    static boolean chariot(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("chariot",seq);
    }
    static boolean archive(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("burning_archive",seq);
    }
    private static long time(ServerPlayerEntity p) {return p.getServer().getOverworld().getTime();}
    private static boolean book(ItemStack stack) {
        return stack.isOf(Items.BOOK)||stack.isOf(Items.WRITABLE_BOOK)
          ||stack.isOf(Items.WRITTEN_BOOK)||stack.isOf(Items.ENCHANTED_BOOK);
    }
    private static boolean study(ServerPlayerEntity p) {
        return book(p.getOffHandStack())||p.getOffHandStack().isOf(Items.CLOCK);
    }
    private static void effect(LivingEntity target,net.minecraft.entity.effect.StatusEffect e,int ticks,int amp) {
        target.addStatusEffect(new StatusEffectInstance(e,ticks,amp));
    }
    private static void modifier(ServerPlayerEntity p,net.minecraft.entity.attribute.EntityAttribute attr,
                                 UUID id,String name,double amount,boolean on) {
        EntityAttributeInstance instance=p.getAttributeInstance(attr);
        if(instance==null)return;
        EntityAttributeModifier old=instance.getModifier(id);
        if(old!=null)instance.removeModifier(id);
        if(on)instance.addTemporaryModifier(new EntityAttributeModifier(id,name,
            amount,EntityAttributeModifier.Operation.ADDITION));
    }
    public static boolean fireImmune(ServerPlayerEntity p,DamageSource source) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && source.isFire() && (chariot(r,9)||archive(r,9));
    }
    public static int modifyXp(ServerPlayerEntity p,int amount) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !(hermit(r,9)||archive(r,9)) || amount<=0)return amount;
        float raw=amount*.35f+r.xpRemainder;
        int bonus=(int)raw;
        r.xpRemainder=raw-bonus;
        state.markDirty();
        return amount+bonus;
    }
    public static float breakMultiplier(ServerPlayerEntity p) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && hermit(r,9) && study(p)?1.2f:1f;
    }
    public static void register() {
        UseEntityCallback.EVENT.register((player,world,hand,entity,hit) -> {
            if(world.isClient || !(player instanceof ServerPlayerEntity p)
                || hand!=Hand.MAIN_HAND || !(entity instanceof LivingEntity victim))return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null || !FoolAbilities.enemy(p,victim))return ActionResult.PASS;
            long now=time(p);
            if(hermit(r,7) && r.ready("hex",now,600)) {
                effect(victim,StatusEffects.WEAKNESS,60,0);
                state.markDirty();return ActionResult.SUCCESS;
            }
            if(chariot(r,8) && p.isSneaking() && r.ready("taunt",now,400)) {
                if(victim instanceof MobEntity mob)mob.setTarget(p);
                else effect(victim,StatusEffects.GLOWING,60,0);
                state.markDirty();return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
        UseBlockCallback.EVENT.register((player,world,hand,hit) -> {
            if(world.isClient || !(player instanceof ServerPlayerEntity p)
                || !p.isSneaking() || hand!=Hand.MAIN_HAND)return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            ItemStack held=p.getMainHandStack();
            if(held.isOf(Items.PAPER) && (hermit(r,6)||archive(r,6))) {
                held.getOrCreateNbt().putInt("TarotRecallX",hit.getBlockPos().getX());
                held.getOrCreateNbt().putInt("TarotRecallY",hit.getBlockPos().getY());
                held.getOrCreateNbt().putInt("TarotRecallZ",hit.getBlockPos().getZ());
                ArcaneMod.info(p,"Scroll coordinates stored on paper.");
                return ActionResult.SUCCESS;
            }
            if(book(held) && archive(r,4)) {
                r.lastBookStudy=time(p);
                state.markDirty();
                ArcaneMod.info(p,"Scholar's Momentum read recorded for 1200 ticks.");
                return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
    }
    public static float outgoing(LivingEntity victim,DamageSource source,float value) {
        if(!(source.getAttacker() instanceof ServerPlayerEntity attacker))return value;
        ArcaneSave.Record r=ArcaneMod.profile(attacker);
        if(r==null||!FoolAbilities.enemy(attacker,victim))return value;
        boolean melee=source.getSource()==attacker;
        if(source.isProjectile() && hermit(r,9))value*=1.2f;
        if(source.isProjectile() && archive(r,1) && time(attacker)<r.libraryUntil)value*=1.5f;
        if(melee && attacker.isSprinting()) {
            if(chariot(r,9)||archive(r,9))value*=1.15f;
            if(archive(r,4) && r.lastBookStudy>0 && time(attacker)-r.lastBookStudy<1200)value*=1.25f;
        }
        if(melee && chariot(r,1) && attacker.isOnFire())value*=1.2f;
        if(melee && r.reapUntil>time(attacker) && (chariot(r,5)||archive(r,5))) {
            value*=1.3f;
            r.reapUntil=0L;
            if(archive(r,5))victim.setOnFireFor(3);
        }
        if(archive(r,2) && melee && r.burnStacks>0 && attacker.fallDistance>0f && !attacker.isOnGround()) {
            value*=1f+Math.min(r.burnStacks,3)*.05f;
            r.burnStacks=0;
        }
        return BurningArchive.outgoing(attacker,victim,source,value);
    }
    public static void onTakenDamage(ServerPlayerEntity player,DamageSource source,float taken) {
        if(taken<=0)return;
        ArcaneSave state=ArcaneSave.get(player.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(player);
        if(r==null)return;
        if((hermit(r,8)||archive(r,8)) && RNG.nextDouble()<.2) {
            effect(player,StatusEffects.RESISTANCE,40,0);
            if(archive(r,8))effect(player,StatusEffects.SPEED,40,0);
        }
        BurningArchive.onTakenDamage(player,source,taken);
        state.markDirty();
    }
    public static void onSuccessfulHit(ServerPlayerEntity p,LivingEntity victim,DamageSource source) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !FoolAbilities.enemy(p,victim))return;
        if(source.getSource()==p && (chariot(r,1)&&p.isOnFire()
            || BurningArchive.combatCap(p)))victim.setOnFireFor(5);
        if(archive(r,1) && time(p)<r.libraryUntil)victim.setOnFireFor(
            source.isProjectile()?3:5);
        BurningArchive.onSuccessfulHit(p,victim,source,r);
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity victim) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !FoolAbilities.enemy(p,victim))return;
        long t=time(p);
        if(chariot(r,9) && r.ready("war_rush",t,360))effect(p,StatusEffects.SPEED,160,0);
        if(chariot(r,6) && RNG.nextDouble()<.2)p.addExperienceLevels(1);
        if(archive(r,6) && RNG.nextDouble()<.2)p.addExperience(1);
        if(chariot(r,3) && r.ready("rally",t,600)) {
            for(PlayerEntity ally:p.getWorld().getEntitiesByClass(PlayerEntity.class,
                new Box(p.getBlockPos()).expand(8),
                player->player.squaredDistanceTo(p)<=64 && HangedAbilities.ally(p,player)))
                effect(ally,StatusEffects.SPEED,100,0);
        }
        if(archive(r,2)) {
            p.addExperience(1);
            if(!BurningArchive.combatCap(p))
                r.burnStacks=Math.min(3,r.burnStacks+1);
        }
        BurningArchive.onKill(p,victim,state,r);
        state.markDirty();
    }

    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long t=time(p);
        if(r.profile.identityActive("hermit") && p.experienceLevel>=30 && !book(p.getOffHandStack()))
            effect(p,StatusEffects.MINING_FATIGUE,40,0);
        if(r.profile.identityActive("chariot") &&
            ((p.getWorld().isRaining() && p.getWorld().isSkyVisible(p.getBlockPos())) || p.isSubmergedInWater())) {
            effect(p,StatusEffects.WEAKNESS,40,0);
            effect(p,StatusEffects.MINING_FATIGUE,40,0);
        }
        if((hermit(r,9)||hermit(r,1)) && p.getWorld().getLightLevel(p.getBlockPos())
            <=(hermit(r,1)?3:7))effect(p,StatusEffects.NIGHT_VISION,220,0);
        if((chariot(r,9)||archive(r,9)) && p.isOnFire())
            effect(p,StatusEffects.STRENGTH,40,0);
        modifier(p,EntityAttributes.GENERIC_ARMOR,IRON_ARMOR,"Tarot Iron Skin",1,
            chariot(r,4) && p.getHealth()<12f);
        modifier(p,EntityAttributes.GENERIC_MOVEMENT_SPEED,BATTLE_SPEED,"Tarot Battle Sprint",
            .02,BurningArchive.combatCap(p));
        if(hermit(r,4) && p.experienceLevel>=30 && book(p.getOffHandStack()))
            effect(p,StatusEffects.LUCK,40,0); // APPROX: Luck is not true +5% enchanting power.
        if(hermit(r,3) && !p.isSprinting()) {
            // Target-acquisition observation is approximated by nearby aggro polling.
            List<MobEntity> mobs=p.getWorld().getEntitiesByClass(MobEntity.class,
                new Box(p.getBlockPos()).expand(16),mob->mob.getTarget()==p);
            if(!mobs.isEmpty() && RNG.nextDouble()<.1)
                effect(p,StatusEffects.SPEED,60,0);
        }
        if((chariot(r,9)||chariot(r,7)||archive(r,7)) && p.isSprinting()) {
            Vec3d behind=p.getPos().subtract(p.getRotationVec(1).multiply(2));
            List<LivingEntity> targets=HangedAbilities.enemies(p,behind,3);
            if(!targets.isEmpty() && r.ready("trail_of_embers",t,300)) {
            for(LivingEntity enemy:targets) {
                enemy.setOnFireFor(2);
                if(archive(r,3)) {
                    enemy.damage(DamageSource.MAGIC,1f);
                    effect(enemy,StatusEffects.SLOWNESS,40,0);
                    ArcaneMod.info(p,"Insightful Flame target HP "+Math.round(enemy.getHealth()));
                }
            }
            p.getWorld().spawnParticles(ParticleTypes.FLAME,behind.x,behind.y+.25,behind.z,
                5,.5,.25,.5,.02);
            }
        }
        if(chariot(r,2) && t<r.stormUntil) {
            p.getWorld().spawnParticles(ParticleTypes.SPLASH,p.getX(),p.getY()+2,p.getZ(),
                15,10,1,10,.05);
            for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),20))
                effect(e,StatusEffects.SLOWNESS,40,0);
        }
        if(archive(r,7) && !p.getWorld().isDay() && t%120==0)
            ArcaneMod.info(p,"Star Chart: "+p.getBlockPos());
        BurningArchive.tick(p,state,r);
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id) {
        long t=time(p);
        switch(id) {
            case "reap":
            case "star_read_reaper": {
                if(!chariot(r,5) && !archive(r,5))return false;
                if(!r.ready("reap",t,600))return false;
                r.reapUntil=t+100;
                if(archive(r,5))showStarRead(p,5);
                break;
            }
            case "star_read": {
                if(!hermit(r,5) || p.getWorld().isDay() || !r.ready(id,t,1200))return false;
                showStarRead(p,15);break;
            }
            case "sages_counsel": {
                if(!hermit(r,2) || !r.ready(id,t,6000))return false;
                // APPROX: Rev2 does not specify how to evaluate arbitrary structure questions.
                ArcaneMod.info(p,"Sage's Counsel: "+(RNG.nextBoolean()?"YES":"NO")
                    +" — a limited oracle omen; not structure detection.");
                effect(p,StatusEffects.LUCK,200,0);break;
            }
            case "emperors_library":
            case "burning_lecture": {
                if(!hermit(r,1) && !archive(r,1) || !r.ready(id,t,3600))return false;
                // APPROX: +50% arrows for 300t, the true item-enchantment transfer needs a safe item overlay.
                r.libraryUntil=t+300;
                ArcaneMod.info(p,"Library open: next 300 ticks arrows deal +50% damage.");break;
            }
            case "storm_call": {
                if(!chariot(r,2) || !r.ready(id,t,6000))return false;
                r.stormUntil=t+600;break;
            }
            case "meteor": {
                if(!chariot(r,1) || !r.ready(id,t,2400))return false;
                Vec3d direction=p.getRotationVec(1).multiply(15);
                BlockPos last=p.getBlockPos();
                for(int i=1;i<=15;i++) {
                    BlockPos spot=new BlockPos(p.getX()+direction.x*i/15,
                        p.getY(),p.getZ()+direction.z*i/15);
                    if(!p.getWorld().isAir(spot) || !p.getWorld().isAir(spot.up()))break;
                    last=spot;
                    for(LivingEntity target:HangedAbilities.enemies(p,
                        new Vec3d(spot.getX()+.5,spot.getY()+.5,spot.getZ()+.5),3))
                        target.setOnFireFor(5);
                }
                p.requestTeleport(last.getX()+.5,last.getY(),last.getZ()+.5);
                r.meteorImmuneUntil=t+5;
                break;
            }
            case "the_battlefield":
            case "the_unseen":
            case "the_burning_archive":
                return BurningArchive.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    private static void showStarRead(ServerPlayerEntity p,int duration) {
        for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),15)) {
            effect(e,StatusEffects.GLOWING,duration*20,0);
            ArcaneMod.info(p,"Star Read "+e.getName().getString()+" "+
                Math.round(e.getHealth())+" / "+Math.round(e.getMaxHealth())+" HP");
        }
    }
}
