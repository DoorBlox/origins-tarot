package club.tarot.arcane;

import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.Random;
import net.minecraft.entity.Entity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.decoration.ArmorStandEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.VexEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.math.BlockPos;

/** Server-owned Paper Martyr resonance: all ten Sequence kits activate at Sequence 1. */
public final class PaperMartyr {
    private PaperMartyr() {}
    private static final Random RNG=new Random();
    private static final Map<UUID,Long> BORROWED=new HashMap<>();

    private static boolean has(ArcaneSave.Record r,int seq) {
        return r.profile.active("paper_martyr",seq);
    }
    static boolean capstoneActive(ServerPlayerEntity p) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && has(r,0) && FoolLegend.active(p);
    }
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect type,int ticks,int amp) {
        e.addStatusEffect(new StatusEffectInstance(type,ticks,amp));
    }
    public static void onDamage(ServerPlayerEntity p,DamageSource source,float taken,ArcaneSave state,ArcaneSave.Record r) {
        if(!has(r,9) || taken<=0f)return;
        long t=HangedAbilities.now(p);
        Entity attacker=source.getAttacker();
        Long until=BORROWED.get(p.getUuid());
        if(until!=null && until>t) {
            BORROWED.remove(p.getUuid());
            if(attacker instanceof LivingEntity victim && FoolAbilities.enemy(p,victim))
                victim.damage(DamageSource.MAGIC,3f);
            p.removeStatusEffect(StatusEffects.INVISIBILITY);
        }
        if(has(r,8) && RNG.nextDouble()<.25 && r.ready("shadow_step",t,400))
            spawnDecoy(p,has(r,4)?2:1,has(r,4)?4:2,2,100,false);
        state.markDirty();
    }

    public static int cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String request) {
        long t=HangedAbilities.now(p);
        switch(request) {
            case "burdened_beginning":
                if(!has(r,9) || !p.isSneaking() || !r.ready(request,t,100))return 0;
                for(LivingEntity e:p.getWorld().getEntitiesByClass(LivingEntity.class,
                    new Box(p.getBlockPos()).expand(10),x->x.isAlive() && p.squaredDistanceTo(x)<=100))
                    effect(e,StatusEffects.GLOWING,100,0);
                break;
            case "suffering_sight":
                if(!has(r,7) || !p.isSneaking())return 0;
                int cost=has(r,3)?3:2;
                List<LivingEntity> nearby=HangedAbilities.enemies(p,p.getPos(),10);
                if(nearby.isEmpty() || r.sin<cost || !r.ready(request,t,200))return 0;
                nearby.sort(Comparator.comparingDouble(p::squaredDistanceTo));
                LivingEntity victim=nearby.get(0);
                r.sin=SinRules.consume(r.sin,cost);
                victim.damage(DamageSource.MAGIC,cost);
                if(has(r,3))effect(victim,StatusEffects.GLOWING,60,0);
                String effectName=victim.getStatusEffects().stream()
                    .filter(x->!x.getEffectType().isBeneficial()).findFirst()
                    .map(x->x.getEffectType().getName().getString()).orElse("none");
                ArcaneMod.info(p,"Suffering Sight: target "+victim.getName().getString()
                    +" / HP "+Math.round(victim.getHealth())+" / debuff "+effectName);
                break;
            case "borrowed_sacrifice":
                if(!has(r,6) || r.inCombat(t) || r.sin<3f || !r.ready(request,t,2400))return 0;
                r.sin=SinRules.consume(r.sin,3f);
                BORROWED.put(p.getUuid(),t+1800);
                effect(p,StatusEffects.INVISIBILITY,1800,0);
                // APPROX: client skin and name replacement requires a client-side renderer.
                break;
            case "gathering_of_martyrs":
                if(!has(r,5) || !r.ready(request,t,6000))return 0;
                boolean stronger=has(r,2);
                for(int i=0;i<2;i++)
                    HangedAbilities.spawnMinion(p,200,true,stronger?6:4,stronger?4:3);
                break;
            case "the_paper_martyr":
                if(!has(r,0) || !FoolLegend.cast(p,state,r))return 0;
                break;
            default: return 0;
        }
        state.markDirty();
        return 1;
    }

    static void spawnDecoy(ServerPlayerEntity owner,int carriedSin,int damage,int radius,int duration,boolean shadow) {
        ArmorStandEntity entity=new ArmorStandEntity(owner.getWorld(),owner.getX(),owner.getY(),owner.getZ());
        entity.setInvisible(true);
        entity.setNoGravity(true);
        entity.setCustomNameVisible(true);
        entity.setCustomName(new net.minecraft.text.LiteralText(shadow?"Sin Shadow":"Paper Martyr Decoy"));
        entity.addScoreboardTag("tarot_decoy");
        entity.addScoreboardTag(shadow?"tarot_shadow_sin":"tarot_paper_decoy");
        entity.addScoreboardTag("tarot_owner_"+owner.getUuidAsString());
        entity.addScoreboardTag("tarot_blast_"+damage+"_"+radius);
        entity.addScoreboardTag("tarot_carried_sin_"+carriedSin);
        owner.getWorld().spawnEntity(entity);
    }
    /** Called from the armor stand damage interception; never damages owner/teammates. */
    public static boolean breakDecoy(Entity e) {
        if(!(e instanceof ArmorStandEntity)
            || (!e.getScoreboardTags().contains("tarot_paper_decoy")
                && !e.getScoreboardTags().contains("tarot_shadow_sin")))return false;
        if(e.getWorld().isClient)return false;
        ServerPlayerEntity owner=owner(e);
        if(owner!=null) {
            int damage=0,radius=0;
            for(String tag:e.getScoreboardTags()) if(tag.startsWith("tarot_blast_")) {
                String[] parts=tag.substring("tarot_blast_".length()).split("_");
                try {damage=Integer.parseInt(parts[0]);radius=Integer.parseInt(parts[1]);}
                catch(NumberFormatException ignored){}
            }
            if(damage>0 && radius>0)HangedAbilities.nova(owner,e.getPos(),radius,damage);
        }
        e.discard();
        return true;
    }
    static ServerPlayerEntity owner(Entity e) {
        if(e.getWorld().getServer()==null)return null;
        for(String tag:e.getScoreboardTags()) if(tag.startsWith("tarot_owner_")) {
            try {
                UUID id=UUID.fromString(tag.substring("tarot_owner_".length()));
                return e.getWorld().getServer().getPlayerManager().getPlayer(id);
            } catch (IllegalArgumentException ignored) { }
        }
        return null;
    }
    static void onMinionDeath(LivingEntity victim) {
        if(!(victim instanceof VexEntity) || !victim.getScoreboardTags().contains("tarot_martyr_figurine"))return;
        ServerPlayerEntity owner=owner(victim);
        if(owner==null)return;
        for(String tag:victim.getScoreboardTags()) if(tag.startsWith("tarot_martyr_blast_")) {
            String[] parts=tag.substring("tarot_martyr_blast_".length()).split("_");
            try {
                HangedAbilities.nova(owner,victim.getPos(),Integer.parseInt(parts[1]),Integer.parseInt(parts[0]));
            } catch(NumberFormatException ignored){}
        }
    }
    /** One rescue, on confirmed lethal damage. Does not heal if no Sequence 1 kit. */
    public static boolean rescue(ServerPlayerEntity p,float damage) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=state.getPlayer(p.getUuid());
        if(r==null || !r.originValid || !has(r,1) || damage<p.getHealth()+p.getAbsorptionAmount())return false;
        long t=HangedAbilities.now(p);
        if(!r.ready("martyrs_substitute",t,7200))return false;
        Vec3d before=p.getPos();
        r.sin=SinRules.absorb(r.sin,3f,HangedAbilities.capacity(p,r),true);
        float blast=Math.min(16f,r.sin);
        spawnDecoy(p,(int)Math.ceil(blast),(int)Math.ceil(blast),10,100,true);
        p.setHealth(20f);
        Vec3d look=p.getRotationVec(1).multiply(-12);
        BlockPos spot=new BlockPos(p.getX()+look.x,p.getY(),p.getZ()+look.z);
        if(p.getWorld().isAir(spot) && p.getWorld().isAir(spot.up()))
            p.requestTeleport(spot.getX()+.5,spot.getY(),spot.getZ()+.5);
        effect(p,StatusEffects.INVISIBILITY,60,0);
        effect(p,StatusEffects.SPEED,60,1);
        state.markDirty();
        return true;
    }

    static void onKill(ServerPlayerEntity p,LivingEntity victim,ArcaneSave state,ArcaneSave.Record r) {
        if(capstoneActive(p))HangedAbilities.spawnMinion(p,400,false,0,0);
    }

    static void capstoneTick(ServerPlayerEntity p,ArcaneSave.Record r,long t) {
        if(!capstoneActive(p))return;
        if(t%80==0 && r.sin>0f)HangedAbilities.nova(p,p.getPos(),8,r.sin*.15f);
    }
    static void capstoneExpire(ServerPlayerEntity p,ArcaneSave.Record r) {
        // Explosion is non-block-destructive; 40 hearts damage cap from stored Sin.
        HangedAbilities.nova(p,p.getPos(),15,SinRules.explosion(r.sin));
        r.sin=0f;
        for(PlayerEntity ally:p.getWorld().getEntitiesByClass(PlayerEntity.class,
             new Box(p.getBlockPos()).expand(10),e->e.squaredDistanceTo(p)<=100
                && HangedAbilities.ally(p,e)))
            effect(ally,StatusEffects.ABSORPTION,200,3);
    }
    static void stopOnDisconnect(ServerPlayerEntity p) { BORROWED.remove(p.getUuid()); }
}
