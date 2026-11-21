// 25% defensive substitution, CD 400t; safe horizontal teleport is approximated by air check.
global.TarotFool.register('hurt',function(p,e,attacker){
  var A=global.TarotFool;
  if(!A.ready(p,7)||!A.enemy(p,attacker)||Math.random()>=0.25)return;
  if(!A.cooldown(p,'stage_magician',400))return;
  A.run(p,'execute if block ^ ^ ^-3 minecraft:air run tp @s ^ ^ ^-3');
  A.decoy(p,100);
});
