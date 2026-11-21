package club.tarot.arcane;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.minecraft.block.BlockState;
import net.minecraft.block.CropBlock;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttribute;
import net.minecraft.entity.attribute.EntityAttributeInstance;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.effect.StatusEffect;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.mob.MobEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.tag.TagKey;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.Vec3d;
import net.minecraft.util.registry.Registry;

/** Native Emperor, Lovers, and Benevolent Crown sequence handlers. */
public final class EmperorLoversAbilities {
    private EmperorLoversAbilities() {}
    private static final TagKey<EntityType<?>> PASSIVE=TagKey.of(
        Registry.ENTITY_TYPE_KEY,new Identifier("tarot","passive"));
    private static final UUID ARMOR=UUID.fromString("d7fc49b0-6ab3-4c22-b4ce-81ecda4d9303");
    private static final UUID KB=UUID.fromString("d7fc49b0-6ab3-4c22-b4ce-81ecda4d9304");
    private static final UUID SHIELD_SPEED=UUID.fromString("d7fc49b0-6ab3-4c22-b4ce-81ecda4d9305");
    private static final UUID AURA_SPEED=UUID.fromString("d7fc49b0-6ab3-4c22-b4ce-81ecda4d9306");
    private static final UUID SYMBIOSIS_HEALTH=UUID.fromString("d7fc49b0-6ab3-4c22-b4ce-81ecda4d9307");
    private static final double PAIR_RANGE=64;

    static boolean emperor(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("emperor",seq);
    }
    static boolean lovers(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("lovers",seq);
    }
    static boolean crown(ArcaneSave.Record r,int seq){
        return r!=null&&r.originValid&&r.profile.active("benevolent_crown",seq);
    }
    static boolean emperorIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("emperor");
    }
    static boolean loversIdentity(ArcaneSave.Record r){
        return r!=null&&r.originValid&&r.profile.identityActive("lovers");
    }
    static boolean passive(Entity entity){return entity.getType().isIn(PASSIVE);}
    private static long time(ServerPlayerEntity p){return p.getServer().getOverworld().getTime();}
    private static void effect(LivingEntity e,StatusEffect status,int duration,int amplifier){
        e.addStatusEffect(new StatusEffectInstance(status,duration,amplifier));
    }
    private static void modifier(ServerPlayerEntity p,EntityAttribute attribute,UUID key,
                                 String label,double value,EntityAttributeModifier.Operation op,
                                 boolean enabled){
        EntityAttributeInstance instance=p.getAttributeInstance(attribute);
        if(instance==null)return;
        if(instance.getModifier(key)!=null)instance.removeModifier(key);
        if(enabled)instance.addTemporaryModifier(new EntityAttributeModifier(key,label,value,op));
    }
    static boolean shield(ServerPlayerEntity p){
        return p.getMainHandStack().isOf(Items.SHIELD)||p.getOffHandStack().isOf(Items.SHIELD);
    }
    static boolean armor(ServerPlayerEntity p){
        for(ItemStack stack:p.getArmorItems())if(!stack.isEmpty())return true;
        return false;
    }
    private static boolean nearAnyPlayer(ServerPlayerEntity p){
        return !p.getWorld().getEntitiesByClass(PlayerEntity.class,
            new Box(p.getBlockPos()).expand(8),
            e->e!=p && e.isAlive() && e.squaredDistanceTo(p)<=PAIR_RANGE).isEmpty();
    }
    private static List<ServerPlayerEntity> teamNearby(ServerPlayerEntity p,double radius){
        return p.getWorld().getEntitiesByClass(ServerPlayerEntity.class,
            new Box(p.getBlockPos()).expand(radius),
            e->e!=p && e.isAlive() && e.squaredDistanceTo(p)<=radius*radius
                && HangedAbilities.ally(p,e));
    }
    private static boolean nearPassive(ServerPlayerEntity p,double radius){
        return !p.getWorld().getEntitiesByClass(LivingEntity.class,
            new Box(p.getBlockPos()).expand(radius),
            e->e.isAlive() && passive(e) && e.squaredDistanceTo(p)<=radius*radius).isEmpty();
    }
    private static void removePositive(LivingEntity target){
        for(StatusEffectInstance e:new ArrayList<>(target.getStatusEffects()))
            if(e.getEffectType().isBeneficial())target.removeStatusEffect(e.getEffectType());
    }
    private static void pacifyMob(LivingEntity target){
        if(target instanceof MobEntity mob){mob.setTarget(null);mob.getNavigation().stop();}
    }
    private static boolean takeIron(ServerPlayerEntity p,int amount){
        int count=0;for(int i=0;i<p.getInventory().size();i++){
            ItemStack stack=p.getInventory().getStack(i);
            if(stack.isOf(Items.IRON_INGOT))count+=stack.getCount();
        }
        if(count<amount)return false;
        int remaining=amount;
        for(int i=0;i<p.getInventory().size() && remaining>0;i++){
            ItemStack stack=p.getInventory().getStack(i);
            if(stack.isOf(Items.IRON_INGOT)){
                int n=Math.min(stack.getCount(),remaining);stack.decrement(n);remaining-=n;
            }
        }
        p.getInventory().markDirty();return true;
    }
    private static boolean takeGold(ServerPlayerEntity p){
        for(int i=0;i<p.getInventory().size();i++){
            ItemStack stack=p.getInventory().getStack(i);
            if(stack.isOf(Items.GOLD_INGOT)){stack.decrement(1);p.getInventory().markDirty();return true;}
        }
        return false;
    }
    public static void register(){
        UseEntityCallback.EVENT.register((player,world,hand,entity,hit)->{
            if(world.isClient||!(player instanceof ServerPlayerEntity p)||hand!=Hand.MAIN_HAND
                || !(entity instanceof LivingEntity target))return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            long now=time(p);
            if(entity instanceof ServerPlayerEntity ally && HangedAbilities.ally(p,ally)
                && (lovers(r,8)||crown(r,1)) && r.ready("triage",now,400)){
                ally.heal(2f);
                if(crown(r,1)){
                    LivingEntity enemy=HangedAbilities.enemies(p,ally.getPos(),6).stream()
                        .min(Comparator.comparingDouble(ally::squaredDistanceTo)).orElse(null);
                    if(enemy!=null){
                        effect(enemy,StatusEffects.SLOWNESS,60,0);
                        enemy.damage(DamageSource.MAGIC,2f);
                    }
                }
                state.markDirty();return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
        UseBlockCallback.EVENT.register((player,world,hand,hit)->{
            if(world.isClient||!(player instanceof ServerPlayerEntity p)
                || hand!=Hand.MAIN_HAND||!p.isSneaking())return ActionResult.PASS;
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r==null)return ActionResult.PASS;
            BlockPos pos=hit.getBlockPos();
            BlockState block=world.getBlockState(pos);
            long now=time(p);
            if((lovers(r,7)||crown(r,7)) && block.getBlock() instanceof CropBlock crop){
                // Per-crop cooldown: a plant's location, NOT a global ability cooldown.
                String key="crop:"+world.getRegistryKey().getValue()+":"+pos.asLong();
                if(!r.ready(key,now,1200))return ActionResult.PASS;
                world.setBlockState(pos,crop.withAge(crop.getMaxAge()),3);
                state.markDirty();return ActionResult.SUCCESS;
            }
            if((emperor(r,6)||crown(r,6)) && block.getMaterial().isSolid()
                && r.ready("corrupt_ground",now,1200)){
                r.corruptCenter=pos.up();
                r.corruptUntil=now+600;
                r.corruptDimension=world.getRegistryKey().getValue().toString();
                state.markDirty();
                ArcaneMod.info(p,"Corrupt Ground active: 5x5 for 600 ticks.");
                return ActionResult.SUCCESS;
            }
            return ActionResult.PASS;
        });
    }
    /**
     * Permanent drawbacks multiply the vanilla exhaustion amount only when
     * their source conditions are true; they continue to apply at Seq4/Seq1.
     */
    public static float exhaustion(ServerPlayerEntity p,float amount){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return amount;
        if(emperorIdentity(r) && p.isSprinting() && armor(p))amount*=1.50f;
        if(loversIdentity(r) && CrownRules.separationActive(r.aloneTicks))amount*=1.35f;
        return amount;
    }
    public static float healMultiplier(ServerPlayerEntity p,float amount){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        return r!=null && (lovers(r,9)||crown(r,9))?amount*1.25f:amount;
    }
    public static float breakSpeed(ServerPlayerEntity p,BlockState target){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return 1f;
        float factor=1f;
        if((lovers(r,9)||crown(r,9)) && target.getBlock() instanceof CropBlock)factor*=1.20f;
        if(loversIdentity(r) && CrownRules.separationActive(r.aloneTicks))factor*=.85f;
        return factor;
    }
    public static float outgoing(ServerPlayerEntity p,LivingEntity victim,DamageSource source,float value){
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null || !FoolAbilities.enemy(p,victim))return value;
        if(BenevolentCrown.domainOf(p,"the_emperors_domain"))value*=1.15f;
        if(BenevolentCrown.domainOf(p,"the_benevolent_crown"))value*=1.20f;
        if(BenevolentCrown.consortDamage(p))value*=1.15f;
        return value;
    }
    public static float incoming(LivingEntity victim,DamageSource source,float value){
        if(victim instanceof ServerPlayerEntity p){
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r!=null){
                if((emperor(r,9)||crown(r,9)) && shield(p)){
                    boolean improved=emperor(r,1);
                    value*=CrownRules.shieldDamageMultiplier(true,improved);
                }
                if(BenevolentCrown.domainOf(p,"the_emperors_domain"))value*=.85f;
                if(BenevolentCrown.domainOf(p,"the_benevolent_crown"))value*=.80f;
                if(crown(r,2) && time(p)<r.decreeUntil)value*=.90f;
            }
            // These benefits must apply to same-team non-Tarot allies too.
            if(BenevolentCrown.consortDamage(p))value*=.85f;
            if(BenevolentCrown.linkedCrownShield(p))value*=.95f;
        }
        if(source.isProjectile() && victim.getWorld() instanceof net.minecraft.server.world.ServerWorld world){
            // One protective field per eligible Emperor; no compounding from
            // overlapping domains or independent slots.
            for(ServerPlayerEntity caster:world.getPlayers()){
                ArcaneSave.Record r=ArcaneMod.profile(caster);
                if(r==null || !emperor(r,2) || caster.squaredDistanceTo(victim)>25)continue;
                long now=time(caster);
                if(r.entropyUntil<now && r.ready("entropy_field",now,3600)){
                    r.entropyUntil=now+100;
                    ArcaneSave.get(caster.getServer()).markDirty();
                }
                if(now<r.entropyUntil){value*=.5f;break;}
            }
        }
        return value;
    }
    public static void onTakenDamage(ServerPlayerEntity p,DamageSource source,float taken){
        if(taken<=0)return;
        ArcaneSave.Record r=ArcaneMod.profile(p);
        if(r==null)return;
        Entity enemy=source.getAttacker();
        if(!(enemy instanceof LivingEntity victim) || !FoolAbilities.enemy(p,victim))return;
        long now=time(p);
        if((emperor(r,9)||crown(r,9)) && r.ready("distorted_authority",now,280)){
            effect(victim,StatusEffects.SLOWNESS,emperor(r,4)?60:40,0);
            if(emperor(r,4))effect(victim,StatusEffects.WEAKNESS,20,0);
            ArcaneSave.get(p.getServer()).markDirty();
        }
    }
    public static void onAnyDeath(LivingEntity victim){
        if(!passive(victim))return;
        for(ServerPlayerEntity p:victim.getWorld().getEntitiesByClass(
            ServerPlayerEntity.class,new Box(victim.getBlockPos()).expand(8),
            x->x.isAlive() && x.squaredDistanceTo(victim)<=64)){
            ArcaneSave.Record r=ArcaneMod.profile(p);
            if(r!=null && lovers(r,3))effect(p,StatusEffects.REGENERATION,60,0);
        }
    }
    private static boolean standingInCorrupt(ServerPlayerEntity p,ArcaneSave.Record r,
                                              LivingEntity target,long t){
        return r.corruptCenter!=null && r.corruptUntil>t &&
            p.getWorld().getRegistryKey().getValue().toString().equals(r.corruptDimension)
            && Math.abs(target.getBlockX()-r.corruptCenter.getX())<=2
            && Math.abs(target.getBlockZ()-r.corruptCenter.getZ())<=2
            && Math.abs(target.getBlockY()-r.corruptCenter.getY())<=2;
    }
    public static void tick(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r){
        long t=time(p);
        if(loversIdentity(r)){
            if(nearAnyPlayer(p))r.aloneTicks=0;
            else r.aloneTicks=Math.min(1200,r.aloneTicks+20);
        }else r.aloneTicks=0;
        if((emperor(r,8)||crown(r,8)) && p.getHealth()<12f)
            p.removeStatusEffect(StatusEffects.WEAKNESS);
        modifier(p,EntityAttributes.GENERIC_ARMOR,ARMOR,"Sovereign's Plate",3,
            EntityAttributeModifier.Operation.ADDITION,emperor(r,9)||crown(r,9));
        modifier(p,EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE,KB,"Sovereign's Stance",
            .40,EntityAttributeModifier.Operation.ADDITION,emperor(r,9)||crown(r,9));
        modifier(p,EntityAttributes.GENERIC_MOVEMENT_SPEED,SHIELD_SPEED,"Weight of the Crown",
            -.25,EntityAttributeModifier.Operation.MULTIPLY_TOTAL,emperorIdentity(r)&&shield(p));

        if((emperor(r,9)) && shield(p)){
            List<LivingEntity> villagers=p.getWorld().getEntitiesByClass(LivingEntity.class,
                new Box(p.getBlockPos()).expand(8),e->e.getType()==EntityType.VILLAGER
                    && e.squaredDistanceTo(p)<=PAIR_RANGE);
            if(!villagers.isEmpty())
                effect(p,StatusEffects.HERO_OF_THE_VILLAGE,40,0);
            // APPROX: Hero of the Village affects trades, not an exact 10% discount.
        }
        if((lovers(r,9)) && !teamNearby(p,8).isEmpty() && r.ready("linked_hearts",t,500)){
            List<ServerPlayerEntity> team=teamNearby(p,8);
            p.heal(1f);
            for(ServerPlayerEntity member:team)member.heal(1f);
        }
        if((lovers(r,9)||lovers(r,1)) && nearAnyPlayer(p)
            && r.ready("shared_refuge",t,600)){
            effect(p,StatusEffects.RESISTANCE,lovers(r,1)?40:60,0);
            if(lovers(r,1))effect(p,StatusEffects.REGENERATION,40,0);
        }
        if((emperor(r,3)) && p.getHealth()<8f && r.ready("frenzy",t,600)){
            effect(p,StatusEffects.SPEED,100,0);
            effect(p,StatusEffects.HASTE,100,0);
        }
        if((lovers(r,2)) && !HangedAbilities.enemies(p,p.getPos(),5).isEmpty()
            && r.ready("withering",t,3600))
            for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),5))
                effect(enemy,StatusEffects.WITHER,60,0);
        if((emperor(r,6)||crown(r,6)) && r.corruptCenter!=null && r.corruptUntil>t){
            for(LivingEntity enemy:HangedAbilities.enemies(p,Vec3d.ofCenter(r.corruptCenter),5))
                if(standingInCorrupt(p,r,enemy,t))effect(enemy,StatusEffects.SLOWNESS,40,0);
            if(crown(r,3)){
                for(ServerPlayerEntity player:teamNearby(p,8))
                    if(standingInCorrupt(p,r,player,t))
                        effect(player,StatusEffects.REGENERATION,60,0);
                if(standingInCorrupt(p,r,p,t))effect(p,StatusEffects.REGENERATION,60,0);
            }
        }
        if(crown(r,4) && shield(p) && t%200==0)
            for(ServerPlayerEntity ally:teamNearby(p,8))ally.heal(1f);
        if(t%1200==0)r.cooldowns.entrySet().removeIf(e->
            e.getKey().startsWith("crop:") && t-e.getValue()>1200);
        BenevolentCrown.tick(p,state,r);
        state.markDirty();
    }
    /** Updates server-managed, source-specific modifiers for non-Tarot allies too. */
    public static void updateAllies(MinecraftServer server){
        for(ServerPlayerEntity target:server.getPlayerManager().getPlayerList()){
            double speed=0;
            boolean health=false;
            for(ServerPlayerEntity owner:server.getPlayerManager().getPlayerList()){
                if(owner.getWorld()!=target.getWorld())continue;
                ArcaneSave.Record r=ArcaneMod.profile(owner);
                if(r==null)continue;
                boolean ally=HangedAbilities.ally(owner,target);
                if(ally && owner!=target && target.squaredDistanceTo(owner)<=PAIR_RANGE){
                    if(lovers(r,9))speed=Math.max(speed,.10);
                    if(crown(r,9))speed=Math.max(speed,.05);
                }
                if(owner==target && lovers(r,9) && !teamNearby(owner,8).isEmpty())
                    speed=Math.max(speed,.10);
                if(owner==target && crown(r,9) && !teamNearby(owner,8).isEmpty())
                    speed=Math.max(speed,.05);
                if(ally && BenevolentCrown.allySpeed(owner,target))speed=Math.max(speed,.10);
                if(ally && (lovers(r,6)||crown(r,8)||crown(r,6)) &&
                    nearPassive(owner,4) && target.squaredDistanceTo(owner)<=PAIR_RANGE)
                    health=true;
            }
            modifier(target,EntityAttributes.GENERIC_MOVEMENT_SPEED,AURA_SPEED,"Tarot Linked Speed",
                speed,EntityAttributeModifier.Operation.MULTIPLY_TOTAL,speed>0);
            modifier(target,EntityAttributes.GENERIC_MAX_HEALTH,SYMBIOSIS_HEALTH,
                "Tarot Symbiosis",1,EntityAttributeModifier.Operation.ADDITION,health);
        }
    }
    public static boolean cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String id){
        long t=time(p);
        switch(id){
            case "coin":case "coins_blessing":{
                if(!(emperor(r,7)||crown(r,7)))return false;
                LivingEntity target=HangedAbilities.enemies(p,p.getPos(),8).stream()
                    .min(Comparator.comparingDouble(p::squaredDistanceTo)).orElse(null);
                boolean gold=false;
                for(ItemStack item:p.getInventory().main)if(item.isOf(Items.GOLD_INGOT)){gold=true;break;}
                if(target==null||!gold||!r.ready("coin",t,600))return false;
                if(!takeGold(p))return false;
                BenevolentCrown.pacify(p,target,100);
                state.markDirty();break;
            }
            case "decree":case "decree_of_nature":case "emperors_hymn":{
                if(!(emperor(r,5)||crown(r,5)||crown(r,2)))return false;
                int cooldown=id.equals("emperors_hymn")?900:900;
                if(!r.ready(id,t,cooldown))return false;
                for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),6)){
                    if(enemy instanceof MobEntity mob)mob.setTarget(p);
                    else effect(enemy,StatusEffects.GLOWING,100,0);
                    if(crown(r,5)||crown(r,2))
                        effect(enemy,StatusEffects.SLOWNESS,100,1);
                }
                if(crown(r,2)){
                    r.decreeUntil=t+200;
                    effect(p,StatusEffects.RESISTANCE,200,0);
                    for(ServerPlayerEntity ally:teamNearby(p,8))
                        effect(ally,StatusEffects.REGENERATION,200,0);
                }else if(crown(r,5))for(ServerPlayerEntity ally:teamNearby(p,8))
                    effect(ally,StatusEffects.REGENERATION,100,0);
                break;
            }
            case "natures_grasp":{
                if(!lovers(r,5)||!r.ready(id,t,900))return false;
                for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),4))
                    effect(enemy,StatusEffects.SLOWNESS,60,1);
                break;
            }
            case "transmute":{
                if(!lovers(r,4))return false;
                int count=0;for(ItemStack item:p.getInventory().main)
                    if(item.isOf(Items.IRON_INGOT))count+=item.getCount();
                if(count<2||!r.ready(id,t,12000))return false;
                if(!takeIron(p,2))return false;
                p.getInventory().insertStack(new ItemStack(Items.GOLD_INGOT));
                break;
            }
            case "abolish":{
                if(!emperor(r,1)||!r.ready(id,t,1800))return false;
                for(LivingEntity enemy:HangedAbilities.enemies(p,p.getPos(),8)){
                    removePositive(enemy);
                    effect(enemy,StatusEffects.SLOWNESS,100,1);
                    effect(enemy,StatusEffects.WEAKNESS,100,0);
                }
                break;
            }
            case "natures_step":{
                if(!lovers(r,1)||!r.ready(id,t,2400))return false;
                r.natureStepUntil=t+300;
                p.heal(4f);
                effect(p,StatusEffects.REGENERATION,200,0);
                for(ServerPlayerEntity ally:teamNearby(p,8)){
                    ally.heal(4f);effect(ally,StatusEffects.REGENERATION,200,0);
                }
                // APPROX: true temporary leaves-phasing needs safe client collision.
                break;
            }
            case "the_emperors_domain":case "the_garden":case "the_benevolent_crown":
                return BenevolentCrown.cast(p,state,r,id);
            default:return false;
        }
        state.markDirty();return true;
    }
    public static void stopOnDisconnect(ServerPlayerEntity p){
        BenevolentCrown.stopOnDisconnect(p);
        modifier(p,EntityAttributes.GENERIC_ARMOR,ARMOR,"Sovereign's Plate",0,
            EntityAttributeModifier.Operation.ADDITION,false);
        modifier(p,EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE,KB,"Sovereign's Stance",0,
            EntityAttributeModifier.Operation.ADDITION,false);
        modifier(p,EntityAttributes.GENERIC_MOVEMENT_SPEED,SHIELD_SPEED,"Weight of the Crown",0,
            EntityAttributeModifier.Operation.MULTIPLY_TOTAL,false);
        modifier(p,EntityAttributes.GENERIC_MOVEMENT_SPEED,AURA_SPEED,"Tarot Linked Speed",0,
            EntityAttributeModifier.Operation.MULTIPLY_TOTAL,false);
        modifier(p,EntityAttributes.GENERIC_MAX_HEALTH,SYMBIOSIS_HEALTH,"Tarot Symbiosis",0,
            EntityAttributeModifier.Operation.ADDITION,false);
    }
}
