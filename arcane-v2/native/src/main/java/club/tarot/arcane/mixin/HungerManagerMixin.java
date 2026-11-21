package club.tarot.arcane.mixin;

import club.tarot.arcane.HangedAbilities;
import net.minecraft.entity.player.HungerManager;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.server.network.ServerPlayerEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Intercept ONLY vanilla hunger-based natural regeneration, not healing potions or spells. */
@Mixin(HungerManager.class)
public abstract class HungerManagerMixin {
    @Redirect(method="update",at=@At(value="INVOKE",
        target="Lnet/minecraft/entity/player/PlayerEntity;heal(F)V"))
    private void tarot$naturalRegen(PlayerEntity player,float hp) {
        if(player instanceof ServerPlayerEntity sp && HangedAbilities.blockNaturalHeal(sp,hp)) return;
        player.heal(hp);
    }
}
