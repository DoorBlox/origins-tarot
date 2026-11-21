package club.tarot.arcane.mixin;

import club.tarot.arcane.FoolAbilities;
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
    @Inject(method="damage",at=@At("HEAD"),cancellable=true)
    private void tarot$rescue(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        if ((Object)this instanceof ServerPlayerEntity
            && FoolAbilities.rescueIfLethal((ServerPlayerEntity)(Object)this,source,amount))
            cir.setReturnValue(false);
    }

    @Inject(method="damage",at=@At("RETURN"))
    private void tarot$afterDamage(DamageSource source,float amount,CallbackInfoReturnable<Boolean> cir) {
        if (Boolean.TRUE.equals(cir.getReturnValue())
            && (Object)this instanceof ServerPlayerEntity)
            FoolAbilities.afterDamage((ServerPlayerEntity)(Object)this,source);
    }
}
