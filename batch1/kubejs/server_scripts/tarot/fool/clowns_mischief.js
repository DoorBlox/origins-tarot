// Tagged [D] in Rev 2, but KubeJS applies the team-aware hit filter to protect allies.
global.TarotFool.register('hurt',function(p,e,attacker){
  var A=global.TarotFool;
  if(!A.ready(p,9)||!A.enemy(p,attacker)||Math.random()>=0.20)return;
  if(A.cooldown(p,'clowns_mischief',100))A.effect(attacker,'blindness',20,0);
});
