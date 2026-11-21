package club.tarot.arcane.mixin;

import club.tarot.arcane.ArcaneSave;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.FoodComponent;
import net.minecraft.item.ItemStack;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.world.World;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Rev 2 spiritual expenditure and Fools' Bounty, no KubeJS. */
@Mixin(PlayerEntity.class)
public abstract class PlayerEntityMixin {
    @ModifyVariable(method = "addExhaustion", at = @At("HEAD"), argsOnly = true)
    private float tarot$spiritualExpenditure(float amount) {
        if (!((Object)this instanceof ServerPlayerEntity)) return amount;
        ServerPlayerEntity player=(ServerPlayerEntity)(Object)this;
        ArcaneSave.Record record=ArcaneSave.get(player.getServer()).getPlayer(player.getUuid());
        if(record==null || !(record.profile.primary().equals("fool")
            || record.profile.active("paper_martyr",9))) return amount;
        // Approx: while sprinting, other exhaustion sources share this multiplier.
        return player.isSprinting() || player.isFallFlying() ? amount * 1.25f : amount;
    }

    @Inject(method = "eatFood", at = @At("TAIL"))
    private void tarot$foolsBounty(World world, ItemStack consumed,
        CallbackInfoReturnable<ItemStack> cir) {
        if(world.isClient || !((Object)this instanceof ServerPlayerEntity)) return;
        ServerPlayerEntity player=(ServerPlayerEntity)(Object)this;
        ArcaneSave state=ArcaneSave.get(player.getServer());
        ArcaneSave.Record r=state.getPlayer(player.getUuid());
        if(r==null || !r.profile.active("fool",3)) return;
        FoodComponent food=consumed.getItem().getFoodComponent();
        if(food!=null) {
            r.foodRemainder += food.getHunger() * 0.20f;
            int extra=(int)r.foodRemainder;
            if(extra>0) {
                player.getHungerManager().add(extra,food.getSaturationModifier());
                r.foodRemainder-=extra;
            }
        }
        if(consumed.isOf(net.minecraft.item.Items.GOLDEN_APPLE))
            player.addStatusEffect(new net.minecraft.entity.effect.StatusEffectInstance(
                net.minecraft.entity.effect.StatusEffects.SPEED,100,0));
        state.markDirty();
    }
}
