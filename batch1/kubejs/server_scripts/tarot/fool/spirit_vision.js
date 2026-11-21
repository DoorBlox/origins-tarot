// Native active_self dispatches V to this handler. 10-block sphere, 40t Glow, CD 100t.
global.TarotFool.registerCast('spirit_vision',9,'secondary',function(p){
  var A=global.TarotFool;
  if(!(p.isCrouching&&p.isCrouching()) && !p.crouching){p.tell('[Tarot] Sneak to use Spirit Vision.');return false;}
  if(!A.cooldown(p,'spirit_vision',100))return false;
  var targets=A.nearby(p,10);targets.push(p);
  for(var i=0;i<targets.length;i++)A.effect(targets[i],'glowing',40,0);
  return true;
});
