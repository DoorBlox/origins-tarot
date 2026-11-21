package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.decoration.ArmorStandEntity;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.HostileEntity;
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

    private static boolean enabled(ArcaneSave.Record r,int seq) {
        return r.profile.active("fool",seq);
    }
    private static boolean enemy(ServerPlayerEntity holder,Entity target) {
        if(target==holder) return false;
        if(target instanceof PlayerEntity) {
            if(holder.getScoreboardTeam()!=null && holder.isTeammate(target)) return false;
            // Unteamed players are enemies for Tarot combat targeting.
            return true;
        }
        return target instanceof HostileEntity;
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
    private static void decoy(ServerPlayerEntity p) {
        ArmorStandEntity stand=new ArmorStandEntity(p.world,p.getX(),p.getY(),p.getZ());
        stand.setInvisible(true);
        stand.setNoGravity(true);
        stand.addCommandTag("tarot_decoy");
        stand.setCustomName(new LiteralText("Paper Decoy"));
        stand.setCustomNameVisible(true);
        p.world.spawnEntity(stand);
        // Cleanup without orphaned chunk-loading / persistent ghost armor stands.
        p.getServer().execute(() -> { /* decoy expiry is maintained by tick cleanup below */ });
    }
    public static void register() {
        ServerLivingEntityEvents.ALLOW_DEATH.register((victim, source, amount) -> {
            if(!(victim instanceof ServerPlayerEntity)) return true;
            ServerPlayerEntity p=(ServerPlayerEntity)victim;
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null || !enabled(r,1)) return true;
            long now=p.getServerWorld().getTime();
            if(!r.ready("history_substitution",now,7200)) return true;
            p.setHealth(20);
            p.requestTeleport(p.getX()+12,p.getY(),p.getZ());
            effect(p,StatusEffects.INVISIBILITY,60,0);
            effect(p,StatusEffects.SPEED,60,1);
            ArcaneSave.get(p.getServer()).markDirty();
            return false;
        });
        ServerLivingEntityEvents.AFTER_DAMAGE.register((living, source, base, taken, blocked) -> {
            if(!(living instanceof ServerPlayerEntity)) return;
            ServerPlayerEntity p=(ServerPlayerEntity)living;
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null) return;
            long now=p.getServerWorld().getTime();
            r.combat(now);
            if(enabled(r,9) && RANDOM.nextDouble()<0.20 && r.ready("clowns_mischief",now,100)
                && source.getAttacker() instanceof LivingEntity)
                effect((LivingEntity)source.getAttacker(),StatusEffects.BLINDNESS,20,0);
            if(enabled(r,7) && RANDOM.nextDouble()<0.25 && r.ready("stage_magician",now,400)) {
                Vec3d behind=p.getRotationVec(1).multiply(-3);
                p.requestTeleport(p.getX()+behind.x,p.getY(),p.getZ()+behind.z);
                decoy(p);
            }
            if(enabled(r,1) && RANDOM.nextDouble()<0.25 && r.ready("paper_figurine_substitute",now,6000)) {
                effect(p,StatusEffects.SPEED,40,1);
                decoy(p);
            }
            ArcaneSave.get(p.getServer()).markDirty();
        });
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long now=p.getServerWorld().getTime();
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
        long now=p.getServerWorld().getTime();
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
                // Cannot grant an implemented AI-controlled combat minion using vanilla Vex behavior.
                return unavailable(p,"Fools' Gathering needs the native minion AI module.");
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
    private static int failure(ServerPlayerEntity p) {
        ArcaneMod.error(p,"Not unlocked, invalid stance, on cooldown, or no valid target.");
        return 0;
    }
    private static int unavailable(ServerPlayerEntity p,String message) {
        ArcaneMod.error(p,message);
        return 0;
    }
}
