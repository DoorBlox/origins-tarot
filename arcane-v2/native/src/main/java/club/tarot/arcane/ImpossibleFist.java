package club.tarot.arcane;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.tag.TagKey;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;

/**
 * Time-limited Magician / Strength / Impossible Fist capstones.
 * Phasing is experimental (server-side noClip) and should only be exercised
 * on a backed-up development world. All state is stopped on disconnect.
 */
public final class ImpossibleFist {
    private ImpossibleFist() {}
    private static final TagKey<net.minecraft.block.Block> UNPHASABLE=TagKey.of(
        Registry.BLOCK_KEY,new Identifier("tarot","unphasable"));
    private static final Map<UUID,Active> ACTIVE=new HashMap<>();
    private static final class Active {
        final String ability;
        final ServerWorld dimension;
        final long end;
        final boolean oldNoClip;
        BlockPos lastSafe;
        BlockPos lastSolid;
        int momentum;
        Active(ServerPlayerEntity p,String ability,long until){
            this.ability=ability;
            this.dimension=p.getWorld();
            this.end=until;
            this.oldNoClip=p.noClip;
            this.lastSafe=p.getBlockPos();
        }
        boolean phase(){return ability.equals("all_paths_converge") ||
            ability.equals("the_impossible_fist");}
    }
    private static long time(ServerPlayerEntity p) {
        return p.getServer().getOverworld().getTime();
    }
    private static boolean safe(ServerPlayerEntity p,BlockPos pos) {
        return p.getWorld().getBlockState(pos).isAir() &&
            p.getWorld().getBlockState(pos.up()).isAir() &&
            p.getWorld().getWorldBorder().contains(pos);
    }
    public static void register(){
        // Unlike the other paths this safety check must run EVERY tick while
        // noClip is active, not the 20-tick routine ability scheduler.
        ServerTickEvents.END_SERVER_TICK.register(server-> {
            if(ACTIVE.isEmpty())return;
            for(UUID id:new java.util.ArrayList<>(ACTIVE.keySet())) {
                ServerPlayerEntity owner=server.getPlayerManager().getPlayer(id);
                if(owner==null)continue;
                Active a=ACTIVE.get(id);
                if(a==null)continue;
                if(time(owner)>=a.end || owner.getWorld()!=a.dimension
                    || !owner.isAlive()) {
                    expire(owner,a,owner.isAlive() && owner.getWorld()==a.dimension &&
                        time(owner)>=a.end);
                    ACTIVE.remove(id);continue;
                }
                if(a.phase()) {
                    BlockPos position=owner.getBlockPos();
                    if(owner.getWorld().getBlockState(position).isIn(UNPHASABLE) ||
                        owner.getWorld().getBlockState(position.up()).isIn(UNPHASABLE)) {
                        expire(owner,a,false);ACTIVE.remove(id);continue;
                    }
                    if(safe(owner,position))a.lastSafe=position;
                    else if(!position.equals(a.lastSolid)) {
                        a.lastSolid=position;
                        a.momentum=Math.min(10,a.momentum+1);
                        if(a.ability.equals("the_impossible_fist"))for(LivingEntity victim:
                            HangedAbilities.enemies(owner,owner.getPos(),2))
                            victim.damage(DamageSource.MAGIC,victim.getHealth()*.20f);
                    }
                    owner.noClip=true;
                }
            }
        });
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String ability){
        boolean ok=switch(ability){
            case "all_paths_converge" -> MagicianStrengthAbilities.magician(r,0);
            case "the_giants_decay" -> MagicianStrengthAbilities.strength(r,0);
            case "the_impossible_fist" -> MagicianStrengthAbilities.fist(r,0);
            default -> false;
        };
        if(!ok || active(p))return false;
        long now=time(p);
        int cd=ability.equals("the_giants_decay")?24000:18000;
        if(!r.ready(ability,now,cd))return false;
        int dur=ability.equals("the_giants_decay")?600:900;
        Active a=new Active(p,ability,now+dur);
        ACTIVE.put(p.getUuid(),a);
        if(a.phase())p.noClip=true;
        ArcaneMod.info(p,ability+" active for "+(dur/20)+" seconds (development mechanics).");
        state.markDirty();return true;
    }
    public static boolean active(ServerPlayerEntity p) {
        Active a=ACTIVE.get(p.getUuid());
        return a!=null&&p.getWorld()==a.dimension&&time(p)<a.end;
    }
    public static float outgoing(ServerPlayerEntity player,LivingEntity victim,
                                 DamageSource source,float damage) {
        if(!active(player)||!FoolAbilities.enemy(player,victim))return damage;
        Active a=ACTIVE.get(player.getUuid());
        if(a.ability.equals("the_giants_decay")){
            if(player.squaredDistanceTo(victim)<=225)damage*=1.30f;
        }else if(a.ability.equals("the_impossible_fist")) {
            damage*=1.30f;
            if(source.getSource()==player)damage*=1f+.05f*a.momentum;
        }
        return damage;
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        if(!active(p))return;
        Active a=ACTIVE.get(p.getUuid());
        if(a.ability.equals("all_paths_converge"))return;
        for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),15)) {
            e.addStatusEffect(new StatusEffectInstance(StatusEffects.WITHER,40,1));
            e.addStatusEffect(new StatusEffectInstance(StatusEffects.SLOWNESS,40,1));
            // Target armor reduction requires source-scoped attribute management.
        }
    }
    private static void expire(ServerPlayerEntity p,Active a,boolean normalExpiry){
        p.noClip=a.oldNoClip;
        if(a.phase() && p.getWorld()==a.dimension && !safe(p,p.getBlockPos())){
            BlockPos spot=a.lastSafe;
            if(safe(p,spot))p.requestTeleport(spot.getX()+.5,spot.getY(),spot.getZ()+.5);
        }
        if(normalExpiry && a.ability.equals("the_impossible_fist"))
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),5))
                enemy.damage(DamageSource.MAGIC,Math.max(2f,2f*a.momentum));
    }
    public static void stopOnDisconnect(ServerPlayerEntity player){
        Active a=ACTIVE.remove(player.getUuid());
        if(a!=null)expire(player,a,false);
    }
}
