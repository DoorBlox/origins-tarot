// APPROX: Fabric 1802 lacks a verified LivingChangeTargetEvent; sample mob target on 10t ticks.
// Only mob-vs-mob retargeting is simulated. Human player controls are never hijacked.
global.TarotFool.register('tick',function(p,ticks){
  var A=global.TarotFool;if(ticks%10!==0||!A.ready(p,8)||!A.offCooldown(p,'tricksters_favor'))return;
  var mobs=A.enemies(p,6),me=p.minecraftPlayer||p;
  for(var i=0;i<mobs.length;i++){
    var mob=mobs[i];if(A.player(mob)||!mob.getTarget||mob.getTarget()!==me)continue;
    if(Math.random()>=0.10)continue;
    var others=mobs.filter(function(x){return x!==mob&&!A.player(x);});
    if(!others.length)continue;
    if(A.cooldown(p,'tricksters_favor',200)){mob.setTarget(others[0]);break;}
  }
});
