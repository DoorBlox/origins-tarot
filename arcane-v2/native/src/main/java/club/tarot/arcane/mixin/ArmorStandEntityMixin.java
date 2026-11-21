package club.tarot.arcane.mixin;
import club.tarot.arcane.PaperMartyr;
import net.minecraft.entity.decoration.ArmorStandEntity;
import net.minecraft.entity.damage.DamageSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Paper decoy tags are damage interceptors; ordinary armor stands remain untouched. */
@Mixin(ArmorStandEntity.class)
public abstract class ArmorStandEntityMixin {
    @Inject(method="damage",at=@At("HEAD"),cancellable=true)
    private void tarot$decoyHit(DamageSource source,float damage,CallbackInfoReturnable<Boolean> cir) {
        if(PaperMartyr.breakDecoy((ArmorStandEntity)(Object)this))cir.setReturnValue(true);
    }
}
