// APPROX: server cannot replace another player's signed skin/model/name for all clients.
// Instead use invisible gray-fog disguise plus a target identity hint. Exact skin needs client mod.
global.TarotFool.registerCast('full_faceless_disguise',9,'primary',function(p){
  var A=global.TarotFool;if(!A.safe(p)){p.tell('[Tarot] Cannot disguise in combat.');return false;}
  if(!A.cooldown(p,'full_faceless_disguise',6000))return false;
  var duration=2400+Math.floor(Math.random()*481);
  var candidates=p.server.players.filter(function(other){return other.username!==p.username;});
  var target=candidates.length?candidates[Math.floor(Math.random()*candidates.length)]:null;
  p.persistentData.putString('tc_fool_disguise_target',target?String(target.username):'Gray Fog');
  p.persistentData.putLong('tc_fool_disguise_until',Date.now()+duration*50);
  A.effect(p,'invisibility',duration,0);
  p.tell('[Tarot] Faceless camouflage active: '+p.persistentData.getString('tc_fool_disguise_target'));
  return true;
});
function cancelFaceless(p){
  if(p.persistentData.getLong('tc_fool_disguise_until')===0)return;
  p.persistentData.putLong('tc_fool_disguise_until',0);
  try{p.potionEffects.remove('minecraft:invisibility');}catch(ignore){}
}
global.TarotFool.register('hurt',function(p){cancelFaceless(p);});
global.TarotFool.register('hit',function(p){cancelFaceless(p);});
global.TarotFool.register('tick',function(p){
  var n=p.persistentData.getLong('tc_fool_disguise_until');
  if(n>0&&Date.now()>=n)cancelFaceless(p);
});
