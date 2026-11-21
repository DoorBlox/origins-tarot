"""Rev2 individual batch: nine additional source-traced combat/utility powers."""
from ..powers import power, apply, mod
from .shared import active, periodic, effect, mobs, combined, cmd


def register(add):
    hostile={"type":"origins:in_tag","tag":"tarot:hostile"}
    undead={"type":"origins:in_tag","tag":"tarot:undead"}
    add("chariot",5,"Reap",
        active("Reap","Secondary grants Strength I for 100 ticks, 600-tick cooldown.",
               apply("strength",100),600),
        "partial","Rev2 grants exactly +30% for the next melee strike within 100 ticks; a timed Strength I potion is not identical and may buff multiple hits")
    add("strength",5,"Bulwark",
        active("Bulwark","Secondary grants Resistance II and extreme Slowness for 100 ticks.",
               combined(apply("resistance",100,1),
                        apply("slowness",100,5)),1200),
        "partial","Resistance II reduces damage by 40% rather than exactly 30%; Slowness VI does not fully immobilize; 1200t cooldown is a conservative default absent source duration")
    add("death",6,"Guide",
        power("Guide","Killing an undead mob restores 1 HP.",
              "origins:self_action_on_kill",
              bientity_condition={"type":"origins:target_condition",
                                  "condition":undead},
              entity_action={"type":"origins:heal","amount":1}),
        "partial","Requires any nearby undead death within eight blocks; this only detects kills by the caster")
    add("judgement",6,"Verdict",
        power("Verdict","After a kill, slow tagged hostile mobs within four blocks for 40 ticks.",
              "origins:self_action_on_kill",cooldown=400,
              entity_action=effect(mobs(4),"slowness",40)),
        "partial","Nearby enemy players must also be affected, but cannot be safely distinguished from teammates")
    add("death",9,"Grave Whisper",
        power("Grave Whisper","10% chance after killing an undead mob to receive one rotten flesh.",
              "origins:self_action_on_kill",
              bientity_condition={"type":"origins:target_condition",
                                  "condition":undead},
              entity_action={"type":"origins:chance","chance":0.10,
                             "action":cmd("give @s minecraft:rotten_flesh 1")}),
        "partial","Source requires an extra 10% of the undead mob's actual loot; fixed rotten flesh is a non-equivalent fallback")
    add("strength",2,"Twilight Blade",
        power("Twilight Blade","Every 3600t, a hostile melee hit applies Slowness II and Weakness I for 100t.",
              "origins:target_action_on_hit",cooldown=3600,
              target_condition=hostile,
              entity_action=combined(apply("slowness",100,1),
                                     apply("weakness",100))),
        "partial","Rev2 applies only to the player's chosen next melee hit, including enemy players; trigger is automatic and only mob-targeted")
    add("moon",9,"Sanguine Resilience",
        power("Sanguine Resilience","At night, on damage, 10% chance to clear Wither.",
              "origins:self_action_when_hit",cooldown=1,
              condition={"type":"origins:daytime","inverted":True},
              entity_action={"type":"origins:chance","chance":0.10,
                             "action":{"type":"origins:clear_effect",
                                       "effect":"minecraft:wither"}}),
        "partial","Rev2 says 10% Wither resistance at night; this only removes existing Wither on actual damage events")
    add("lovers",1,"Nature's Step",
        active("Nature's Step","Primary heals self four HP and gives Regeneration I for 200t.",
               combined({"type":"origins:heal","amount":4},
                        apply("regeneration",200)),2400,primary=True),
        "partial","Walking through leaves for 300t and healing same-team allies within eight blocks are omitted")
    add("sun",2,"Sanctify",
        active("Sanctify","Secondary applies Wither I to undead mobs within five blocks.",
               effect(mobs(5,"undead"),"wither",600),3600),
        "partial","Source says consecrated zone persists 600t and deals exact 2 damage/sec; a 600t Wither I effect is not equivalent, with no terrain sanctification")
