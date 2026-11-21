// HOOK: entity.hurt cancellable in KubeJS 1802; verify exact timing before trusting lethal saves.
// On lethal hit: cancel, relocate 12 backward if the destination is air, restore 20 HP, invis+speed II.
global.TarotFool.register('hurt',function(p,e,attacker){
  var A=global.TarotFool;
  if(!A.ready(p,1)||Number(p.health)>Number(e.damage||e.amount)||!A.offCooldown(p,'history_substitution'))return;
  if(!e.cancel)return; // Fail-closed when damage cannot be cancelled.
  if(!A.cooldown(p,'history_substitution',7200))return;
  e.cancel();
  A.run(p,'execute if block ^ ^ ^-12 minecraft:air run tp @s ^ ^ ^-12');
  try{p.setHealth(20);}catch(ignore){p.health=20;}
  A.effect(p,'invisibility',60,0);A.effect(p,'speed',60,1);
});
