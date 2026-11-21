package club.tarot.arcane;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v1.CommandRegistrationCallback;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.entity.event.v1.ServerEntityWorldChangeEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.text.LiteralText;
import net.minecraft.util.Formatting;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.List;

import static net.minecraft.server.command.CommandManager.argument;
import static net.minecraft.server.command.CommandManager.literal;

/** Native no-KubeJS command, persistence, and Apoli power-source bridge. */
public final class ArcaneMod implements ModInitializer {
    public static final Logger LOG = LoggerFactory.getLogger("tarot-arcane-v2");
    private static final String SOURCE = "tarot_slot";

    @Override public void onInitialize() {
        CommandRegistrationCallback.EVENT.register((dispatcher, dedicated) -> dispatcher.register(
            literal("tarot")
                .then(literal("slots").executes(c -> withPlayer(c, (p,s,r) -> { show(p,r); return 1; })))
                .then(literal("slot")
                    .then(literal("auto").executes(c -> alter(c, r -> r.profile.auto())))
                    .then(literal("swap")
                        .then(argument("a",IntegerArgumentType.integer(1))
                            .then(argument("b",IntegerArgumentType.integer(1))
                                .executes(c -> alter(c,r -> r.profile.swap(IntegerArgumentType.getInteger(c,"a"), IntegerArgumentType.getInteger(c,"b")))))))
                    .then(argument("index",IntegerArgumentType.integer(1))
                        .then(literal("clear").executes(c -> alter(c, r -> r.profile.clearSlot(IntegerArgumentType.getInteger(c,"index")))))
                        .then(argument("pathway",StringArgumentType.word())
                            .then(argument("sequence",IntegerArgumentType.integer(0,9))
                                .executes(c -> alter(c,r -> r.profile.setSlot(
                                    IntegerArgumentType.getInteger(c,"index"),
                                    normalize(StringArgumentType.getString(c,"pathway")),
                                    IntegerArgumentType.getInteger(c,"sequence"))))))))
                .then(literal("reset").executes(c -> alter(c,r -> r.profile.reset())))
                .then(literal("cast").then(argument("ability",StringArgumentType.word())
                    .executes(c -> withPlayer(c,(p,s,r) -> FoolAbilities.cast(p,s,r,StringArgumentType.getString(c,"ability"))))))
                .then(literal("debug").requires(src -> src.hasPermissionLevel(2))
                    .then(literal("sequence").then(argument("level",IntegerArgumentType.integer(0,9))
                        .executes(c -> withPlayer(c,(p,s,r) -> onSequenceChange(p,s,r,IntegerArgumentType.getInteger(c,"level"))))))
        )));
        ServerPlayConnectionEvents.JOIN.register((handler,sender,server) ->
            server.execute(() -> enrollAndRefresh(handler.getPlayer())));
        ServerPlayerEvents.AFTER_RESPAWN.register((oldPlayer,newPlayer,alive) ->
            enrollAndRefresh(newPlayer));
        ServerEntityWorldChangeEvents.AFTER_PLAYER_CHANGE_WORLD.register((player,from,to) ->
            enrollAndRefresh(player));
        ServerTickEvents.END_SERVER_TICK.register(server -> {
            if (server.getTicks() % 20 != 0) return;
            for (ServerPlayerEntity player : server.getPlayerManager().getPlayerList()) {
                ArcaneSave state = ArcaneSave.get(server);
                ArcaneSave.Record record = state.getPlayer(player.getUuid());
                // Origins choice can occur after JOIN; discover the selected Arcana without KubeJS.
                if (record == null) {
                    if (server.getTicks() % 100 == 0) enrollAndRefresh(player);
                    continue;
                }
                FoolAbilities.tick(player,state,record);
            }
        });
        FoolAbilities.register();
        LOG.info("Arcane V2 native runtime initialized (KubeJS not required)");
    }

    public static String normalize(String name) {
        return name.startsWith("tarot:") ? name.substring(6) : name;
    }
    static ArcaneSave.Record profile(ServerPlayerEntity player) {
        return ArcaneSave.get(player.getServer()).getPlayer(player.getUuid());
    }
    static void info(ServerPlayerEntity player, String msg) {
        player.sendMessage(new LiteralText("[Tarot] " + msg).formatted(Formatting.AQUA), false);
    }
    static void error(ServerPlayerEntity player, String msg) {
        player.sendMessage(new LiteralText("[Tarot] " + msg).formatted(Formatting.RED), false);
    }
    @FunctionalInterface private interface CommandWork {
        int run(ServerPlayerEntity player, ArcaneSave state, ArcaneSave.Record record);
    }
    private static int withPlayer(CommandContext<ServerCommandSource> c, CommandWork work) {
        try {
            ServerPlayerEntity p = c.getSource().getPlayer();
            ArcaneSave state=ArcaneSave.get(p.getServer());
            ArcaneSave.Record r=state.getPlayer(p.getUuid());
            if(r == null) { error(p,"Choose a Tarot Arcana first."); return 0; }
            return work.run(p,state,r);
        } catch (com.mojang.brigadier.exceptions.CommandSyntaxException e) { return 0; }
    }
    @FunctionalInterface private interface Mutation { void apply(ArcaneSave.Record record); }
    private static int alter(CommandContext<ServerCommandSource> c, Mutation action) {
        return withPlayer(c,(p,s,r) -> {
            try {
                action.apply(r);
                s.markDirty();
                refreshSlots(p,r);
                show(p,r);
                return 1;
            } catch (IllegalArgumentException | IllegalStateException ex) {
                error(p,ex.getMessage()); return 0;
            }
        });
    }
    private static int onSequenceChange(ServerPlayerEntity p, ArcaneSave s, ArcaneSave.Record r, int next) {
        int old = r.profile.sequence();
        try {
            r.profile.onSequenceChange(next);
            s.markDirty();
            refreshSlots(p,r);
            if (old >= 5 && next <= 4 && next > 1)
                info(p,"Second pathway unlocked: "+r.profile.secondary()+". Configure up to "+r.profile.maxSlots()+" slots.");
            if (old > 1 && next <= 1)
                info(p,"Your two pathways have merged. Resonance achieved: "+r.profile.resonance()+".");
            info(p,"Sequence "+old+" -> "+next+"; mode "+r.profile.mode()+".");
            return 1;
        } catch (IllegalArgumentException ex) { error(p,ex.getMessage()); return 0; }
    }
    /** External advancement integrations call this from the server thread after validated ascension. */
    public static boolean onSequenceChange(ServerPlayerEntity player, int oldSeq, int newSeq) {
        ArcaneSave state=ArcaneSave.get(player.getServer());
        ArcaneSave.Record record=state.getPlayer(player.getUuid());
        if(record==null || record.profile.sequence()!=oldSeq) return false;
        return onSequenceChange(player,state,record,newSeq)>0;
    }
    static void run(ServerPlayerEntity player, String command) {
        MinecraftServer server=player.getServer();
        server.getCommandManager().execute(server.getCommandSource().withLevel(4),command);
    }
    /** Never use wildcard powers, or clear powers from other mods. */
    static void refreshSlots(ServerPlayerEntity p, ArcaneSave.Record r) {
        String selector=p.getUuidAsString();
        run(p, "power revokeall "+selector+" "+SOURCE);
        SlotModel.Profile profile=r.profile;
        if ("resonance".equals(profile.mode())) {
            // Resonance grant is guarded by implementation availability: no phantom powers.
            for (int seq=9;seq>=0;seq--)
                for (String id : AbilityRegistry.forSequence(profile.resonance(),seq))
                    run(p,"power grant "+selector+" "+id+" "+SOURCE);
        } else for (SlotModel.Choice choice : profile.slots()) {
            if (choice==null) continue;
            for (String id:AbilityRegistry.forSequence(choice.pathway,choice.sequence))
                run(p,"power grant "+selector+" "+id+" "+SOURCE);
        }
    }
    static void enrollAndRefresh(ServerPlayerEntity p) {
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record existing=state.getPlayer(p.getUuid());
        if(existing!=null) {
            // Do not grant powers if player no longer holds the registered origin.
            int holds=originHas(p,existing.profile.primary());
            if (holds > 0) refreshSlots(p,existing);
            else error(p,"Registered Arcana mismatch; slot powers suspended until origin restored.");
            return;
        }
        for(String card:SlotModel.PAIRS.keySet()) if(originHas(p,card)>0) {
            ArcaneSave.Record r=state.enroll(p.getUuid(),card);
            refreshSlots(p,r); info(p,"Enrolled as "+card+" at Sequence 9.");
            return;
        }
    }
    private static int originHas(ServerPlayerEntity p,String card) {
        String selector=p.getUuidAsString();
        return p.getServer().getCommandManager().execute(p.getServer().getCommandSource().withLevel(4),
            "origin has origin "+selector+" origins:origin tarot:"+card);
    }
    private static void show(ServerPlayerEntity p,ArcaneSave.Record r) {
        SlotModel.Profile model=r.profile;
        int filled=(int)model.slots().stream().filter(c->c!=null).count();
        info(p,model.mode().toUpperCase()+" / Sequence "+model.sequence()
            +" / "+filled+"/"+model.maxSlots()+" slots");
        if(model.mode().equals("resonance")) { info(p,"Resonance: "+model.resonance()+" (Sequences 9-0)"); return; }
        int i=1;
        for(SlotModel.Choice slot:model.slots()) info(p,"["+i+++"] "+(slot==null?"(empty)":slot.toString()));
    }
}
