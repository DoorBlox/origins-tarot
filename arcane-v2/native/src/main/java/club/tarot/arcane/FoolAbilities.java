package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.mob.VexEntity;
import java.util.UUID;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.decoration.ArmorStandEntity;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.tag.TagKey;
import net.minecraft.util.Identifier;
import net.minecraft.util.registry.Registry;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.text.LiteralText;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;

/**
 * Server-side KubeJS replacement for Fool's event abilities.
 * Non-implemented visual identity/skin swaps are explicitly approximated.
 */
public final class FoolAbilities {
    private FoolAbilities() { }
    private static final Random RANDOM=new Random();
    private static final TagKey<EntityType<?>> HOSTILE = TagKey.of(Registry.ENTITY_TYPE_KEY,new Identifier("tarot","hostile"));

    private static boolean enabled(ArcaneSave.Record r,int seq) {
        return r.profile.active("fool",seq);
    }
    public static boolean supportsBinding(String key,String ability) {
        if("primary".equals(key)) return "full_faceless_disguise".equals(ability)
            || "legend_of_the_fool".equals(ability);
        if("secondary".equals(key)) return "spirit_vision".equals(ability)
            || "borrowed_face".equals(ability) || "puppet_string".equals(ability)
            || "fools_gathering".equals(ability);
        return false;
    }
    public static boolean enemy(ServerPlayerEntity holder,Entity target) {
        if(target==holder) return false;
        if(target instanceof PlayerEntity) {
            if(holder.getScoreboardTeam()!=null && holder.isTeammate(target)) return false;
            // Unteamed players are enemies for Tarot combat targeting.
            return true;
        }
        return target.getType().isIn(HOSTILE);
    }
    private static List<LivingEntity> enemies(ServerPlayerEntity p,double radius) {
        List<LivingEntity> out=new ArrayList<>();
        for(LivingEntity e : p.world.getEntitiesByClass(LivingEntity.class,
            new Box(p.getBlockPos()).expand(radius), x->x.isAlive())) {
            if(p.squaredDistanceTo(e)<=radius*radius && enemy(p,e)) out.add(e);
        }
        return out;
    }
    private static void effect(LivingEntity living,net.minecraft.entity.effect.StatusEffect e,int duration,int amplifier) {
        living.addStatusEffect(new StatusEffectInstance(e,duration,amplifier));
    }
    static void decoy(ServerPlayerEntity p) {
        ArmorStandEntity stand=new ArmorStandEntity(p.world,p.getX(),p.getY(),p.getZ());
        stand.setInvisible(true);
        stand.setNoGravity(true);
        stand.addScoreboardTag("tarot_decoy");
        stand.setCustomName(new LiteralText("Paper Decoy"));
        stand.setCustomNameVisible(true);
        p.world.spawnEntity(stand);
        // The native server tick discards decoys once they are 100 ticks old.
    }
    public static void register() {
        // LivingEntityMixin installs the native 1.18.2 damage hooks.
        // Fabric API 0.76.0 on 1.18.2 does not contain ServerLivingEntityEvents.
    }

    /**
     * Head-of-damage interception. APPROX: raw incoming damage is checked before
     * vanilla armor/protection processing, which may trigger rescue early.
     */
    public static boolean rescueIfLethal(ServerPlayerEntity p, DamageSource source, float damage) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !enabled(r,1) || damage < p.getHealth()+p.getAbsorptionAmount()) return false;
        long now=p.getWorld().getTime();
        if(!r.ready("history_substitution",now,7200)) return false;
        p.setHealth(20);
        p.requestTeleport(p.getX()+12,p.getY(),p.getZ());
        effect(p,StatusEffects.INVISIBILITY,60,0);
        effect(p,StatusEffects.SPEED,60,1);
        ArcaneSave.get(p.getServer()).markDirty();
        return true;
    }

    public static void afterDamage(ServerPlayerEntity p, DamageSource source) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null) return;
        long now=p.getWorld().getTime();
        r.combat(now);
        Entity attacker=source.getAttacker();
        if(enabled(r,9) && attacker instanceof LivingEntity && enemy(p,attacker)
            && RANDOM.nextDouble()<0.20 && r.ready("clowns_mischief",now,100))
            effect((LivingEntity)attacker,StatusEffects.BLINDNESS,20,0);
        if(enabled(r,7) && RANDOM.nextDouble()<0.25 && r.ready("stage_magician",now,400)) {
            Vec3d behind=p.getRotationVec(1).multiply(-3);
            p.requestTeleport(p.getX()+behind.x,p.getY(),p.getZ()+behind.z);
            decoy(p);
        }
        if(enabled(r,1) && attacker instanceof LivingEntity && enemy(p,attacker)
            && RANDOM.nextDouble()<0.25 && r.ready("paper_figurine_substitute",now,6000)) {
            effect(p,StatusEffects.SPEED,40,1);
            decoy(p);
        }
        ArcaneSave.get(p.getServer()).markDirty();
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long now=p.getWorld().getTime();
        FoolLegend.tick(p);
        for (ArmorStandEntity decoy : p.getWorld().getEntitiesByClass(ArmorStandEntity.class,
            new Box(p.getBlockPos()).expand(128), e -> e.age >= 100
                && e.getScoreboardTags().contains("tarot_decoy"))) decoy.discard();
        if(enabled(r,8)) {
            // APPROX: poll mob targets every 20 ticks. Players have no MobEntity AI target.
            List<MobEntity> targeting=p.getWorld().getEntitiesByClass(MobEntity.class,
                new Box(p.getBlockPos()).expand(24),
                mob -> mob.getTarget()==p && mob.getType().isIn(HOSTILE));
            for(MobEntity mob:targeting) {
                if(RANDOM.nextDouble()>=0.10 || !r.ready("tricksters_favor",now,200)) continue;
                List<LivingEntity> alternate=p.getWorld().getEntitiesByClass(LivingEntity.class,
                    new Box(mob.getBlockPos()).expand(6),
                    e -> e!=mob && e!=p && e.isAlive() && enemy(p,e));
                alternate.sort(Comparator.comparingDouble(mob::squaredDistanceTo));
                if(!alternate.isEmpty()) {
                    mob.setTarget(alternate.get(0));
                    state.markDirty();
                    break;
                }
            }
        }
        // Allied Vex-like minions: bound to owner and targeting hostile mobs AND enemy players.
        for(VexEntity vex : p.getWorld().getEntitiesByClass(VexEntity.class,
            new Box(p.getBlockPos()).expand(64), e -> e.getScoreboardTags().contains("tarot_shadow_minion")
            && e.getScoreboardTags().contains("tarot_owner_"+p.getUuidAsString()))) {
            List<LivingEntity> eligible = enemies(p,24);
            eligible.sort(Comparator.comparingDouble(vex::squaredDistanceTo));
            if(!eligible.isEmpty()) vex.setTarget(eligible.get(0));
            else vex.setTarget(null);
        }
        if(enabled(r,9) && now%40==0) {
            int mobs=0; boolean playerEnemy=false;
            for(LivingEntity e:enemies(p,8)) {
                if(e instanceof PlayerEntity) playerEnemy=true; else mobs++;
            }
            if(mobs>=3 || playerEnemy) effect(p,StatusEffects.NAUSEA,100,0);
        }
        if(enabled(r,4) && p.getHealth()<8
            && r.ready("tricksters_escape",now,600)) {
            effect(p,StatusEffects.SPEED,60,1);
            decoy(p);
            state.markDirty();
        }
    }
    public static int cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String requested) {
        String id=requested.toLowerCase(java.util.Locale.ROOT);
        long now=p.getWorld().getTime();
        switch(id) {
            case "spirit_vision":
                if(!enabled(r,9) || !p.isSneaking()) return failure(p);
                if(!r.ready(id,now,100)) return failure(p);
                for(Entity e:p.world.getOtherEntities(p,new Box(p.getBlockPos()).expand(10),
                    e->e.squaredDistanceTo(p)<=100)) if(e instanceof LivingEntity)
                    effect((LivingEntity)e,StatusEffects.GLOWING,40,0);
                effect(p,StatusEffects.GLOWING,40,0);
                break;
            case "puppet_string":
                if(!enabled(r,5) || !p.isSneaking()) return failure(p);
                List<LivingEntity> targets=enemies(p,8);
                if(targets.isEmpty() || !r.ready(id,now,400)) return failure(p);
                targets.sort(Comparator.comparingDouble(p::squaredDistanceTo));
                LivingEntity target=targets.get(0);
                effect(target,StatusEffects.SLOWNESS,target instanceof PlayerEntity?40:80,1);
                if(target instanceof PlayerEntity) {
                    ArcaneMod.info(p,"Puppet target at "+target.getBlockPos());
                    // Approx: Slowness cannot completely forbid sprint; server-side speed clamp needed.
                } else effect(target,StatusEffects.WEAKNESS,100,0);
                break;
            case "fools_gathering":
                if(!enabled(r,2) || !r.ready(id,now,6000)) return failure(p);
                for(int i=0;i<2;i++) {
                    VexEntity vex=EntityType.VEX.create(p.getWorld());
                    if(vex==null) continue;
                    vex.refreshPositionAndAngles(p.getX()+(i==0?-1:1),p.getY()+1,p.getZ(),0f,0f);
                    vex.getAttributeInstance(EntityAttributes.GENERIC_MAX_HEALTH).setBaseValue(4.0D);
                    vex.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE).setBaseValue(1.0D);
                    vex.setHealth(4.0f);
                    vex.setLifeTicks(200);
                    vex.addScoreboardTag("tarot_shadow_minion");
                    vex.addScoreboardTag("tarot_owner_"+p.getUuidAsString());
                    p.getWorld().spawnEntity(vex);
                }
                break;
            case "legend_of_the_fool":
                if(!FoolLegend.cast(p,state,r)) return failure(p);
                break;
            case "full_faceless_disguise":
                if(!enabled(r,9) || r.inCombat(now) || !r.ready(id,now,6000)) return failure(p);
                // APPROX: server-only invisibility. Actual player skin/model/name override requires client integration.
                effect(p,StatusEffects.INVISIBILITY,2400,0);
                break;
            case "borrowed_face":
                if(!enabled(r,6) || r.inCombat(now) || !r.ready(id,now,2400)) return failure(p);
                // APPROX: no genuine name/profile swap without client integration.
                effect(p,StatusEffects.INVISIBILITY,1800,0);
                break;
            default: return unavailable(p,"No native handler registered for "+id);
        }
        state.markDirty();
        ArcaneMod.info(p,"Cast "+id+".");
        return 1;
    }
    /** A player/teammate cannot be injured by the Fool's own tagged Vex-like minion. */
    public static boolean cancelFriendlyMinionHit(LivingEntity victim,DamageSource source) {
        if(!(source.getAttacker() instanceof VexEntity)
            || !(victim instanceof ServerPlayerEntity)) return false;
        VexEntity vex=(VexEntity)source.getAttacker();
        if(!vex.getScoreboardTags().contains("tarot_shadow_minion")) return false;
        ServerPlayerEntity target=(ServerPlayerEntity)victim;
        for(String tag:vex.getScoreboardTags()) {
            if(!tag.startsWith("tarot_owner_")) continue;
            try {
                UUID ownerId=UUID.fromString(tag.substring("tarot_owner_".length()));
                if(ownerId.equals(target.getUuid())) return true;
                ServerPlayerEntity owner=target.getServer().getPlayerManager().getPlayer(ownerId);
                if(owner!=null && owner.getScoreboardTeam()!=null && owner.isTeammate(target)) return true;
            } catch(IllegalArgumentException ignored) { }
        }
        return false;
    }
    private static int failure(ServerPlayerEntity p) {
        ArcaneMod.error(p,"Not unlocked, invalid stance, on cooldown, or no valid target.");
        return 0;
    }
    private static int unavailable(ServerPlayerEntity p,String message) {
        ArcaneMod.error(p,message);
        return 0;
    }
}
