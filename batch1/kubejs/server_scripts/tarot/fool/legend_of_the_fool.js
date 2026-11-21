// Rev 2 700t duration, 18000t CD (12000t below 6HP), limited creative flight.
function endFoolLegend(p,dead){
  var data=p.persistentData,end=data.getLong('tc_legend_until');if(end===0)return;
  data.putLong('tc_legend_until',0);
  try{p.abilities.mayfly=data.getBoolean('tc_legend_mayfly');p.abilities.flying=false;p.onUpdateAbilities();}catch(ignore){}
  if(dead)return; // Expiring after death must not rewind or heal.
  var original=JSON.parse(String(data.getString('tc_legend_position')||'{}'));
  if(typeof original.x==='number'&&typeof original.y==='number'&&typeof original.z==='number')
    global.TarotFool.run(p,'tp @s '+original.x+' '+original.y+' '+original.z);
  try{p.setHealth(20);p.foodLevel=20;p.saturation=20;}catch(ignore){p.health=20;}
  global.TarotFool.effect(p,'regeneration',200,1);global.TarotFool.effect(p,'speed',200,1);
}
global.TarotFool.registerCast('legend_of_the_fool',0,'primary',function(p){
  var A=global.TarotFool,ticks=Number(p.health)<6?12000:18000;
  if(!A.cooldown(p,'legend_of_the_fool',ticks))return false;
  var d=p.persistentData;
  d.putLong('tc_legend_until',Date.now()+700*50);
  d.putString('tc_legend_position',JSON.stringify({x:p.x,y:p.y,z:p.z}));
  try{d.putBoolean('tc_legend_mayfly',p.abilities.mayfly);p.abilities.mayfly=true;p.onUpdateAbilities();}catch(ignore){}
  A.effect(p,'fire_resistance',700,0);
  A.effect(p,'resistance',700,3); // APPROX: Resistance IV is 80%, not precise 75%.
  A.effect(p,'strength',700,0);   // APPROX: Strength I is not exactly +50% final damage.
  A.decoy(p,100);return true;
});
global.TarotFool.register('tick',function(p,ticks){
  var end=p.persistentData.getLong('tc_legend_until');
  if(end===0)return;
  if(Date.now()>=end){endFoolLegend(p,false);return;}
  if(ticks%100===0)global.TarotFool.decoy(p,100);
});
global.TarotFool.register('hurt',function(p,e){
  if(p.persistentData.getLong('tc_legend_until')<=Date.now())return;
  if(String(e.source&&e.source.type).indexOf('fall')!==-1){if(e.cancel)e.cancel();}
});
global.TarotFool.register('hit',function(p,e,target){
  var A=global.TarotFool;
  if(p.persistentData.getLong('tc_legend_until')<=Date.now()||!A.enemy(p,target))return;
  try{e.damage=Number(e.damage)*1.5;}catch(ignore){}
  A.effect(target,'slowness',80,1);A.effect(target,'weakness',80,0);
});
global.TarotFool.register('death',function(p,e,victim){
  // APPROX: Loot duplication is not safely available on the generic death event.
  // The extra loot requires a registered loot-table hook; not simulated by item duping.
  if(p.persistentData.getLong('tc_legend_until')<=Date.now())return;
  if(Math.pow(p.x-victim.x,2)+Math.pow(p.z-victim.z,2)>100)return;
  // One extra mob XP (not loot) is intentionally NOT claimed as Rev 2's double loot.
});
global.TarotFool.register('dead',function(p){endFoolLegend(p,true);});
