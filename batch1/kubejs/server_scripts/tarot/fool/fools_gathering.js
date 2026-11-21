// APPROX: Vex-like NoAI projections follow owner; KubeJS applies 1 HP damage only to enemies.
// Real autonomous flying ally AI and per-minion health/damage attributes require a companion mod.
global.TarotFool.registerCast('fools_gathering',2,'secondary',function(p){
  var A=global.TarotFool;if(!A.cooldown(p,'fools_gathering',6000))return false;
  var tag='tc_fool_owner_'+String(p.username);
  A.run(p,'summon minecraft:vex ~1 ~1 ~ {NoAI:1b,Silent:1b,Invulnerable:1b,Tags:["tc_fool_minion","'+tag+'"]}');
  A.run(p,'summon minecraft:vex ~-1 ~1 ~ {NoAI:1b,Silent:1b,Invulnerable:1b,Tags:["tc_fool_minion","'+tag+'"]}');
  p.persistentData.putLong('tc_fool_minion_until',Date.now()+200*50);return true;
});
global.TarotFool.register('tick',function(p,ticks){
  if(ticks%20!==0)return;var A=global.TarotFool,end=p.persistentData.getLong('tc_fool_minion_until');
  if(end===0)return;
  var tag='tc_fool_owner_'+String(p.username);
  if(Date.now()>=end){A.run(p,'kill @e[type=minecraft:vex,tag='+tag+',distance=..18]');
    p.persistentData.putLong('tc_fool_minion_until',0);return;}
  A.run(p,'tp @e[type=minecraft:vex,tag='+tag+',distance=..18] ~ ~1 ~');
  var enemies=A.enemies(p,10);if(!enemies.length)return;
  for(var i=0;i<2;i++){
    var t=enemies[i%enemies.length],hp=Number(t.health);
    try{t.setHealth(Math.max(0,hp-1));}catch(ignore){}
  }
});
