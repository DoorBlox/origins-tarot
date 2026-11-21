// Below 8 HP auto-escape: Speed II for 60 ticks + decoy, CD 600t.
global.TarotFool.register('tick',function(p,ticks){
  var A=global.TarotFool;if(ticks%20!==0||!A.ready(p,4))return;
  if(Number(p.health)>=8||!A.cooldown(p,'tricksters_escape',600))return;
  A.effect(p,'speed',60,1);A.decoy(p,100);
});
