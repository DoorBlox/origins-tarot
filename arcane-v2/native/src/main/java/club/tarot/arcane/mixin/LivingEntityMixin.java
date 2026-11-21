package club.tarot.arcane.mixin;

import club.tarot.arcane.FoolAbilities;
import club.tarot.arcane.FoolLegend;
import club.tarot.arcane.HangedAbilities;
import club.tarot.arcane.PaperMartyr;
import club.tarot.arcane.WorldJusticeAbilities;
import club.tarot.arcane.MarkedVerdict;
import club.tarot.arcane.Ascension;
import club.tarot.arcane.ArcaneMod;
import club.tarot.arcane.ArcaneSave;
import club.tarot.arcane.HermitChariotAbilities;
import club.tarot.arcane.BurningArchive;
import club.tarot.arcane.DeathTowerAbilities;
import club.tarot.arcane.CrumblingReaper;
import club.tarot.arcane.MagicianStrengthAbilities;
import club.tarot.arcane.EmperorLoversAbilities;
import club.tarot.arcane.BenevolentCrown;
import club.tarot.arcane.DevilJudgementAbilities;
import club.tarot.arcane.BindingContract;
import club.tarot.arcane.StarEmpressAbilities;
import club.tarot.arcane.StarlessPoison;
import club.tarot.arcane.ImpossibleFist;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.server.network.ServerPlayerEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The Minecraft 1.18.2 native replacement for KubeJS damage event hooks. */
@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin {
    @Unique private float tarot$effectiveHealthBefore;

    @ModifyVariable(method="damage", at=@At("HEAD"), argsOnly=true, index=2)
    private float tarot$scaleDamage(float damage, DamageSource source) {
        LivingEntity victim=(LivingEntity)(Object)this;
        float amount=HangedAbilities.scaleIncoming(victim,HangedAbilities.scaleOutgoing(victim,source,damage));
        amount=WorldJusticeAbilities.scaleIncoming(victim,source,
            WorldJusticeAbilities.scaleOutgoing(victim,source,amount));
        amount=HermitChariotAbilities.outgoing(victim,source,amount);
        if(victim instanceof ServerPlayerEntity target)
            amount=DeathTowerAbilities.incoming(target,source,amount);
        if(source.getAttacker() instanceof ServerPlayerEntity owner)
            amount=DeathTowerAbilities.outgoing(owner,victim,source,amount);
        if(victim instanceof ServerPlayerEntity target)
            amount=MagicianStrengthAbilities.incoming(target,source,amount);
        if(source.getAttacker() instanceof ServerPlayerEntity owner)
            amount=MagicianStrengthAbilities.outgoing(owner,victim,source,amount);
        amount=EmperorLoversAbilities.incoming(victim,source,amount);
        if(source.getAttacker() instanceof ServerPlayerEntity owner)
            amount=EmperorLoversAbilities.outgoing(owner,victim,source,amount);
        if(victim instanceof ServerPlayerEntity target)
            amount=DevilJudgementAbilities.incoming(target,source,amount);
        if(source.getAttacker() instanceof ServerPlayerEntity owner)
            amount=DevilJudgementAbilities.outgoing(owner,victim,source,amount);
        if(victim instanceof ServerPlayerEntity target)
            amount=StarEmpressAbilities.incoming(target,source,amount);
        if(source.getAttacker() instanceof ServerPlayerEntity owner)
            amount=StarEmpressAbilities.outgoing(owner,victim,source,amount);
        return amount;
    }
    @ModifyVariable(method="heal",at=@At("HEAD"),argsOnly=true,index=1)
    private float tarot$loversHealing(float healing) {
        if((Object)this instanceof ServerPlayerEntity player)
            return DevilJudgementAbilities.healingMultiplier(player,
                EmperorLoversAbilities.healMultiplier(player,healing));
        return healing;
    }

    @Inject(method="damage",at=@At("HEAD"))
    private void tarot$captureBefore(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        LivingEntity victim=(LivingEntity)(Object)this;
        tarot$effectiveHealthBefore=victim.getHealth()+victim.getAbsorptionAmount();
    }

    @Inject(method="damage",at=@At("HEAD"),cancellable=true)
    private void tarot$rescue(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        LivingEntity victim=(LivingEntity)(Object)this;
        if((victim instanceof ServerPlayerEntity p && StarlessPoison.mirrorImmune(p)) ||
            BenevolentCrown.protectsPassive(victim) ||
            BenevolentCrown.preventAttack(victim,source) ||
            BindingContract.preventAttack(victim,source)) {
            cir.setReturnValue(false);
            return;
        }
        if((Object)this instanceof ServerPlayerEntity p &&
            DevilJudgementAbilities.fireImmune(p,source)) {
            cir.setReturnValue(false);
            return;
        }
        if((Object)this instanceof ServerPlayerEntity p &&
            MagicianStrengthAbilities.fallSave(p,source)) {
            cir.setReturnValue(false);
            return;
        }
        if((Object)this instanceof ServerPlayerEntity p &&
            (HermitChariotAbilities.fireImmune(p,source) || BurningArchive.immortalDash(p))) {
            cir.setReturnValue(false);
            return;
        }
        if(WorldJusticeAbilities.cancelDamage((LivingEntity)(Object)this,source)) {
            cir.setReturnValue(false);
            return;
        }
        if(FoolLegend.immuneToDamage((LivingEntity)(Object)this,source)) {
            cir.setReturnValue(false);
            return;
        }
        if(FoolAbilities.cancelFriendlyMinionHit((LivingEntity)(Object)this,source)) {
            cir.setReturnValue(false);
            return;
        }
        if ((Object)this instanceof ServerPlayerEntity p &&
            DeathTowerAbilities.rescue(p,amount)) {
            cir.setReturnValue(false);
            return;
        }
        if ((Object)this instanceof ServerPlayerEntity p &&
            WorldJusticeAbilities.rescue(p,source,amount)) {
            cir.setReturnValue(false);
            return;
        }
        if ((Object)this instanceof ServerPlayerEntity p && PaperMartyr.rescue(p,amount)) {
            cir.setReturnValue(false);
            return;
        }
        if ((Object)this instanceof ServerPlayerEntity
            && FoolAbilities.rescueIfLethal((ServerPlayerEntity)(Object)this,source,amount))
            cir.setReturnValue(false);
    }

    @Inject(method="damage",at=@At("RETURN"))
    private void tarot$afterDamage(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        if (Boolean.TRUE.equals(cir.getReturnValue())) {
            FoolLegend.afterSuccessfulHit((LivingEntity)(Object)this,source);
            WorldJusticeAbilities.onSuccessfulHit((LivingEntity)(Object)this,source);
            BenevolentCrown.onSuccessfulHit((LivingEntity)(Object)this,source);
            if(source.getAttacker() instanceof ServerPlayerEntity caster) {
                DevilJudgementAbilities.onSuccessfulHit(caster,(LivingEntity)(Object)this,source);
                StarEmpressAbilities.onSuccessfulHit(caster,(LivingEntity)(Object)this,source);
            }
            if(source.getAttacker() instanceof ServerPlayerEntity owner)
                DeathTowerAbilities.onHit(owner,(LivingEntity)(Object)this,source);
            if(source.getAttacker() instanceof ServerPlayerEntity attacker)
                HermitChariotAbilities.onSuccessfulHit(attacker,(LivingEntity)(Object)this,source);
            if(source.getAttacker() instanceof ServerPlayerEntity attacker) {
                ArcaneSave.Record r=ArcaneSave.get(attacker.getServer()).getPlayer(attacker.getUuid());
                if(r!=null&&r.originValid) {
                    r.combat(attacker.getServer().getOverworld().getTime());
                    ArcaneSave.get(attacker.getServer()).markDirty();
                }
            }
        }
        if (Boolean.TRUE.equals(cir.getReturnValue())
            && (Object)this instanceof ServerPlayerEntity) {
            ServerPlayerEntity p=(ServerPlayerEntity)(Object)this;
            float taken=Math.max(0f,tarot$effectiveHealthBefore-p.getHealth()-p.getAbsorptionAmount());
            HangedAbilities.onDamage(p,source,taken);
            WorldJusticeAbilities.onTakenDamage(p,source,taken);
            HermitChariotAbilities.onTakenDamage(p,source,taken);
            DeathTowerAbilities.onDamage(p,source,taken);
            EmperorLoversAbilities.onTakenDamage(p,source,taken);
            DevilJudgementAbilities.onTakenDamage(p,source,taken);
            StarEmpressAbilities.onTakenDamage(p,source,taken);
            FoolAbilities.afterDamage(p,source);
        }
    }

    @Inject(method="jump",at=@At("TAIL"))
    private void tarot$travelerJump(CallbackInfo ci) {
        if((Object)this instanceof ServerPlayerEntity player) {
            float multiplier=MagicianStrengthAbilities.jumpMultiplier(player);
            if(multiplier!=1f){
                net.minecraft.util.math.Vec3d velocity=player.getVelocity();
                player.setVelocity(velocity.x,velocity.y*multiplier,velocity.z);
                player.velocityModified=true;
            }
        }
    }

    @Inject(method="jump",at=@At("HEAD"),cancellable=true)
    private void tarot$blockJump(CallbackInfo ci) {
        if((Object)this instanceof ServerPlayerEntity player &&
            (!WorldJusticeAbilities.canJump(player) ||
                !BenevolentCrown.maySprintOrJump(player) ||
                !BindingContract.mayJump(player)))ci.cancel();
    }

    @Inject(method="onDeath",at=@At("HEAD"))
    private void tarot$onDeath(DamageSource source,CallbackInfo ci) {
        LivingEntity victim=(LivingEntity)(Object)this;
        HangedAbilities.onMinionDeath(victim);
        DeathTowerAbilities.onAnyDeath(victim);
        EmperorLoversAbilities.onAnyDeath(victim);
        BenevolentCrown.onAnyDeath(victim);
        BindingContract.onAnyDeath(victim,source);
        if(victim instanceof ServerPlayerEntity p) {
            HangedAbilities.onPlayerDeath(p);
            // Stop all timed powers immediately on death, before any fresh
            // Origin grants/respawn; never leave flight/noClip or living minions.
            FoolLegend.stopOnDisconnect(p);
            HangedAbilities.stopOnDisconnect(p);
            PaperMartyr.stopOnDisconnect(p);
            WorldJusticeAbilities.stopOnDisconnect(p);
            BurningArchive.stopOnDisconnect(p);
            CrumblingReaper.stopOnDisconnect(p);
            ImpossibleFist.stopOnDisconnect(p);
            EmperorLoversAbilities.stopOnDisconnect(p);
            DevilJudgementAbilities.stopOnDisconnect(p);
            StarEmpressAbilities.stopOnDisconnect(p);
        }
        if(source.getAttacker() instanceof ServerPlayerEntity attacker) {
            HangedAbilities.onKill(attacker,victim);
            WorldJusticeAbilities.onKill(attacker,victim);
            HermitChariotAbilities.onKill(attacker,victim);
            DeathTowerAbilities.onKill(attacker,victim);
            DevilJudgementAbilities.onKill(attacker,victim);
            StarEmpressAbilities.onKill(attacker,victim);
            Ascension.onKill(attacker,victim);
        }
    }
}
