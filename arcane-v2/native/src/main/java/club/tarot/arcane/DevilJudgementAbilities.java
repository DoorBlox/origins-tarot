package club.tarot.arcane;

import java.util.Comparator;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
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
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.potion.PotionUtil;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.TypedActionResult;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/** KubeJS-free Devil/Judgement ability handlers; only equipped kits may act. */
public final class DevilJudgementAbilities {
    private DevilJudgementAbilities(){}
    private static final Random RNG=new Random();
    private static final UUID ARMOR=UUID.fromString("ed46eceb-22bc-4f2b-9ad4-86f47a615b11");
    private static final UUID KB=UUID.fromString("ed46eceb-22bc-4f2b-9ad4-86f47a615b12");
    static boolean devil(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("devil",seq);
    }
    static boolean judgement(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("judgement",seq);
    }
    static boolean contract(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("binding_contract",seq);
    }
    static boolean devilIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("devil");
    }
    static boolean judgementIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("judgement");
    }
    private static long time(ServerPlayerEntity p){return p.getServer().getOverworld().getTime();}
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect status,
                               int ticks,int amp){
        e.addStatusEffect(new StatusEffectInstance(status,ticks,amp));
    }
    private static boolean enemy(ServerPlayerEntity owner,Entity target){
        return target instanceof LivingEntity && FoolAbilities.enemy(owner,target);
    }
    public static void register(){
        UseItemCallback.EVENT.register((player,world,hand)->{
            ItemStack stack=player.getStackInHand(hand);
            if(world.isClient || !(player instanceof ServerPlayerEntity p))
                return TypedActionResult.pass(stack);
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return TypedActionResult.pass(stack);
            if(devilIdentity(r) && (stack.isOf(Items.GOLDEN_APPLE) ||
                stack.isOf(Items.ENCHANTED_GOLDEN_APPLE))){
                ArcaneMod.error(p,"Sacred Rejection: golden apples cannot be consumed.");
                return TypedActionResult.fail(stack);
            }
            if(judgementIdentity(r) && (stack.isOf(Items.ENDER_PEARL) ||
                stack.isOf(Items.CHORUS_FRUIT))){
                ArcaneMod.error(p,"No Unlawful Escape: that teleport item is forbidden.");
                return TypedActionResult.fail(stack);
            }
            if(devilIdentity(r) && stack.isOf(Items.POTION) &&
                PotionUtil.getPotionEffects(stack).stream().anyMatch(x->
                    x.getEffectType()==StatusEffects.INSTANT_HEALTH)){
                // APPROX: this flag covers self-drinking; thrown/splash potions
                // and other healing within this window require event-level source IDs.
                r.sacredPotionUntil=time(p)+60;
                ArcaneSave.get(p.getServer()).markDirty();
            }
            return TypedActionResult.pass(stack);
        });
        UseEntityCallback.EVENT.register((player,world,hand,target,hit)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p) ||
                hand!=Hand.MAIN_HAND || !(target instanceof LivingEntity victim))
                return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            long now=time(p);
            boolean handled=false;
            if(victim instanceof ServerPlayerEntity other && other!=p &&
                judgement(r,8) && !p.isSneaking()){
                r.posseTarget=other.getUuid();r.posseUntil=now+1200;
                ArcaneMod.info(p,"Posse tracking target "+other.getGameProfile().getName()+" for 1200t.");
                handled=true;
            }
            if(victim instanceof ServerPlayerEntity other && p.isSneaking() &&
                (devil(r,5)||contract(r,5)) && r.ready("desire",now,200)){
                ArcaneMod.info(p,"Desire: "+other.getGameProfile().getName()+" holds "+
                    other.getMainHandStack().getName().getString()+".");
                if(contract(r,5) && enemy(p,other))
                    effect(other,StatusEffects.SLOWNESS,60,1);
                handled=true;
            }
            if(p.isSneaking() && enemy(p,victim) &&
                (judgement(r,7)||contract(r,8)) && r.ready("question",now,400)){
                effect(victim,StatusEffects.WEAKNESS,60,0);handled=true;
            }
            if(enemy(p,victim) && (devil(r,6)||contract(r,6))
                && r.ready("devils_mark",now,400)){
                effect(victim,StatusEffects.WITHER,40,0);handled=true;
            }
            if(enemy(p,victim) && contract(r,7) &&
                r.ready("predators_calm",now,400)){
                effect(victim,StatusEffects.SLOWNESS,60,0);handled=true;
            }
            if(target instanceof ServerPlayerEntity other && other!=p
                && contract(r,2) && !p.isSneaking()){
                if(BindingContract.offer(p,other,state,r,now))handled=true;
            }
            if(handled){state.markDirty();return ActionResult.SUCCESS;}
            return ActionResult.PASS;
        });
    }
    public static boolean fireImmune(ServerPlayerEntity player,DamageSource src){
        ArcaneSave.Record r=ArcaneMod.profile(player);
        return r!=null && src.isFire() && (devil(r,9)||contract(r,9));
    }
    public static float healingMultiplier(ServerPlayerEntity p,float healed){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && devilIdentity(r) && time(p)<r.sacredPotionUntil
            ?healed*.5f:healed;
    }
    public static float incoming(ServerPlayerEntity victim,DamageSource source,float damage){
        ArcaneSave.Record r=ArcaneMod.profile(victim);
        if(r==null)return damage;
        if(!victim.isSprinting() && source.getAttacker() instanceof LivingEntity
            && source.getSource()==source.getAttacker()){
            if(judgement(r,4))damage*=.82f;
            else if(judgement(r,9))damage*=.88f;
        }
        if(BindingContract.descentActive(victim))damage*=1.15f;
        return damage;
    }
    public static float outgoing(ServerPlayerEntity attacker,LivingEntity victim,
                                 DamageSource source,float damage){
        ArcaneSave.Record r=ArcaneMod.profile(attacker);
        if(r==null || !enemy(attacker,victim))return damage;
        boolean melee=source.getSource()==attacker;
        if(melee){
            double threshold=devil(r,4)?.5:.4;
            if(devil(r,9) && attacker.getHealth()/attacker.getMaxHealth()<threshold)
                damage*=1.18f;
            if(judgement(r,3) && victim instanceof MobEntity mob &&
                mob.getTarget() instanceof PlayerEntity target && target!=attacker)
                damage*=1.10f;
            if(r.chaosStrikeUntil>time(attacker) &&
                (devil(r,1)||contract(r,1))){
                damage*=1.50f;
                r.chaosStrikeUntil=0;
                effect(victim,StatusEffects.WITHER,100,1);
            }
            if(r.disciplineUntil>time(attacker) &&
                (judgement(r,5)||contract(r,5))){
                effect(victim,StatusEffects.SLOWNESS,20,255);
                r.disciplineUntil=0;
            }
            if(r.orderStrikeUntil>time(attacker) && judgement(r,1)){
                effect(victim,StatusEffects.SLOWNESS,40,255);
                r.orderStrikeUntil=0;
            }
        }
        return damage;
    }
    public static void onSuccessfulHit(ServerPlayerEntity caster,LivingEntity victim,
                                       DamageSource source){
        ArcaneSave state=ArcaneSave.get(caster.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(caster);
        if(r==null || !enemy(caster,victim))return;
        long now=time(caster);
        if(source.getSource()==caster && (devil(r,9)||contract(r,4))
            && r.ready("corrupting_claws",now,320)){
            effect(victim,StatusEffects.WITHER,40,0);
            if(contract(r,4)){
                effect(victim,StatusEffects.SLOWNESS,40,0);
                effect(victim,StatusEffects.GLOWING,80,0);
            }
        }
        if(source.getSource()==caster && BindingContract.descentActive(caster))
            BindingContract.onMeleeHit(caster,victim,r,state);
        state.markDirty();
    }
    public static void onTakenDamage(ServerPlayerEntity p,DamageSource src,float amount){
        if(amount<=0)return;
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        long now=time(p);
        Entity attacker=src.getAttacker();
        if(attacker instanceof LivingEntity enemy && enemy(p,enemy)){
            if((judgement(r,9)||contract(r,9)) &&
                r.ready("retaliatory_sentence",now,280))
                effect(enemy,StatusEffects.SLOWNESS,60,0);
            if(contract(r,3)){
                enemy.damage(DamageSource.MAGIC,2f);
                effect(enemy,StatusEffects.SLOWNESS,40,1);
                if(p.getHealth()/p.getMaxHealth()<.5f)
                    effect(enemy,StatusEffects.WITHER,60,0);
            }
            BindingContract.onAttacked(p,enemy,r,now);
        }
        if((devil(r,8)||contract(r,8)) && RNG.nextDouble()<.1)
            effect(p,StatusEffects.STRENGTH,40,0);
        state.markDirty();
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity victim){
        if(!enemy(p,victim))return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        long now=time(p);
        if(devil(r,7)||contract(r,7))effect(p,StatusEffects.SPEED,60,0);
        if(judgement(r,9) && RNG.nextDouble()<.10)
            for(LivingEntity mob:HangedAbilities.enemies(p,victim.getPos(),4)){
                if(mob instanceof MobEntity hostile){hostile.setTarget(null);}
                effect(mob,StatusEffects.SLOWNESS,40,0);
            }
        if((judgement(r,6)||contract(r,6)) &&
            r.ready("verdict",now,400))
            for(LivingEntity e:HangedAbilities.enemies(p,victim.getPos(),4))
                effect(e,StatusEffects.SLOWNESS,40,0);
        BindingContract.onKill(p,victim,state,r);
        state.markDirty();
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        long now=time(p);
        double armor=(judgement(r,9)||contract(r,9))?2:0;
        EntityAttributeInstance a=p.getAttributeInstance(EntityAttributes.GENERIC_ARMOR);
        if(a!=null){
            if(a.getModifier(ARMOR)!=null)a.removeModifier(ARMOR);
            if(armor>0)a.addTemporaryModifier(new EntityAttributeModifier(ARMOR,
                "Law's Weight",armor,EntityAttributeModifier.Operation.ADDITION));
        }
        double kb=judgement(r,1)?.60:(judgement(r,9)||contract(r,9))?.45:0;
        EntityAttributeInstance resist=p.getAttributeInstance(EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE);
        if(resist!=null){
            if(resist.getModifier(KB)!=null)resist.removeModifier(KB);
            if(kb>0)resist.addTemporaryModifier(new EntityAttributeModifier(KB,
                "Law's Stance",kb,EntityAttributeModifier.Operation.ADDITION));
        }
        if((devil(r,9)||contract(r,9)) && p.isOnFire() &&
            r.ready("infernal_vitality",now,devil(r,1)?60:80))
            p.heal(1f);
        if(judgement(r,8) && r.posseTarget!=null && now<r.posseUntil && now%100==0){
            ServerPlayerEntity target=p.getServer().getPlayerManager().getPlayer(r.posseTarget);
            if(target!=null && target.getWorld()==p.getWorld()){
                Vec3d d=target.getPos().subtract(p.getPos());
                ArcaneMod.info(p,"Posse target "+target.getGameProfile().getName()+
                    ": dx="+Math.round(d.x)+", dz="+Math.round(d.z)+
                    ", distance="+Math.round(d.length())+" blocks.");
            }
        }
        if((devil(r,3)) && now%100==0 && RNG.nextDouble()<.10)
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),5)){
                if(enemy instanceof MobEntity mob){
                    LivingEntity alternative=HangedAbilities.enemies(p,enemy.getPos(),5)
                        .stream().filter(x->x!=enemy).findFirst().orElse(null);
                    if(alternative!=null)mob.setTarget(alternative);
                }else effect(enemy,StatusEffects.NAUSEA,40,0);
            }
        BindingContract.tick(p,state,r);
        state.markDirty();
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,
                               ArcaneSave.Record r,String id){
        long now=time(p);
        switch(id){
            case "blood_price":{
                if(!devil(r,2)||p.getHealth()<=4 || !r.ready(id,now,3600))return false;
                p.setHealth(p.getHealth()-4f);
                effect(p,StatusEffects.STRENGTH,200,1);
                break;
            }
            case "discipline":case "desires_discipline":{
                if(!(judgement(r,5)||contract(r,5)) || !r.ready("discipline",now,600))return false;
                r.disciplineUntil=now+100;break;
            }
            case "balance":{
                if(!judgement(r,2))return false;
                LivingEntity target=HangedAbilities.enemies(p,p.getPos(),6).stream()
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(target==null || !r.ready("balance",now,3600))return false;
                float average=(p.getHealth()+target.getHealth())/2f;
                p.setHealth(Math.min(p.getMaxHealth(),average));
                target.setHealth(Math.min(target.getMaxHealth(),average));
                break;
            }
            case "chaos_unleashed":case "chaos_law":{
                if(!(devil(r,1)||contract(r,1)) || !r.ready("chaos",now,1800))
                    return false;
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),10)){
                    effect(e,StatusEffects.SLOWNESS,160,1);
                    effect(e,StatusEffects.WEAKNESS,160,0);
                }
                r.chaosStrikeUntil=now+160;
                break;
            }
            case "order":{
                if(!judgement(r,1)||!r.ready("order",now,1800))return false;
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),8)){
                    effect(e,StatusEffects.SLOWNESS,160,1);
                    effect(e,StatusEffects.WEAKNESS,160,1);
                }
                r.orderStrikeUntil=now+160;
                break;
            }
            case "descent":case "the_absolute_law":case "the_binding_contract":
                return BindingContract.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    public static void stopOnDisconnect(ServerPlayerEntity p){
        BindingContract.stopOnDisconnect(p);
        EntityAttributeInstance armor=p.getAttributeInstance(EntityAttributes.GENERIC_ARMOR);
        if(armor!=null && armor.getModifier(ARMOR)!=null)armor.removeModifier(ARMOR);
        EntityAttributeInstance kb=p.getAttributeInstance(EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE);
        if(kb!=null && kb.getModifier(KB)!=null)kb.removeModifier(KB);
    }
}
