package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.UUID;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.mob.VexEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/** Full native event router for Hanged Man and shared Paper Martyr Sin mechanics. */
public final class HangedAbilities {
    private HangedAbilities() {}
    private static final Random RNG = new Random();
    private static final UUID DARK_SPEED=UUID.fromString("f770cb35-12f5-4aae-a2f8-830a2f6454b8");
    private static final UUID BLADE_SPEED=UUID.fromString("d1d49a0b-1bbf-48ab-9691-3f6c9508dffb");
    private static final UUID MANIFEST_SLOW=UUID.fromString("ca853c47-fb9f-4f21-bc38-b632ca1e76bb");
    private static final Map<UUID,List<Hit>> HITS=new HashMap<>();
    private static final Map<UUID,Set<UUID>> TRACKED_TARGETS=new HashMap<>();
    private static final Map<UUID,BlockPos> LAST_POS=new HashMap<>();
    private static final Map<UUID,Manifest> MANIFESTS=new HashMap<>();

    private record Hit(long tick,String type) {}
    private static final class Manifest {
        final long until;
        Manifest(long now) { until=now+1200; }
    }

    static boolean has(ArcaneSave.Record r,int seq) { return r.profile.active("hanged_man",seq); }
    static boolean paper(ArcaneSave.Record r) { return r.profile.active("paper_martyr",9); }
    static boolean sinEnabled(ArcaneSave.Record r) { return has(r,9) || paper(r); }
    static boolean identity(ArcaneSave.Record r) {
        return r.profile.primary().equals("hanged_man") || has(r,9) || paper(r);
    }
    static long now(ServerPlayerEntity p) { return p.getServer().getOverworld().getTime(); }
    public static float naturalRegenLimit(ServerPlayerEntity p) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !identity(r)) return Float.POSITIVE_INFINITY;
        long t=now(p);
        return SinRules.regenLimit(r.killedForRegen,t<r.healingPotionUntil || t<r.darkStillUntil);
    }
    public static boolean blockNaturalHeal(ServerPlayerEntity p,float heal) {
        return p.getHealth() >= naturalRegenLimit(p);
    }
    public static void afterHealingPotion(ServerPlayerEntity p) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=state.getPlayer(p.getUuid());
        if(r==null || !identity(r)) return;
        r.healingPotionUntil=now(p)+1200;
        state.markDirty();
    }
    static float capacity(ServerPlayerEntity p,ArcaneSave.Record r) {
        return SinRules.capacity(paper(r),paper(r) && r.profile.active("paper_martyr",4),
            activeManifest(p) || PaperMartyr.capstoneActive(p));
    }
    static boolean activeManifest(ServerPlayerEntity p) {
        Manifest m=MANIFESTS.get(p.getUuid());
        return m!=null && now(p)<m.until;
    }
    static float reduction(ServerPlayerEntity p,ArcaneSave.Record r) {
        float factor=1f;
        if(has(r,5) && r.sin>0f) factor*=.9f;
        if(activeManifest(p) || FoolLegend.active(p)) factor*=.25f;
        return factor;
    }
    /** Damage remains actual HP; no double scaling through potion resistance. */
    public static float scaleIncoming(LivingEntity victim,float amount) {
        if(!(victim instanceof ServerPlayerEntity p))return amount;
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null) return amount;
        return amount*reduction(p,r);
    }
    public static float scaleOutgoing(LivingEntity victim,DamageSource source,float amount) {
        Entity attacker=source.getAttacker();
        if(!(attacker instanceof ServerPlayerEntity p) || !FoolAbilities.enemy(p,victim)) return amount;
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return amount;
        boolean melee=source.getSource()==attacker;
        float scaled=amount;
        if(melee && has(r,4) && p.getHealth()<12f) scaled*=1.15f;
        if(PaperMartyr.capstoneActive(p) || FoolLegend.active(p)) scaled*=1.5f;
        if(melee && (activeManifest(p) || PaperMartyr.capstoneActive(p))) scaled+=.05f*r.sin;
        return scaled;
    }
    private static void effect(LivingEntity victim,StatusEffect e,int ticks,int level) {
        victim.addStatusEffect(new StatusEffectInstance(e,ticks,level));
    }
    private static void speed(ServerPlayerEntity p,UUID id,String name,double value,boolean enabled) {
        EntityAttributeInstance attr=p.getAttributeInstance(EntityAttributes.GENERIC_MOVEMENT_SPEED);
        if(attr==null)return;
        EntityAttributeModifier old=attr.getModifier(id);
        if(old!=null)attr.removeModifier(id);
        if(enabled)attr.addTemporaryModifier(new EntityAttributeModifier(id,name,value,EntityAttributeModifier.Operation.MULTIPLY_TOTAL));
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long t=now(p);
        int light=p.getWorld().getLightLevel(p.getBlockPos());
        boolean dark=has(r,9) && light<=(has(r,7)?11:7);
        if(dark) effect(p,StatusEffects.RESISTANCE,35,0);
        speed(p,DARK_SPEED,"Tarot: shadow speed",.05,dark);
        speed(p,BLADE_SPEED,"Tarot: dark blade",.10,has(r,4) && p.getHealth()<12f);
        speed(p,MANIFEST_SLOW,"Tarot: manifested burden",-.15,activeManifest(p));

        if(identity(r) && light<=9 && p.isOnGround()) {
            BlockPos position=p.getBlockPos();
            if(position.equals(LAST_POS.get(p.getUuid())))r.darkStillTicks+=20;
            else r.darkStillTicks=0;
            LAST_POS.put(p.getUuid(),position);
            if(r.darkStillTicks>=160)r.darkStillUntil=t+600;
        } else {r.darkStillTicks=0;LAST_POS.remove(p.getUuid());}

        // The spec's Sin expires after 200 ticks without new damage.
        if(sinEnabled(r) && r.sin>0 && t-r.lastSinDamage>=200) {
            r.sin=0f;
            if(has(r,5))effect(p,StatusEffects.REGENERATION,60,0);
        }
        if(!sinEnabled(r) && r.sin>0f)r.sin=0f;
        if(has(r,9) && p.getHealth()<8f && r.sin>0f) burst(p,state,r);
        if(has(r,8)) shadowWhisper(p,t);
        if(activeManifest(p) && t%80==0 && r.sin>0) nova(p,p.getPos(),8,.15f*r.sin);
        Manifest cap=MANIFESTS.get(p.getUuid());
        if(cap!=null && t>=cap.until) {
            MANIFESTS.remove(p.getUuid());
            expireManifest(p,r,state);
        }
        state.markDirty();
    }

    private static void shadowWhisper(ServerPlayerEntity p,long now) {
        Set<UUID> previous=TRACKED_TARGETS.computeIfAbsent(p.getUuid(),k->new HashSet<>());
        Set<UUID> current=new HashSet<>();
        for(MobEntity m:p.getWorld().getEntitiesByClass(MobEntity.class,new Box(p.getBlockPos()).expand(32),
            entity->entity.getTarget()==p && entity.isAlive() && FoolAbilities.enemy(p,entity))) {
            double follow=m.getAttributeValue(EntityAttributes.GENERIC_FOLLOW_RANGE);
            if(m.squaredDistanceTo(p) > follow*follow*.49) {m.setTarget(null);continue;}
            current.add(m.getUuid());
            if(!previous.contains(m.getUuid()) && RNG.nextDouble()<.15)
                effect(p,StatusEffects.RESISTANCE,40,0);
        }
        TRACKED_TARGETS.put(p.getUuid(),current);
    }

    public static void onDamage(ServerPlayerEntity p,DamageSource source,float taken) {
        if(taken<=0)return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=state.getPlayer(p.getUuid());
        if(r==null)return;
        long t=now(p);
        if(sinEnabled(r)) {
            r.sin=SinRules.absorb(r.sin,taken,capacity(p,r),
                activeManifest(p) || PaperMartyr.capstoneActive(p));
            r.lastSinDamage=t;
        }
        if(has(r,6) && RNG.nextDouble()<.20) p.heal(4f);
        if(has(r,3)) recordTrinity(p,source,t);
        Entity attacker=source.getAttacker();
        if(has(r,2) && attacker instanceof LivingEntity e && FoolAbilities.enemy(p,e)
            && RNG.nextDouble()<.10 && r.ready("profane_aura",t,100))
            effect(e,StatusEffects.WEAKNESS,60,0);
        PaperMartyr.onDamage(p,source,taken,state,r);
        if(has(r,9) && p.getHealth()<8f && r.sin>0f)burst(p,state,r);
        state.markDirty();
    }

    private static void recordTrinity(ServerPlayerEntity p,DamageSource src,long t) {
        List<Hit> queue=HITS.computeIfAbsent(p.getUuid(),k->new ArrayList<>());
        queue.removeIf(hit->t-hit.tick>100);
        queue.add(new Hit(t,src.getName()));
        long unique=queue.stream().map(hit->hit.type).distinct().count();
        if(unique>=3) {
            queue.clear();
            effect(p,StatusEffects.RESISTANCE,60,1);
            p.heal(4f);
        }
    }

    private static void burst(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        float sin=r.sin; r.sin=0f;
        boolean overflow=has(r,1);
        nova(p,p.getPos(),overflow?10:8,SinRules.burstDamage(sin));
        for(LivingEntity victim:enemies(p,p.getPos(),overflow?10:8)) {
            effect(victim,StatusEffects.WEAKNESS,overflow?60:80,overflow?1:0);
            if(overflow)effect(victim,StatusEffects.SLOWNESS,60,1);
        }
        p.heal(SinRules.burstHeal(sin,overflow));
        state.markDirty();
    }

    public static void onKill(ServerPlayerEntity p,LivingEntity victim) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=state.getPlayer(p.getUuid());
        if(r==null || !FoolAbilities.enemy(p,victim))return;
        long t=now(p);
        if(identity(r))r.killedForRegen=true;
        if(has(r,9) && r.ready("graze_the_soul",t,120)) {
            p.heal(2f);effect(p,StatusEffects.RESISTANCE,60,0);
        }
        if(has(r,2) && r.ready("profane_kill",t,100)) {
            for(LivingEntity e:enemies(p,victim.getPos(),5))effect(e,StatusEffects.SLOWNESS,40,0);
        }
        if(has(r,1) && RNG.nextDouble()<.20 && r.ready("depraved_dependent",t,2400))
            spawnMinion(p,300,false,0,0);
        if(activeManifest(p) && RNG.nextDouble()<.50)spawnMinion(p,400,false,0,0);
        PaperMartyr.onKill(p,victim,state,r);
        state.markDirty();
    }

    static List<LivingEntity> enemies(ServerPlayerEntity owner,Vec3d center,double radius) {
        Box box=new Box(center.x-radius,center.y-radius,center.z-radius,
            center.x+radius,center.y+radius,center.z+radius);
        return owner.getWorld().getEntitiesByClass(LivingEntity.class,box,
            entity->entity.isAlive() && entity.squaredDistanceTo(center)<=radius*radius
                && FoolAbilities.enemy(owner,entity));
    }
    static void nova(ServerPlayerEntity owner,Vec3d center,double radius,float damage) {
        if(damage<=0f)return;
        for(LivingEntity victim:enemies(owner,center,radius))
            victim.damage(DamageSource.MAGIC,damage);
    }
    static boolean ally(ServerPlayerEntity owner,PlayerEntity target) {
        return owner==target || (owner.getScoreboardTeam()!=null && owner.isTeammate(target));
    }
    static int countMinions(ServerPlayerEntity p) {
        String tag="tarot_owner_"+p.getUuidAsString();
        return p.getWorld().getEntitiesByClass(VexEntity.class,new Box(p.getBlockPos()).expand(128),
             entity->entity.isAlive() && entity.getScoreboardTags().contains(tag)).size();
    }
    static VexEntity spawnMinion(ServerPlayerEntity p,int life,boolean figurine,int damage,int radius) {
        if(countMinions(p)>=2)return null;
        VexEntity vex=EntityType.VEX.create(p.getWorld());
        if(vex==null)return null;
        vex.refreshPositionAndAngles(p.getX()+1,p.getY()+1,p.getZ(),0f,0f);
        EntityAttributeInstance hp=vex.getAttributeInstance(EntityAttributes.GENERIC_MAX_HEALTH);
        if(hp!=null)hp.setBaseValue(4);
        EntityAttributeInstance attack=vex.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE);
        if(attack!=null)attack.setBaseValue(1);
        vex.setHealth(4f); vex.setLifeTicks(life);
        vex.addScoreboardTag("tarot_shadow_minion");
        vex.addScoreboardTag("tarot_owner_"+p.getUuidAsString());
        if(figurine) {
            vex.addScoreboardTag("tarot_martyr_figurine");
            vex.addScoreboardTag("tarot_martyr_blast_"+damage+"_"+radius);
        }
        p.getWorld().spawnEntity(vex);
        return vex;
    }
    public static void onMinionDeath(LivingEntity victim) {
        PaperMartyr.onMinionDeath(victim);
    }

    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String key) {
        if(!"weight_of_sin_made_manifest".equals(key)||!has(r,0))return false;
        long now=now(p);
        if(activeManifest(p) || !r.ready(key,now,14400))return false;
        MANIFESTS.put(p.getUuid(),new Manifest(now));
        state.markDirty();
        return true;
    }
    public static void onPlayerDeath(ServerPlayerEntity p) {
        MANIFESTS.remove(p.getUuid());
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=state.getPlayer(p.getUuid());
        if(r!=null) {r.sin=0f;state.markDirty();}
    }
    public static void stopOnDisconnect(ServerPlayerEntity p) {
        MANIFESTS.remove(p.getUuid());
        HITS.remove(p.getUuid()); LAST_POS.remove(p.getUuid()); TRACKED_TARGETS.remove(p.getUuid());
    }
    private static void expireManifest(ServerPlayerEntity p,ArcaneSave.Record r,ArcaneSave state) {
        float spent=SinRules.explosion(r.sin);
        r.sin=0;
        nova(p,p.getPos(),15,spent);
        float recovery=spent*.5f;
        float missing=Math.max(0f,p.getMaxHealth()-p.getHealth());
        p.heal(Math.min(missing,recovery));
        if(recovery>missing)effect(p,StatusEffects.ABSORPTION,200,1);
        effect(p,StatusEffects.RESISTANCE,300,0);
        state.markDirty();
    }
}
