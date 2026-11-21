package club.tarot.arcane.mixin;

import club.tarot.arcane.FoolAbilities;
import club.tarot.arcane.FoolLegend;
import club.tarot.arcane.HangedAbilities;
import club.tarot.arcane.PaperMartyr;
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
        return HangedAbilities.scaleIncoming(victim,HangedAbilities.scaleOutgoing(victim,source,damage));
    }

    @Inject(method="damage",at=@At("HEAD"))
    private void tarot$captureBefore(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        LivingEntity victim=(LivingEntity)(Object)this;
        tarot$effectiveHealthBefore=victim.getHealth()+victim.getAbsorptionAmount();
    }

    @Inject(method="damage",at=@At("HEAD"),cancellable=true)
    private void tarot$rescue(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        if(FoolLegend.immuneToDamage((LivingEntity)(Object)this,source)) {
            cir.setReturnValue(false);
            return;
        }
        if(FoolAbilities.cancelFriendlyMinionHit((LivingEntity)(Object)this,source)) {
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
        if (Boolean.TRUE.equals(cir.getReturnValue()))
            FoolLegend.afterSuccessfulHit((LivingEntity)(Object)this,source);
        if (Boolean.TRUE.equals(cir.getReturnValue())
            && (Object)this instanceof ServerPlayerEntity) {
            ServerPlayerEntity p=(ServerPlayerEntity)(Object)this;
            float taken=Math.max(0f,tarot$effectiveHealthBefore-p.getHealth()-p.getAbsorptionAmount());
            HangedAbilities.onDamage(p,source,taken);
            FoolAbilities.afterDamage(p,source);
        }
    }

    @Inject(method="onDeath",at=@At("HEAD"))
    private void tarot$onDeath(DamageSource source,CallbackInfo ci) {
        LivingEntity victim=(LivingEntity)(Object)this;
        HangedAbilities.onMinionDeath(victim);
        if(victim instanceof ServerPlayerEntity p)HangedAbilities.onPlayerDeath(p);
        if(source.getAttacker() instanceof ServerPlayerEntity attacker)
            HangedAbilities.onKill(attacker,victim);
    }
}
