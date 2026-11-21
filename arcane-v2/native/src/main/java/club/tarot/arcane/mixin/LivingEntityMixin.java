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
        return HermitChariotAbilities.outgoing(victim,source,amount);
    }

    @Inject(method="damage",at=@At("HEAD"))
    private void tarot$captureBefore(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        LivingEntity victim=(LivingEntity)(Object)this;
        tarot$effectiveHealthBefore=victim.getHealth()+victim.getAbsorptionAmount();
    }

    @Inject(method="damage",at=@At("HEAD"),cancellable=true)
    private void tarot$rescue(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
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
            FoolAbilities.afterDamage(p,source);
        }
    }

    @Inject(method="jump",at=@At("HEAD"),cancellable=true)
    private void tarot$blockJump(CallbackInfo ci) {
        if((Object)this instanceof ServerPlayerEntity player &&
            !WorldJusticeAbilities.canJump(player))ci.cancel();
    }

    @Inject(method="onDeath",at=@At("HEAD"))
    private void tarot$onDeath(DamageSource source,CallbackInfo ci) {
        LivingEntity victim=(LivingEntity)(Object)this;
        HangedAbilities.onMinionDeath(victim);
        if(victim instanceof ServerPlayerEntity p)HangedAbilities.onPlayerDeath(p);
        if(source.getAttacker() instanceof ServerPlayerEntity attacker) {
            HangedAbilities.onKill(attacker,victim);
            WorldJusticeAbilities.onKill(attacker,victim);
            HermitChariotAbilities.onKill(attacker,victim);
            Ascension.onKill(attacker,victim);
        }
    }
}
