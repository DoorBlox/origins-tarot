package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.passive.AnimalEntity;
import net.minecraft.entity.passive.VillagerEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Items;
import net.minecraft.item.ItemStack;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/**
 * KubeJS-free World and Justice gameplay, plus their shared low-Sequence mechanics.
 * All server mutations require the matching player's validated Origin and slot.
 * Targeting rule is always hostile tagged mobs OR enemy players, not teammates.
 */
public final class WorldJusticeAbilities {
    private static final Random RNG=new Random();
    private WorldJusticeAbilities() {}

    public static boolean world(ArcaneSave.Record r,int seq) {
        return r!=null && r.originValid && r.profile.active("world",seq);
    }
    public static boolean justice(ArcaneSave.Record r,int seq) {
        return r!=null && r.originValid && r.profile.active("justice",seq);
    }
    public static boolean verdict(ArcaneSave.Record r,int seq) {
        return r!=null && r.originValid && r.profile.active("marked_verdict",seq);
    }
    public static boolean worldIdentity(ArcaneSave.Record r) {
        return r!=null && r.originValid &&
            (r.profile.primary().equals("world") || r.profile.mode().equals("resonance")
                && r.profile.resonance().equals("marked_verdict"));
    }
    public static boolean justiceIdentity(ArcaneSave.Record r) {
        return r!=null && r.originValid &&
            (r.profile.primary().equals("justice") || r.profile.mode().equals("resonance")
                && r.profile.resonance().equals("marked_verdict"));
    }
    public static void register() {
        UseEntityCallback.EVENT.register((player,world,hand,entity,hitResult) -> {
            if(world.isClient || !(player instanceof ServerPlayerEntity owner)
                || hand!=Hand.MAIN_HAND)return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(owner.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(owner);
            if(r==null)return ActionResult.PASS;
            if(entity instanceof VillagerEntity && worldIdentity(r)) {
                ArcaneMod.error(owner,"Terrifying Reputation: this villager refuses to trade.");
                return ActionResult.FAIL;
            }
            if(!(entity instanceof LivingEntity target))return ActionResult.PASS;
            long now=owner.getServer().getOverworld().getTime();
            if(owner.isSneaking() && (justice(r,8)||verdict(r,6)) && entity instanceof PlayerEntity) {
                if(!r.ready("mind_read",now,200))return ActionResult.PASS;
                ArcaneMod.info(owner,"Mind Read: "+target.getName().getString()
                    +" health "+Math.round(target.getHealth())+"/"+Math.round(target.getMaxHealth()));
                state.markDirty();return ActionResult.SUCCESS;
            }
            if(justice(r,7) && FoolAbilities.enemy(owner,target) && r.ready("calm",now,400)) {
                effect(target,StatusEffects.SLOWNESS,60,0);
                state.markDirty();return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
    }
    public static void effect(LivingEntity target,StatusEffect which,int ticks,int level) {
        target.addStatusEffect(new StatusEffectInstance(which,ticks,level));
    }
    public static long now(ServerPlayerEntity p) { return p.getServer().getOverworld().getTime(); }
    private static boolean hasBow(ServerPlayerEntity p) {
        return p.getMainHandStack().isOf(Items.BOW) || p.getOffHandStack().isOf(Items.BOW);
    }
    private static boolean passive(Entity victim) {
        return victim.getType().isIn(net.minecraft.tag.TagKey.of(net.minecraft.util.registry.Registry.ENTITY_TYPE_KEY,
            new net.minecraft.util.Identifier("tarot","passive"))) ||
            victim instanceof VillagerEntity || victim instanceof net.minecraft.entity.passive.TameableEntity;
    }
    private static List<LivingEntity> enemies(ServerPlayerEntity p,double radius) {
        return HangedAbilities.enemies(p,p.getPos(),radius);
    }
    private static ServerPlayerEntity nearestEnemyPlayer(ServerPlayerEntity p,double radius) {
        return p.getWorld().getEntitiesByClass(ServerPlayerEntity.class,new Box(p.getBlockPos()).expand(radius),
            e->e!=p && e.isAlive() && e.squaredDistanceTo(p)<=radius*radius &&
                FoolAbilities.enemy(p,e)).stream().min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
    }
    /** Applies combat modifiers only to an attack from a registered Arcana holder. */
    public static float scaleOutgoing(LivingEntity victim,DamageSource damage,float amount) {
        Entity attacker=damage.getAttacker();
        if(!(attacker instanceof ServerPlayerEntity owner))return amount;
        ArcaneSave.Record r=ArcaneMod.profile(owner);
        if(r==null)return amount;
        boolean mob=!(victim instanceof PlayerEntity);
        float out=amount;
        if(justiceIdentity(r)) {
            float reduction=(justice(r,1)? .20f:.30f);
            if(passive(victim))out*=reduction;
            else if(victim instanceof PlayerEntity && FoolAbilities.enemy(owner,victim)
                && now(owner)>r.provokedUntil)out*=.70f;
        }
        if(world(r,1) && FoolAbilities.enemy(owner,victim) && !passive(victim))
            out*=1.0f; // Cold Precision II is applied to projectile only.
        if(damage.isProjectile()) {
            if(world(r,9) || verdict(r,9))out*=1.25f;
            if(world(r,1))out*=1.04f; // +30% total relative to base (1.25 * 1.04)
            if(world(r,9) || verdict(r,7))out*=1f+Math.min(verdict(r,7)? .30f:.30f,
                r.bowStillTicks * (verdict(r,7)? .05f/30f:.05f/60f));
        }
        return MarkedVerdict.scaleOutgoing(owner,victim,damage,out);
    }
    public static float scaleIncoming(LivingEntity victim,DamageSource source,float amount) {
        if(!(victim instanceof ServerPlayerEntity p))return amount;
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return amount;
        boolean mobAttack=source.getAttacker() instanceof LivingEntity &&
            !(source.getAttacker() instanceof PlayerEntity);
        if(mobAttack && !p.isSprinting() && (justice(r,9)||verdict(r,9)))return amount*.88f;
        return amount;
    }
    public static boolean cancelDamage(LivingEntity victim,DamageSource source) {
        return MarkedVerdict.cancelDamage(victim,source);
    }
    public static boolean rescue(ServerPlayerEntity victim,DamageSource source,float amount) {
        ArcaneSave.Record r=ArcaneMod.profile(victim);
        if(r==null || amount < victim.getHealth()+victim.getAbsorptionAmount())return false;
        long t=now(victim);
        if(world(r,1) && r.ready("hunters_substitution",t,9600)) {
            escape(victim,8);
            victim.setHealth(Math.min(4f,victim.getMaxHealth()));
            effect(victim,StatusEffects.SPEED,60,1);
            ArcaneSave.get(victim.getServer()).markDirty();
            return true;
        }
        if(verdict(r,1) && r.ready("swift_judgment",t,9600)) {
            escape(victim,8);
            victim.setHealth(Math.min(4f,victim.getMaxHealth()));
            if(source.getAttacker() instanceof LivingEntity attacker && FoolAbilities.enemy(victim,attacker))
                effect(attacker,StatusEffects.SLOWNESS,40,255);
            ArcaneSave.get(victim.getServer()).markDirty();
            return true;
        }
        return false;
    }
    private static void escape(ServerPlayerEntity p,int distance) {
        Vec3d look=p.getRotationVec(1).multiply(-distance);
        BlockPos candidate=new BlockPos(p.getX()+look.x,p.getY(),p.getZ()+look.z);
        if(p.getWorld().isAir(candidate) && p.getWorld().isAir(candidate.up())) {
            p.requestTeleport(candidate.getX()+.5,candidate.getY(),candidate.getZ()+.5);
        } else {
            // Validated safe fallback, never teleport into solid blocks.
            p.requestTeleport(p.getX(),p.getY()+1,p.getZ());
        }
    }
    /** Damage interception accounts for already-processed hits, not cancelled hits. */
    public static void onTakenDamage(ServerPlayerEntity p,DamageSource source,float taken) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || taken<=0f)return;
        Entity attacker=source.getAttacker();
        long t=now(p);
        if(attacker instanceof PlayerEntity)r.provokedUntil=t+200;
        if((justice(r,9)||justice(r,4)) && attacker instanceof LivingEntity target &&
            FoolAbilities.enemy(p,target) && r.ready("emotional_recoil",t,360))
            effect(target,StatusEffects.WEAKNESS,justice(r,4)?100:80,0);
        state.markDirty();
    }
    public static void onSuccessfulHit(LivingEntity victim,DamageSource source) {
        if(!(source.getAttacker() instanceof ServerPlayerEntity p))return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !FoolAbilities.enemy(p,victim))return;
        long t=now(p);
        if((world(r,9)||world(r,4)||verdict(r,4)) && r.ready("marked_prey",t,200)) {
            effect(victim,StatusEffects.GLOWING,world(r,4)?160:120,0);
            r.markedEntity=victim.getUuid();r.markedUntil=t+160;
            if(verdict(r,4))effect(victim,StatusEffects.WEAKNESS,120,0);
        }
        MarkedVerdict.onSuccessfulHit(p,victim,source,r);
        state.markDirty();
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity victim) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !FoolAbilities.enemy(p,victim))return;
        long t=now(p);
        if(world(r,9) && r.ready("hunters_tempo",t,360))effect(p,StatusEffects.SPEED,160,0);
        if(verdict(r,2) && r.markedEntity!=null && r.markedEntity.equals(victim.getUuid())) {
            for(LivingEntity target:HangedAbilities.enemies(p,victim.getPos(),8)) {
                effect(target,StatusEffects.SLOWNESS,60,255);
                effect(target,StatusEffects.WEAKNESS,60,255);
                if(target instanceof MobEntity mob) {mob.setTarget(null);mob.getNavigation().stop();}
            }
            effect(p,StatusEffects.ABSORPTION,600,0);
        }
        MarkedVerdict.onKill(p,victim,state,r);
        state.markDirty();
    }
    /** Called per second, on server thread, after identity checks. */
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long t=now(p);
        boolean still=p.getBlockPos().equals(r.lastWorldPosition) && !p.isSprinting();
        if(hasBow(p) && still)r.bowStillTicks=Math.min(360,r.bowStillTicks+20);
        else r.bowStillTicks=0;
        r.lastWorldPosition=p.getBlockPos();

        if(world(r,9) && p.getWorld().getEntitiesByClass(LivingEntity.class,
            new Box(p.getBlockPos()).expand(16),e->FoolAbilities.enemy(p,e)).size()>0 &&
            t%100==0)
            for(LivingEntity enemy:enemies(p,12))effect(enemy,StatusEffects.GLOWING,40,0);

        if(justice(r,9) && r.ready("therapists_presence",t,900))
            for(PlayerEntity ally:p.getWorld().getEntitiesByClass(PlayerEntity.class,
                new Box(p.getBlockPos()).expand(6),e->e.squaredDistanceTo(p)<=36
                    && HangedAbilities.ally(p,e)))
                effect(ally,StatusEffects.REGENERATION,80,0);

        if(justice(r,9)||verdict(r,6)) {
            // APPROX: stopping animal navigation reduces flight but does not remove all panic goals.
            for(AnimalEntity animal:p.getWorld().getEntitiesByClass(AnimalEntity.class,
                new Box(p.getBlockPos()).expand(6),e->e.isAlive() && !e.getType().isIn(
                    net.minecraft.tag.TagKey.of(net.minecraft.util.registry.Registry.ENTITY_TYPE_KEY,
                        new net.minecraft.util.Identifier("tarot","hostile")))))
                if(animal.getAttacker()==null)animal.getNavigation().stop();
        }
        if(justice(r,5)) {
            if(r.wasSleeping && !p.isSleeping()) effect(p,StatusEffects.REGENERATION,200,0);
            r.wasSleeping=p.isSleeping();
        }
        if(justice(r,3) && p.isSneaking() && p.isOnGround()) {
            r.crouchTicks+=20;
            if(r.crouchTicks>=60 && r.ready("shared_dream",t,1200)) {
                for(PlayerEntity ally:p.getWorld().getEntitiesByClass(PlayerEntity.class,
                    new Box(p.getBlockPos()).expand(8),e->e.squaredDistanceTo(p)<=64
                        && HangedAbilities.ally(p,e)))
                    effect(ally,StatusEffects.NIGHT_VISION,200,0);
                r.crouchTicks=0;
            }
        } else r.crouchTicks=0;
        if((verdict(r,7)||verdict(r,3)) && still && hasBow(p))
            for(LivingEntity enemy:enemies(p,6))effect(enemy,StatusEffects.SLOWNESS,40,0);
        if(verdict(r,4) && r.markedEntity!=null && t<r.markedUntil && t%40==0) {
            Entity e=p.getWorld().getEntity(r.markedEntity);
            if(e!=null && FoolAbilities.enemy(p,e))ArcaneMod.info(p,
                "Marked Judgment target at "+e.getBlockPos());
        }
        MarkedVerdict.tick(p,state,r);
        state.markDirty();
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String ability) {
        long t=now(p);
        switch(ability) {
            case "paper_dagger":
            case "paper_sentence": {
                if(!world(r,8)&&!verdict(r,8))return false;
                LivingEntity target=enemies(p,8).stream().min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(target==null)return false;
                int paperSlot=-1;
                for(int slot=0;slot<p.getInventory().size();slot++)
                    if(p.getInventory().getStack(slot).isOf(Items.PAPER)) { paperSlot=slot;break; }
                if(paperSlot<0 || !r.ready(ability,t,200))return false;
                p.getInventory().removeStack(paperSlot,1);
                target.damage(DamageSource.MAGIC,3);
                effect(target,StatusEffects.SLOWNESS,40,0);
                if(verdict(r,8))effect(target,StatusEffects.WEAKNESS,40,0);
                break;
            }
            case "air_cannon": {
                if(!world(r,7) || !r.ready(ability,t,160))return false;
                Vec3d start=p.getEyePos();
                LivingEntity target=HangedAbilities.enemies(p,start.add(p.getRotationVec(1).multiply(7)),7)
                    .stream().filter(e->e.squaredDistanceTo(p)<=196)
                    .min(Comparator.comparingDouble(e->e.getPos().distanceTo(start.add(p.getRotationVec(1).multiply(14)))).orElse(null);
                if(target==null)return false;
                boolean player=target instanceof PlayerEntity;
                target.damage(DamageSource.MAGIC,player?3f:4f);
                Vec3d knock=target.getPos().subtract(p.getPos()).normalize().multiply(player?1.0:2.0);
                target.addVelocity(knock.x,player?.15:.3,knock.z);
                break;
            }
            case "borrowed_face": {
                if(!world(r,6)||r.inCombat(t)||!r.ready(ability,t,2400))return false;
                effect(p,StatusEffects.INVISIBILITY,600,0);
                break;
            }
            case "puppet_string": {
                if(!world(r,5) || !p.isSneaking() || !r.ready(ability,t,400))return false;
                LivingEntity target=enemies(p,8).stream().min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(target==null)return false;
                effect(target,StatusEffects.SLOWNESS,target instanceof PlayerEntity?40:80,1);
                if(target instanceof PlayerEntity)ArcaneMod.info(p,"Puppet String target "+target.getBlockPos());
                else effect(target,StatusEffects.WEAKNESS,80,0);
                break;
            }
            case "small_miracle": {
                // APPROX: Rev2 specifies cooldown only; bounded direct self-heal used.
                if(!world(r,3)||!r.ready(ability,t,9600))return false;
                p.heal(8);effect(p,StatusEffects.REGENERATION,200,0);
                break;
            }
            case "mystery_step": {
                // APPROX: Rev2 specifies cooldown only; safe forward short teleport.
                if(!world(r,2)||!r.ready(ability,t,4800))return false;
                Vec3d step=p.getRotationVec(1).multiply(12);
                BlockPos dest=new BlockPos(p.getX()+step.x,p.getY(),p.getZ()+step.z);
                if(p.getWorld().isAir(dest) && p.getWorld().isAir(dest.up()))
                    p.requestTeleport(dest.getX()+.5,dest.getY(),dest.getZ()+.5);
                break;
            }
            case "suggestion": {
                if(!justice(r,6)||!r.ready(ability,t,600))return false;
                LivingEntity target=enemies(p,6).stream().min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(target==null)return false;
                if(target instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
                else effect(target,StatusEffects.SLOWNESS,100,255);
                break;
            }
            case "discern": {
                if(!justice(r,2)||!r.ready(ability,t,3600))return false;
                ServerPlayerEntity enemy=nearestEnemyPlayer(p,6);if(enemy==null)return false;
                List<String> inventory=new ArrayList<>();
                for(int i=0;i<enemy.getInventory().size();i++){
                    ItemStack item=enemy.getInventory().getStack(i);
                    if(!item.isEmpty())inventory.add(item.getCount()+"x "+item.getName().getString());
                }
                ArcaneMod.info(p,"Discern "+enemy.getName().getString()+" inventory: "+
                    (inventory.isEmpty()?"empty":String.join(", ",inventory)));
                break;
            }
            case "authors_edit": {
                // APPROX: exact chat word editing requires client interception; target debuff/health reveal.
                if(!justice(r,1)||!r.ready(ability,t,2400))return false;
                ServerPlayerEntity enemy=nearestEnemyPlayer(p,20);if(enemy==null)return false;
                effect(enemy,StatusEffects.WEAKNESS,300,0);
                ArcaneMod.info(p,"Author's Edit: "+enemy.getName().getString()
                    +" has "+Math.round(enemy.getHealth())+" HP.");
                break;
            }
            case "the_perfect_prey":
            case "the_mindscape":
            case "the_marked_verdict":
            case "puppets_sentence":
            case "silent_witness":
                return MarkedVerdict.cast(p,state,r,ability);
            default:return false;
        }
        state.markDirty();return true;
    }
    public static boolean canSprint(ServerPlayerEntity p) {return MarkedVerdict.canSprint(p);}
    public static boolean canJump(ServerPlayerEntity p) {return MarkedVerdict.canJump(p);}
    public static void stopOnDisconnect(ServerPlayerEntity p) {MarkedVerdict.stopOnDisconnect(p);}
}
