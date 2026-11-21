package club.tarot.arcane.mixin;

import club.tarot.arcane.ArcaneSave;
import club.tarot.arcane.WorldJusticeAbilities;
import club.tarot.arcane.HermitChariotAbilities;
import net.minecraft.block.BlockState;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
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
    @ModifyVariable(method="addExperience",at=@At("HEAD"),argsOnly=true,index=1)
    private int tarot$xpBonus(int experience) {
        if((Object)this instanceof ServerPlayerEntity player)
            return HermitChariotAbilities.modifyXp(player,experience);
        return experience;
    }

    @Inject(method="getBlockBreakingSpeed",at=@At("RETURN"),cancellable=true)
    private void tarot$investigationSpeed(BlockState state,CallbackInfoReturnable<Float> cir) {
        if((Object)this instanceof ServerPlayerEntity player)
            cir.setReturnValue(cir.getReturnValue()*HermitChariotAbilities.breakMultiplier(player));
    }

    @Inject(method="tick",at=@At("HEAD"))
    private void tarot$movementRestriction(CallbackInfo ci) {
        if((Object)this instanceof ServerPlayerEntity player &&
            !WorldJusticeAbilities.canSprint(player))player.setSprinting(false);
    }
    @ModifyVariable(method = "addExhaustion", at = @At("HEAD"), argsOnly = true)
    private float tarot$spiritualExpenditure(float amount) {
        if (!((Object)this instanceof ServerPlayerEntity)) return amount;
        ServerPlayerEntity player=(ServerPlayerEntity)(Object)this;
        ArcaneSave.Record record=ArcaneSave.get(player.getServer()).getPlayer(player.getUuid());
        if(record==null || !record.originValid || !record.profile.identityActive("fool")) return amount;
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
