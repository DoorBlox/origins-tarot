// KubeJS LivingEntity radius scan every 40t; hostile mobs >=3 OR enemy players >=1.
global.TarotFool.register('tick',function(p,ticks){
  var A=global.TarotFool;if(ticks%40!==0||!A.ready(p,9))return;
  var enemies=A.enemies(p,8),mobs=0,players=0;
  for(var i=0;i<enemies.length;i++)
    if(A.player(enemies[i]))players++;else mobs++;
  if(mobs>=3||players>=1)A.effect(p,'nausea',100,0);
});
