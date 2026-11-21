package club.tarot.arcane;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.mob.VexEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.Box;

/**
 * Judgement law / Devil descent / fused Binding Contract domains.
 * Contract offers require target's explicit decision; silence never means refuse.
 */
public final class BindingContract {
    private BindingContract(){}
    private static final Random RANDOM=new Random();
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static final Map<UUID,Offer> PENDING=new HashMap<>();
    private static final Map<UUID,WitherMark> WITHER_MARKS=new HashMap<>();
    private enum Decree { NO_SPRINT,NO_JUMP,NO_ATTACK,NO_SPAWN }
    private static final class Active {
        final String name;
        final long until;
        final ServerWorld world;
        Decree decree=Decree.NO_SPRINT;
        Active(ServerPlayerEntity owner,String skill,int ticks){
            this.name=skill;
            this.world=owner.getWorld();
            this.until=time(owner)+ticks;
        }
        boolean law(){return "the_absolute_law".equals(name);}
        boolean contract(){return "the_binding_contract".equals(name);}
        boolean descent(){return "descent".equals(name)||contract();}
    }
    private record Offer(UUID owner,ServerWorld world,long until) {}
    private record WitherMark(UUID owner,ServerWorld world,long until) {}
    private static long time(ServerPlayerEntity p){
        return p.getServer().getOverworld().getTime();
    }
    private static boolean nearby(ServerPlayerEntity owner,Entity subject,double radius){
        return owner.getWorld()==subject.getWorld() &&
            owner.squaredDistanceTo(subject)<=radius*radius;
    }
    private static Active valid(ServerPlayerEntity p){
        Active a=ACTIVE.get(p.getUuid());
        return a!=null && a.world==p.getWorld() && p.isAlive() &&
            time(p)<a.until?a:null;
    }
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect status,
                               int ticks,int level){
        e.addStatusEffect(new StatusEffectInstance(status,ticks,level));
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,
                               ArcaneSave.Record r,String id){
        boolean permitted=switch(id){
            case "descent" -> DevilJudgementAbilities.devil(r,0);
            case "the_absolute_law" -> DevilJudgementAbilities.judgement(r,0);
            case "the_binding_contract" -> DevilJudgementAbilities.contract(r,0);
            default -> false;
        };
        if(!permitted || valid(p)!=null)return false;
        long now=time(p);
        int cd="the_absolute_law".equals(id)?24000:18000;
        if(!r.ready(id,now,cd))return false;
        int duration="the_absolute_law".equals(id)?600:800;
        ACTIVE.put(p.getUuid(),new Active(p,id,duration));
        ArcaneMod.info(p,id+" active for "+duration+" ticks."
            +(id.equals("the_absolute_law")?" Select /tarot decree <type>.":""));
        state.markDirty();
        if(id.equals("the_binding_contract"))
            for(ServerPlayerEntity target:p.getWorld().getPlayers())
                if(target!=p && nearby(p,target,15))
                    offerWithoutCooldown(p,target,now+200);
        return true;
    }
    public static boolean descentActive(ServerPlayerEntity p){
        Active a=valid(p);return a!=null && a.descent();
    }
    public static boolean offer(ServerPlayerEntity owner,ServerPlayerEntity target,
                                ArcaneSave state,ArcaneSave.Record r,long now){
        if(!DevilJudgementAbilities.contract(r,2)||owner==target ||
            !nearby(owner,target,15) || !r.ready("contract_enforcement",now,3600))
            return false;
        offerWithoutCooldown(owner,target,now+200);
        state.markDirty();
        return true;
    }
    private static void offerWithoutCooldown(ServerPlayerEntity owner,ServerPlayerEntity target,
                                             long until){
        if(owner==target)return;
        Offer existing=PENDING.get(target.getUuid());
        if(existing!=null && existing.until>=time(owner))return;
        PENDING.put(target.getUuid(),new Offer(owner.getUuid(),owner.getWorld(),until));
        ArcaneMod.info(target,"Contract from "+owner.getGameProfile().getName()+
            ": use /tarot contract accept or /tarot contract refuse within 10s. Silence has no penalty.");
    }
    public static boolean answer(ServerPlayerEntity target,String decision){
        Offer pending=PENDING.get(target.getUuid());
        long now=time(target);
        if(pending==null || !ContractRules.validOffer(false,true,now,pending.until) ||
            pending.world!=target.getWorld()){
            PENDING.remove(target.getUuid());
            ArcaneMod.error(target,"No pending, valid contract offer.");
            return false;
        }
        PENDING.remove(target.getUuid()); // Prevent duplicate handling on replays.
        ServerPlayerEntity owner=target.getServer().getPlayerManager().getPlayer(pending.owner);
        if(owner==null || !nearby(owner,target,15)){
            ArcaneMod.error(target,"Contract owner is no longer within range.");
            return false;
        }
        if("accept".equals(decision)){
            effect(target,StatusEffects.REGENERATION,200,0);
            effect(target,StatusEffects.RESISTANCE,200,0);
            effect(owner,StatusEffects.REGENERATION,200,0);
            effect(owner,StatusEffects.RESISTANCE,200,0);
            ArcaneMod.info(target,"You accepted. Both parties receive temporary regeneration/resistance.");
            ArcaneMod.info(owner,target.getGameProfile().getName()+" accepted the contract.");
            return true;
        }
        if(ContractRules.penaltyPermitted(decision)){
            effect(target,StatusEffects.WEAKNESS,600,1);
            ItemStack main=target.getMainHandStack();
            if(!main.isEmpty())target.dropItem(main.split(1),true);
            ArcaneMod.info(target,"You explicitly refused; Weakness II 600t and one item dropped.");
            ArcaneMod.info(owner,target.getGameProfile().getName()+" refused the contract.");
            return true;
        }
        ArcaneMod.error(target,"Choose accept or refuse.");return false;
    }
    public static boolean selectDecree(ServerPlayerEntity p,String type){
        Active active=valid(p);
        if(active==null || !active.law()){
            ArcaneMod.error(p,"The Absolute Law must be active.");
            return false;
        }
        try {active.decree=Decree.valueOf(type.toUpperCase(java.util.Locale.ROOT).replace('-','_'));}
        catch(IllegalArgumentException ex){
            ArcaneMod.error(p,"Valid decrees: no_sprint, no_jump, no_attack, no_spawn.");
            return false;
        }
        ArcaneMod.info(p,"Absolute Law decree: "+active.decree+
            (active.decree==Decree.NO_SPAWN?" (spawn suppression approximate)":""));
        return true;
    }
    private static boolean inLaw(ServerPlayerEntity caster,Entity e,Decree decree){
        Active a=valid(caster);
        return a!=null && a.law() && a.decree==decree && nearby(caster,e,30);
    }
    public static boolean maySprint(ServerPlayerEntity target){
        for(ServerPlayerEntity caster:target.getServer().getPlayerManager().getPlayerList()){
            if(inLaw(caster,target,Decree.NO_SPRINT))return false;
            Active a=valid(caster);
            if(a!=null && a.contract() && nearby(caster,target,15) &&
                FoolAbilities.enemy(caster,target))return false;
        }
        return true;
    }
    public static boolean mayJump(ServerPlayerEntity target){
        for(ServerPlayerEntity caster:target.getServer().getPlayerManager().getPlayerList()){
            if(inLaw(caster,target,Decree.NO_JUMP))return false;
            Active a=valid(caster);
            if(a!=null && a.contract() && nearby(caster,target,15) &&
                FoolAbilities.enemy(caster,target))return false;
        }
        return true;
    }
    /** Blocks attacks, not ambient damage, when the selected law is NO_ATTACK. */
    public static boolean preventAttack(LivingEntity target,DamageSource source){
        Entity attacker=source.getAttacker();
        if(attacker==null || !(target.getWorld() instanceof ServerWorld world))return false;
        for(ServerPlayerEntity caster:world.getPlayers()){
            if(inLaw(caster,attacker,Decree.NO_ATTACK) || inLaw(caster,target,Decree.NO_ATTACK))
                return true;
        }
        return false;
    }
    /** Active Chaos Law punishes hostile attackers without reflecting teammates. */
    public static void onAttacked(ServerPlayerEntity owner,LivingEntity offender,
                                  ArcaneSave.Record r,long now){
        if(DevilJudgementAbilities.contract(r,1) && r.chaosStrikeUntil>now &&
            FoolAbilities.enemy(owner,offender)){
            offender.damage(DamageSource.MAGIC,1f);
            effect(offender,StatusEffects.SLOWNESS,60,1);
        }
    }
    public static void onMeleeHit(ServerPlayerEntity owner,LivingEntity victim,
                                  ArcaneSave.Record r,ArcaneSave state){
        Active a=valid(owner);
        if(a==null || !a.descent() || !FoolAbilities.enemy(owner,victim))return;
        if(a.contract()){
            effect(victim,StatusEffects.WITHER,100,1);
            effect(victim,StatusEffects.SLOWNESS,40,0);
            WITHER_MARKS.put(victim.getUuid(),new WitherMark(owner.getUuid(),
                owner.getWorld(),time(owner)+100));
        }else effect(victim,StatusEffects.WITHER,40,0);
        if(r.ready("infernal_lifesteal",time(owner),20))owner.heal(1f);
        state.markDirty();
    }
    private static void spawnMinion(ServerPlayerEntity owner){
        if(HangedAbilities.countMinions(owner)>=4)return;
        VexEntity minion=EntityType.VEX.create(owner.getWorld());
        if(minion==null)return;
        minion.refreshPositionAndAngles(owner.getX()+1,owner.getY()+1,owner.getZ(),0f,0f);
        EntityAttributeInstance hp=minion.getAttributeInstance(EntityAttributes.GENERIC_MAX_HEALTH);
        if(hp!=null)hp.setBaseValue(4);
        EntityAttributeInstance damage=minion.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE);
        if(damage!=null)damage.setBaseValue(1);
        minion.setHealth(4);
        minion.setLifeTicks(600);
        minion.addScoreboardTag("tarot_shadow_minion");
        minion.addScoreboardTag("tarot_owner_"+owner.getUuidAsString());
        minion.addScoreboardTag("tarot_contract_minion");
        owner.getWorld().spawnEntity(minion);
    }
    public static void onKill(ServerPlayerEntity p,LivingEntity killed,
                              ArcaneSave state,ArcaneSave.Record r){
        Active active=valid(p);
        if(active==null || !active.descent() || !FoolAbilities.enemy(p,killed))return;
        if(RANDOM.nextDouble()<.75)spawnMinion(p);
        state.markDirty();
    }
    /** Death without player-tagged damage may still be credited if Wither was applied recently. */
    public static void onAnyDeath(LivingEntity victim,DamageSource source){
        WitherMark mark=WITHER_MARKS.remove(victim.getUuid());
        // Attacker-attributed kills already flow through onKill once. Only
        // unattributed Wither deaths use the recent mark for rescue attribution.
        if(source.getAttacker() instanceof ServerPlayerEntity)return;
        if(mark==null || !(victim.getWorld() instanceof ServerWorld world) ||
            mark.world!=world)return;
        ServerPlayerEntity owner=world.getServer().getPlayerManager().getPlayer(mark.owner);
        if(owner!=null && time(owner)<=mark.until && descentActive(owner) &&
            FoolAbilities.enemy(owner,victim)){
            effect(owner,StatusEffects.ABSORPTION,600,1);
            ArcaneSave state=ArcaneSave.get(owner.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(owner);
            if(r!=null)onKill(owner,victim,state,r);
        }
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        Active a=ACTIVE.get(p.getUuid());
        if(a==null)return;
        long t=time(p);
        if(valid(p)==null){
            ACTIVE.remove(p.getUuid());
            if(a.descent()){
                effect(p,StatusEffects.HUNGER,200,1);
                p.setAbsorptionAmount(0);
            }
            return;
        }
        if(a.descent()){
            effect(p,StatusEffects.STRENGTH,40,1);
            effect(p,StatusEffects.FIRE_RESISTANCE,40,0);
            effect(p,StatusEffects.SPEED,40,0);
        }
        if(a.contract()){
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),15)){
                effect(enemy,StatusEffects.SLOWNESS,40,255);
                effect(enemy,StatusEffects.WITHER,40,1);
                WITHER_MARKS.put(enemy.getUuid(),new WitherMark(p.getUuid(),
                    p.getWorld(),t+40));
            }
        }else if(a.law()) {
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),30)){
                effect(enemy,StatusEffects.SLOWNESS,40,1);
                effect(enemy,StatusEffects.WEAKNESS,40,0);
                if(a.decree==Decree.NO_SPAWN && enemy instanceof MobEntity mob){
                    mob.setTarget(null);mob.getNavigation().stop();
                    // APPROX: blocks aggression, not actual spawn registration.
                }
            }
        }
        if(t%100==0) {
            PENDING.entrySet().removeIf(e->e.getValue().until<t);
            WITHER_MARKS.entrySet().removeIf(e->e.getValue().until<t);
        }
        state.markDirty();
    }
    public static void stopOnDisconnect(ServerPlayerEntity owner){
        // Clean only our own contract minions; never delete ordinary Vexes.
        String ownerTag="tarot_owner_"+owner.getUuidAsString();
        for(VexEntity minion:owner.getWorld().getEntitiesByClass(VexEntity.class,
            new Box(owner.getBlockPos()).expand(256),
            vex->vex.getScoreboardTags().contains("tarot_contract_minion")
                && vex.getScoreboardTags().contains(ownerTag)))minion.discard();
        ACTIVE.remove(owner.getUuid());
        PENDING.entrySet().removeIf(e->e.getValue().owner.equals(owner.getUuid()));
        WITHER_MARKS.entrySet().removeIf(e->e.getValue().owner.equals(owner.getUuid()));
    }
}
