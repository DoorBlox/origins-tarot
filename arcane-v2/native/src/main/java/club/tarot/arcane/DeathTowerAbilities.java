package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;
import java.util.UUID;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.block.BlockState;
import net.minecraft.block.Blocks;
import net.minecraft.block.NetherPortalBlock;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.mob.VexEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Items;
import net.minecraft.item.ItemStack;
import net.minecraft.item.PickaxeItem;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.tag.TagKey;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.math.Direction;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;
import net.minecraft.world.World;

/** Native Death and Tower pathway mechanics for the 1.18.2 no-KubeJS runtime. */
public final class DeathTowerAbilities {
    private DeathTowerAbilities() {}
    private static final Random RANDOM=new Random();
    private static final TagKey<EntityType<?>> UNDEAD=TagKey.of(Registry.ENTITY_TYPE_KEY,new Identifier("tarot","undead"));
    private static final TagKey<net.minecraft.block.Block> STONE=TagKey.of(Registry.BLOCK_KEY,new Identifier("tarot","natural_stone"));

    static boolean death(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("death",seq);
    }
    static boolean tower(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("tower",seq);
    }
    static boolean reaper(ArcaneSave.Record r,int seq) {
        return r!=null&&r.originValid&&r.profile.active("crumbling_reaper",seq);
    }
    static boolean deathIdentity(ArcaneSave.Record r) {
        return r!=null&&r.originValid&&r.profile.identityActive("death");
    }
    static boolean towerIdentity(ArcaneSave.Record r) {
        return r!=null&&r.originValid&&r.profile.identityActive("tower");
    }
    private static long time(ServerPlayerEntity player) {
        return player.getServer().getOverworld().getTime();
    }
    private static void effect(LivingEntity e,net.minecraft.entity.effect.StatusEffect status,int ticks,int amplifier) {
        e.addStatusEffect(new StatusEffectInstance(status,ticks,amplifier));
    }
    private static boolean undead(Entity entity) {
        return entity.getType().isIn(UNDEAD);
    }
    /** +30% mining speed only while the Tower stone-break kit is equipped. */
    public static float breakMultiplier(ServerPlayerEntity p,BlockState state) {
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && state.isIn(STONE) &&
            (tower(r,9)||reaper(r,9))?1.30f:1f;
    }
    public static boolean preventNaturalRegen(ServerPlayerEntity player) {
        return deathIdentity(ArcaneMod.profile(player));
    }
    public static float incoming(ServerPlayerEntity player,DamageSource source,float damage) {
        ArcaneSave.Record r=ArcaneMod.profile(player);
        if(r==null)return damage;
        if(source.isExplosive()) {
            if(reaper(r,9)||tower(r,9))damage*=.4f;
            if(tower(r,1))damage*=.5f; // −80% total (0.4 × 0.5).
        }
        if(source==DamageSource.FALL) {
            if(towerIdentity(r))damage*=1.75f;
            if((tower(r,6)||reaper(r,6)) &&
                (player.getMainHandStack().getItem() instanceof PickaxeItem ||
                    player.getOffHandStack().getItem() instanceof PickaxeItem))
                damage*=.8f;
        }
        if(source.getAttacker() instanceof LivingEntity attacker && undead(attacker)) {
            if(death(r,1))damage*=.65f;
            else if(death(r,9)||reaper(r,9))damage*=.75f;
        }
        return damage;
    }
    public static float outgoing(ServerPlayerEntity owner,LivingEntity victim,DamageSource source,float dmg) {
        ArcaneSave.Record r=ArcaneMod.profile(owner);
        if(r==null||!FoolAbilities.enemy(owner,victim))return dmg;
        if(source.getSource()==owner && (tower(r,9)||reaper(r,9)) &&
            r.ready("unstable_strike",time(owner),260)) {
            effect(victim,StatusEffects.SLOWNESS,tower(r,4)?40:20,0);
            ArcaneSave.get(owner.getServer()).markDirty();
        }
        return dmg;
    }
    public static void register() {
        UseBlockCallback.EVENT.register((player,world,hand,hit)->{
            if(world.isClient || !(player instanceof ServerPlayerEntity p) ||
                hand!=Hand.MAIN_HAND)return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            long t=time(p);
            BlockPos pos=hit.getBlockPos();
            BlockState block=world.getBlockState(pos);
            if(death(r,8) && (block.isOf(Blocks.SKELETON_SKULL)
                || block.isOf(Blocks.WITHER_SKELETON_SKULL)
                || block.isOf(Blocks.PLAYER_HEAD)
                || block.isOf(Blocks.ZOMBIE_HEAD))) {
                if(r.ready("grave_dirt",t,1200)) {
                    p.addExperience(1);state.markDirty();return ActionResult.SUCCESS;
                }
            }
            if(tower(r,8) && p.isSneaking() && block.isIn(STONE)
                && r.ready("charge",t,600)) {
                r.chargePosition=pos;
                r.chargeUntil=t+60;
                ArcaneMod.info(p,"Charge primed. Stone breaks harmlessly in 60 ticks.");
                state.markDirty();return ActionResult.SUCCESS;
            }
            if((death(r,3)||reaper(r,9)) &&
                world.getFluidState(pos).isIn(net.minecraft.tag.FluidTags.WATER)
                && r.ready("ferry",t,1200)) {
                effect(p,StatusEffects.DOLPHINS_GRACE,100,0); 
                // APPROX: true water walking needs a collision mixin.
                state.markDirty();return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
        PlayerBlockBreakEvents.AFTER.register((world,player,pos,oldState,blockEntity)-> {
            if(world.isClient || !(player instanceof ServerPlayerEntity p))return;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null||!oldState.isIn(STONE))return;
            if((tower(r,7)||reaper(r,8)) && RANDOM.nextFloat()<.05f) {
                BlockPos above=pos.up();
                if(world.getBlockState(above).isIn(STONE))
                    p.interactionManager.tryBreakBlock(above);
            }
            if(tower(r,9) && RANDOM.nextFloat()<.05f)
                ((ServerWorld)world).spawnParticles(ParticleTypes.CRIT,
                    pos.getX()+.5,pos.getY()+.5,pos.getZ()+.5,4,.3,.3,.3,.01);
        });
    }
    public static void onLand(ServerPlayerEntity p,float distance) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        if(distance>=4f && (tower(r,3)||reaper(r,7)))
            HangedAbilities.nova(p,p.getPos(),3,2f);
        if(distance>=3f && reaper(r,4))r.reaperFallUntil=time(p)+200;
        state.markDirty();
    }
    public static boolean rescue(ServerPlayerEntity p,float amount) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !death(r,4) || amount<p.getHealth()+p.getAbsorptionAmount())return false;
        if(RANDOM.nextFloat()>=.05f || !r.ready("undying",time(p),12000))return false;
        p.setHealth(2);
        state.markDirty();
        return true;
    }
    public static void onDamage(ServerPlayerEntity p,DamageSource source,float damage) {
        if(damage<=0)return;
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        if(reaper(r,2) && source==DamageSource.FALL)
            for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),8))
                e.damage(DamageSource.MAGIC,Math.max(1f,damage));
        state.markDirty();
    }
    public static void onHit(ServerPlayerEntity owner,LivingEntity target,DamageSource source) {
        ArcaneSave state=ArcaneSave.get(owner.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(owner);
        if(r==null || !FoolAbilities.enemy(owner,target))return;
        long now=time(owner);
        if(undead(target) && death(r,9) && r.ready("reapers_touch",now,200)) {
            effect(target,StatusEffects.WEAKNESS,60,0);
            state.markDirty();
        }
    }
    /** Nearby undead deaths trigger Guide regardless of who dealt the last hit. */
    public static void onAnyDeath(LivingEntity victim) {
        if(!undead(victim))return;
        for(ServerPlayerEntity observer:victim.getWorld().getEntitiesByClass(
            ServerPlayerEntity.class,new Box(victim.getBlockPos()).expand(8),
            player->player.isAlive() && player.squaredDistanceTo(victim)<=64)) {
            ArcaneSave.Record record=ArcaneMod.profile(observer);
            if(record==null || !FoolAbilities.enemy(observer,victim))continue;
            long now=time(observer);
            if((death(record,6)||reaper(record,6)) &&
                record.ready("guide",now,20)) {
                observer.heal(1f);
                ArcaneSave.get(observer.getServer()).markDirty();
            }
            if(reaper(record,3))
                HangedAbilities.nova(observer,victim.getPos(),3,1f);
        }
    }
    public static void onKill(ServerPlayerEntity owner,LivingEntity victim) {
        ArcaneSave state=ArcaneSave.get(owner.getServer());
        ArcaneSave.Record r=ArcaneMod.profile(owner);
        if(r==null||!FoolAbilities.enemy(owner,victim))return;
        long now=time(owner);
        if(death(r,9) && r.ready("soul_harvest",now,200))owner.heal(2f);
        if(undead(victim)) {
            if(death(r,9) && RANDOM.nextFloat()<.1f)
                victim.dropItem(Items.BONE); // APPROX: one extra bone, not 10% of actual loot table.
        }
        if(reaper(r,4) && now<r.reaperFallUntil) {
            owner.heal(8f);
            HangedAbilities.nova(owner,victim.getPos(),3,2f);
            r.reaperFallUntil=0;
        }
        if(reaper(r,2))owner.heal(2f);
        CrumblingReaper.onKill(owner,victim,state,r);
        state.markDirty();
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r) {
        long t=time(p);
        if((death(r,9)||death(r,1)||reaper(r,9))
            && p.getWorld().getLightLevel(p.getBlockPos())<=7)
            effect(p,StatusEffects.NIGHT_VISION,220,0);
        if(death(r,7)||reaper(r,7)) {
            if(p.isSneaking())r.spiritSenseTicks+=20;
            else r.spiritSenseTicks=0;
            if(r.spiritSenseTicks>=60 && r.ready("spirit_sense",t,600)) {
                for(LivingEntity undead:p.getWorld().getEntitiesByClass(LivingEntity.class,
                    new Box(p.getBlockPos()).expand(10),e->e.getType().isIn(UNDEAD)
                        && e.squaredDistanceTo(p)<=100))
                    effect(undead,StatusEffects.GLOWING,100,0);
                state.markDirty();
            }
        }
        if(r.chargePosition!=null && t>=r.chargeUntil) {
            BlockPos pos=r.chargePosition;r.chargePosition=null;
            if(p.getWorld().getBlockState(pos).isIn(STONE)
                && p.squaredDistanceTo(Vec3d.ofCenter(pos))<=81)
                p.interactionManager.tryBreakBlock(pos);
            state.markDirty();
        }
        // Landing bonuses now use the per-fall PlayerEntity.handleFallDamage
        // callback; 20-tick polling misses short 3-4 block falls.
        if(tower(r,2)) {
            List<LivingEntity> enemies=HangedAbilities.enemies(p,p.getPos(),5);
            if(!enemies.isEmpty() && r.ready("cataclysm",t,3600))
                for(LivingEntity enemy:enemies)
                    effect(enemy,StatusEffects.MINING_FATIGUE,200,0);
        }
        CrumblingReaper.tick(p,state,r);
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id) {
        long t=time(p);
        switch(id) {
            case "gate":
            case "gate_collapse": {
                if(!(death(r,5)||reaper(r,5)))return false;
                if(!canCreatePortal(p) || !r.ready(id,t,12000))return false;
                buildSafePortal(p);
                if(reaper(r,5))breakSquare(p,p.getBlockPos(),1);
                break;
            }
            case "collapse": {
                if(!tower(r,5)||!r.ready(id,t,1200))return false;
                breakSquare(p,p.getBlockPos().offset(p.getHorizontalFacing(),2),1);break;
            }
            case "consul": {
                if(!death(r,2)||!r.ready(id,t,6000))return false;
                VexEntity minion=HangedAbilities.spawnMinion(p,200,false,0,0);
                if(minion==null)return false;
                minion.addScoreboardTag("tarot_undead_consul");
                break;
            }
            case "reap": {
                if(!death(r,1)||!r.ready(id,t,2400))return false;
                LivingEntity target=HangedAbilities.enemies(p,p.getPos(),8).stream()
                    .filter(e->e.getHealth()/e.getMaxHealth()<.30f)
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                if(target==null)return false;
                target.damage(DamageSource.MAGIC,target.getHealth()+2);
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),8))
                    effect(e,StatusEffects.WEAKNESS,60,0);
                break;
            }
            case "falling_tower":
            case "falling_towers_reap": {
                boolean fused="falling_towers_reap".equals(id);
                if(!(fused?reaper(r,1):tower(r,1)) || !r.ready(id,t,2400))return false;
                p.addVelocity(0,1.2,0);
                // A controlled 8-block leap approximation with a 6-block impact zone.
                for(LivingEntity e:HangedAbilities.enemies(p,p.getPos(),6)) {
                    boolean execute=fused && e.getMaxHealth()>0 &&
                        e.getHealth()/e.getMaxHealth()<.20f;
                    boolean damaged=e.damage(DamageSource.MAGIC,
                        execute?e.getHealth()+2:10f);
                    effect(e,StatusEffects.SLOWNESS,100,1);
                    if(fused && damaged && !e.isAlive())
                        CrumblingReaper.grantAbsorption(p,state,r,20f,600);
                }
                break;
            }
            case "the_final_harvest":
            case "the_fall":
            case "the_crumbling_reaper":
                return CrumblingReaper.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    private static Direction portalWidth(ServerPlayerEntity owner) {
        return owner.getHorizontalFacing().getAxis()==Direction.Axis.X
            ?Direction.SOUTH:Direction.EAST;
    }
    private static BlockPos portalBase(ServerPlayerEntity owner) {
        return owner.getBlockPos().offset(owner.getHorizontalFacing(),3)
            .offset(portalWidth(owner),-1);
    }
    /** A full 4x5 portal frame must fit in untouched air with solid ground underneath. */
    private static boolean canCreatePortal(ServerPlayerEntity owner) {
        ServerWorld world=owner.getWorld();
        if(world.getRegistryKey()!=World.OVERWORLD &&
            world.getRegistryKey()!=World.NETHER)return false;
        BlockPos base=portalBase(owner);
        Direction width=portalWidth(owner);
        for(int x=0;x<4;x++) {
            if(!world.getBlockState(base.offset(width,x).down()).getMaterial().isSolid())
                return false;
            for(int y=0;y<5;y++)
                if(!world.getBlockState(base.offset(width,x).up(y)).isAir())
                    return false;
        }
        return true;
    }
    private static void buildSafePortal(ServerPlayerEntity owner) {
        ServerWorld world=owner.getWorld();
        BlockPos base=portalBase(owner);
        Direction width=portalWidth(owner);
        for(int x=0;x<4;x++)
          for(int y=0;y<5;y++)
            if(x==0 || x==3 || y==0 || y==4)
                world.setBlockState(base.offset(width,x).up(y),
                    Blocks.OBSIDIAN.getDefaultState(),3);
        for(int x=1;x<3;x++)
          for(int y=1;y<4;y++)
            world.setBlockState(base.offset(width,x).up(y),
                Blocks.NETHER_PORTAL.getDefaultState()
                    .with(NetherPortalBlock.AXIS,width.getAxis()),3);
    }
    private static void breakSquare(ServerPlayerEntity p,BlockPos center,int radius) {
        for(int dx=-radius;dx<=radius;dx++)
          for(int dz=-radius;dz<=radius;dz++) {
            BlockPos pos=center.add(dx,0,dz);
            if(p.getWorld().getBlockState(pos).isIn(STONE))
                p.interactionManager.tryBreakBlock(pos);
          }
    }
}
