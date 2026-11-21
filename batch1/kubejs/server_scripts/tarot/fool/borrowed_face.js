// APPROX: cannot swap actual skin/model/name server-side; invisible borrowed presence + post-Speed II.
global.TarotFool.registerCast('borrowed_face',6,'secondary',function(p){
  var A=global.TarotFool;if(!A.safe(p)){p.tell('[Tarot] Borrowed Face requires peace.');return false;}
  var nearby=A.nearby(p,20).filter(function(e){return A.player(e)&&e!==p;});
  if(!nearby.length){p.tell('[Tarot] No nearby player to imitate.');return false;}
  if(!A.cooldown(p,'borrowed_face',2400))return false;
  p.persistentData.putLong('tc_fool_borrowed_until',Date.now()+1800*50);
  p.persistentData.putString('tc_fool_borrowed_name',String(nearby[0].username||nearby[0].name));
  A.effect(p,'invisibility',1800,0);p.tell('[Tarot] Borrowed presence: '+p.persistentData.getString('tc_fool_borrowed_name'));return true;
});
global.TarotFool.register('tick',function(p,ticks){
  if(ticks%10!==0)return;var end=p.persistentData.getLong('tc_fool_borrowed_until');
  if(end>0&&Date.now()>=end){p.persistentData.putLong('tc_fool_borrowed_until',0);global.TarotFool.effect(p,'speed',60,1);}
});
