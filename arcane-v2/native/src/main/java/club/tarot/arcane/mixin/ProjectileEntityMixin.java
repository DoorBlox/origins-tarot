package club.tarot.arcane.mixin;

import club.tarot.arcane.MarkedVerdict;
import net.minecraft.entity.projectile.ProjectileEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Homing is applied only to one already-fired projectile while a capstone is active. */
@Mixin(ProjectileEntity.class)
public abstract class ProjectileEntityMixin {
    @Inject(method="tick",at=@At("HEAD"))
    private void tarot$arcaneArrow(CallbackInfo ci) {
        MarkedVerdict.projectileTick((ProjectileEntity)(Object)this);
    }
}
