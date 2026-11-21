// Does NOT prevent lethal damage or teleport, per Rev 2. 25% chance, 6000t cooldown.
global.TarotFool.register('hurt',function(p,e,attacker){
  var A=global.TarotFool;
  if(!A.ready(p,1)||!A.enemy(p,attacker)||Math.random()>=.25)return;
  if(A.cooldown(p,'paper_figurine_substitute',6000)){
    A.decoy(p,100);A.effect(p,'speed',40,1);
  }
});
