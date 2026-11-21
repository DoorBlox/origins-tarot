// Primary action exactly distinguishes mob (80t) and enemy player (40t); target team-filtered.
global.TarotFool.registerCast('puppet_string',5,'secondary',function(p){
  var A=global.TarotFool;
  if(!(p.isCrouching&&p.isCrouching())&&!p.crouching){p.tell('[Tarot] Sneak to use Puppet String.');return false;}
  var targets=A.enemies(p,8);if(!targets.length){p.tell('[Tarot] No hostile target.');return false;}
  targets.sort(function(a,b){return Math.pow(a.x-p.x,2)+Math.pow(a.z-p.z,2)-Math.pow(b.x-p.x,2)-Math.pow(b.z-p.z,2);});
  if(!A.cooldown(p,'puppet_string',400))return false;
  var t=targets[0],isPlayer=A.player(t);
  A.effect(t,'slowness',isPlayer?40:80,1);
  if(isPlayer){
    t.persistentData.putLong('tc_fool_cannot_sprint_until',Date.now()+40*50);
    p.tell('[Tarot] Puppet String target position: '+Math.floor(t.x)+' / '+Math.floor(t.y)+' / '+Math.floor(t.z));
  }else{
    // APPROX: Weakness I roughly halves many mob attacks, not exact next-attack 50%.
    A.effect(t,'weakness',80,0);
  }
  return true;
});
global.TarotFool.register('tick',function(p){
  if(p.persistentData.getLong('tc_fool_cannot_sprint_until')>Date.now())
    try{p.setSprinting(false);}catch(ignore){}
});
