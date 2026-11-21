package club.tarot.arcane.mixin;

import club.tarot.arcane.HangedAbilities;
import net.minecraft.item.ItemStack;
import net.minecraft.item.PotionItem;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.potion.PotionUtil;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.world.World;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Healing-potion exception to Weight of Sin; detects a finished potion, not an attempted use. */
@Mixin(PotionItem.class)
public abstract class PotionItemMixin {
    @Inject(method="finishUsing",at=@At("TAIL"))
    private void tarot$healingPotion(ItemStack stack,World world,LivingEntity consumer,
                                     CallbackInfoReturnable<ItemStack> cir) {
        if(world.isClient || !(consumer instanceof ServerPlayerEntity player))return;
        if(PotionUtil.getPotionEffects(stack).stream()
            .anyMatch(effect->effect.getEffectType()==StatusEffects.INSTANT_HEALTH))
            HangedAbilities.afterHealingPotion(player);
    }
}
