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
                .then(literal("cast").requires(src -> src.hasPermissionLevel(2)).then(argument("ability",StringArgumentType.word())
                    .executes(c -> withPlayer(c,(p,s,r) -> cast(p,s,r,StringArgumentType.getString(c,"ability"))))))
                .then(literal("debug").requires(src -> src.hasPermissionLevel(2))
                    .then(literal("sequence").then(argument("level",IntegerArgumentType.integer(0,9))
                        .executes(c -> withPlayer(c,(p,s,r) -> onSequenceChange(p,s,r,IntegerArgumentType.getInteger(c,"level"))))))
        )));
        // Separate command registration merges additional children into /tarot.
        CommandRegistrationCallback.EVENT.register((dispatcher, dedicated) -> {
            dispatcher.register(literal("tarot")
                .then(literal("bind")
                    .then(argument("binding",StringArgumentType.word())
                        .then(argument("ability",StringArgumentType.word())
                            .executes(c -> withPlayer(c,(p,s,r) -> bind(p,s,r,
                                StringArgumentType.getString(c,"binding"),
                                StringArgumentType.getString(c,"ability")))))))
                .then(literal("key")
                    .then(argument("binding",StringArgumentType.word())
                        .executes(c -> withPlayer(c,(p,s,r) -> activateKey(p,s,r,
                            StringArgumentType.getString(c,"binding")))))));
            // Origins marker callback can signal selection immediately, even before JOIN.
            dispatcher.register(literal("tarot")
                .then(literal("origin_ready").executes(c -> {
                    try { enrollAndRefresh(c.getSource().getPlayer()); return 1; }
                    catch(com.mojang.brigadier.exceptions.CommandSyntaxException ignored) { return 0; }
                })));
        });
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
                if(originHas(player,record.profile.primary())<=0) {
                    revokeIfMismatched(player,record);
                    continue;
                }
                record.originValid=true;
                record.originChecked=true;
                FoolAbilities.tick(player,state,record);
                HangedAbilities.tick(player,state,record);
                WorldJusticeAbilities.tick(player,state,record);
            }
        });
        FoolAbilities.register();
        FoolLegend.register();
        WorldJusticeAbilities.register();
        ServerPlayConnectionEvents.DISCONNECT.register((handler,server) ->
            server.execute(() -> {
                FoolLegend.stopOnDisconnect(handler.getPlayer());
                HangedAbilities.stopOnDisconnect(handler.getPlayer());
                PaperMartyr.stopOnDisconnect(handler.getPlayer());
                WorldJusticeAbilities.stopOnDisconnect(handler.getPlayer());
            }));
        LOG.info("Arcane V2 native runtime initialized (KubeJS not required)");
    }

    public static String normalize(String name) {
        return name.startsWith("tarot:") ? name.substring(6) : name;
    }
    static ArcaneSave.Record profile(ServerPlayerEntity player) {
        ArcaneSave.Record r=ArcaneSave.get(player.getServer()).getPlayer(player.getUuid());
        return r!=null && r.originValid?r:null;
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
            if(originHas(p,r.profile.primary())<=0) {
                revokeIfMismatched(p,r);
                error(p,"Registered Arcana mismatch; Tarot slot powers disabled.");
                return 0;
            }
            r.originValid=true;
            r.originChecked=true;
            return work.run(p,state,r);
        } catch (com.mojang.brigadier.exceptions.CommandSyntaxException e) { return 0; }
    }
    private static int bind(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,
                            String binding,String ability) {
        binding=binding.toLowerCase(java.util.Locale.ROOT);
        ability=ability.toLowerCase(java.util.Locale.ROOT);
        if(!supportsBinding(binding,ability)
            || !AbilityRegistry.isActive(r.profile,ability)) {
            error(p,"Ability not unlocked, unsupported, or wrong key. Use /tarot slots.");
            return 0;
        }
        if("primary".equals(binding)) r.primaryBinding=ability;
        else if("secondary".equals(binding)) r.secondaryBinding=ability;
        else { error(p,"Select primary or secondary."); return 0; }
        state.markDirty();
        info(p,"Bound "+binding+" to "+ability+".");
        return 1;
    }
    private static int activateKey(ServerPlayerEntity p,ArcaneSave state,
                                   ArcaneSave.Record r,String binding) {
        String ability;
        if("primary".equals(binding)) ability=r.primaryBinding;
        else if("secondary".equals(binding)) ability=r.secondaryBinding;
        else { error(p,"Unknown Tarot key."); return 0; }
        if(!supportsBinding(binding,ability)
            || !AbilityRegistry.isActive(r.profile,ability)) {
            error(p,"No active "+binding+" skill. Use /tarot bind "+binding+" <ability>.");
            return 0;
        }
        return cast(p,state,r,ability);
    }
    private static boolean supportsBinding(String binding,String ability) {
        if(FoolAbilities.supportsBinding(binding,ability))return true;
        if("primary".equals(binding))
            return "the_paper_martyr".equals(ability) || "weight_of_sin_made_manifest".equals(ability)
                || "air_cannon".equals(ability) || "the_perfect_prey".equals(ability)
                || "authors_edit".equals(ability) || "the_mindscape".equals(ability)
                || "the_marked_verdict".equals(ability);
        return "secondary".equals(binding) && (
            "paper_dagger".equals(ability) || "paper_sentence".equals(ability)
            || "small_miracle".equals(ability) || "mystery_step".equals(ability)
            || "suggestion".equals(ability) || "discern".equals(ability)
            || "puppets_sentence".equals(ability) || "silent_witness".equals(ability)
            || "burdened_beginning".equals(ability) || "suffering_sight".equals(ability)
            || "borrowed_sacrifice".equals(ability) || "gathering_of_martyrs".equals(ability));
    }
    private static int cast(ServerPlayerEntity p,ArcaneSave state,ArcaneSave.Record r,String ability) {
        if(AbilityRegistry.isActive(r.profile,ability)) {
            if(WorldJusticeAbilities.cast(p,state,r,ability)) {
                info(p,"Cast "+ability);return 1;
            }
            if(PaperMartyr.cast(p,state,r,ability)>0) {
                info(p,"Cast "+ability);return 1;
            }
            if(HangedAbilities.cast(p,state,r,ability)) {
                info(p,"Cast "+ability);return 1;
            }
        }
        return FoolAbilities.cast(p,state,r,ability);
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
            run(p,"power revokeall "+selector+" tarot_secondary_identity");
            String secondaryIdentity=switch(profile.primary()){
                case "fool" -> "tarot:hanged_man/identity_weight_of_sin";
                case "hanged_man" -> "tarot:fool/identity_spiritual_expenditure";
                case "world" -> "tarot:justice/identity_compassionate_restraint";
                case "justice" -> "tarot:world/identity_terrifying_reputation";
                default -> null;
            };
            if(secondaryIdentity!=null)
                run(p,"power grant "+selector+" "+secondaryIdentity+" tarot_secondary_identity");
            // Resonance grant is guarded by implementation availability: no phantom powers.
            for (int seq=9;seq>=0;seq--)
                for (String id : AbilityRegistry.forSequence(profile.resonance(),seq))
                    run(p,"power grant "+selector+" "+id+" "+SOURCE);
        } else for (SlotModel.Choice choice : profile.slots()) {
            if (choice==null) continue;
            for (String id:AbilityRegistry.forSequence(choice.pathway,choice.sequence))
                run(p,"power grant "+selector+" "+id+" "+SOURCE);
        }
        // Clear stale input bindings when a Sequence has been removed.
        if(!AbilityRegistry.isActive(profile,r.primaryBinding)) {
            String[] priorities={"the_marked_verdict","the_mindscape","the_perfect_prey",
                "the_paper_martyr","air_cannon","authors_edit",
                "weight_of_sin_made_manifest","full_faceless_disguise"};
            r.primaryBinding="";
            for(String candidate:priorities)
                if(AbilityRegistry.isActive(profile,candidate) && supportsBinding("primary",candidate)) {
                    r.primaryBinding=candidate;break;
                }
        }
        if(!AbilityRegistry.isActive(profile,r.secondaryBinding)) {
            String[] priorities={"puppets_sentence","paper_sentence","suffering_sight",
                "suggestion","paper_dagger","spirit_vision","borrowed_face","discern"};
            r.secondaryBinding="";
            for(String candidate:priorities)
                if(AbilityRegistry.isActive(profile,candidate) && supportsBinding("secondary",candidate)) {
                    r.secondaryBinding=candidate;break;
                }
        }
        ArcaneSave.get(p.getServer()).markDirty();
    }
    private static void grantInputKeys(ServerPlayerEntity p) {
        String uuid=p.getUuidAsString();
        run(p,"power grant "+uuid+" tarot:meta/primary_key tarot_input");
        run(p,"power grant "+uuid+" tarot:meta/secondary_key tarot_input");
    }
    static void enrollAndRefresh(ServerPlayerEntity p) {
        FoolLegend.recoverStaleFlight(p);
        ArcaneSave state=ArcaneSave.get(p.getServer());
        ArcaneSave.Record existing=state.getPlayer(p.getUuid());
        if(existing!=null) {
            // Do not grant powers if player no longer holds the registered origin.
            int holds=originHas(p,existing.profile.primary());
            if (holds > 0) {
                existing.originValid=true;
                existing.originChecked=true;
                grantInputKeys(p); refreshSlots(p,existing);
            } else {
                revokeIfMismatched(p,existing);
                error(p,"Registered Arcana mismatch; slot powers suspended until origin restored.");
            }
            return;
        }
        for(String card:SlotModel.PAIRS.keySet()) if(originHas(p,card)>0) {
            ArcaneSave.Record r=state.enroll(p.getUuid(),card);
            r.originValid=true;
            r.originChecked=true;
            grantInputKeys(p);
            refreshSlots(p,r); info(p,"Enrolled as "+card+" at Sequence 9.");
            return;
        }
    }
    private static void revokeIfMismatched(ServerPlayerEntity p,ArcaneSave.Record r) {
        if(!r.originValid && r.originChecked)return; // avoid spamming after first revocation
        r.originValid=false;
        r.originChecked=true;
        FoolLegend.stopOnDisconnect(p);
        HangedAbilities.stopOnDisconnect(p);
        PaperMartyr.stopOnDisconnect(p);
        WorldJusticeAbilities.stopOnDisconnect(p);
        run(p,"power revokeall "+p.getUuidAsString()+" tarot_secondary_identity");
        run(p,"power revokeall "+p.getUuidAsString()+" tarot_input");
        run(p,"power revokeall "+p.getUuidAsString()+" "+SOURCE);
        info(p,"Current Origins selection does not match registered Arcana; powers suspended.");
    }
    private static int originHas(ServerPlayerEntity p,String card) {
        String selector=p.getUuidAsString();
        return p.getServer().getCommandManager().execute(p.getServer().getCommandSource().withLevel(4),
            "origin has origin "+selector+" origins:origin tarot:"+card);
    }
    private static void show(ServerPlayerEntity p,ArcaneSave.Record r) {
        SlotModel.Profile model=r.profile;
        int filled=(int)model.slots().stream().filter(c->c!=null).count();
        if(model.primary().equals("hanged_man") || model.active("hanged_man",9)
            || model.resonance().equals("paper_martyr") && model.mode().equals("resonance"))
            info(p,"Sin: "+String.format(java.util.Locale.ROOT,"%.1f",r.sin)+" HP");
        info(p,model.mode().toUpperCase()+" / Sequence "+model.sequence()
            +" / "+filled+"/"+model.maxSlots()+" slots");
        if(model.mode().equals("resonance")) { info(p,"Resonance: "+model.resonance()+" (Sequences 9-0)"); return; }
        int i=1;
        for(SlotModel.Choice slot:model.slots()) info(p,"["+i+++"] "+(slot==null?"(empty)":slot.toString()));
        info(p,"Keys: primary="+r.primaryBinding+" | secondary="+r.secondaryBinding);
        info(p,"Use /tarot bind <primary|secondary> <ability> to change key bindings.");
    }
}
