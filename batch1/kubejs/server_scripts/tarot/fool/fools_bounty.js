// Food modifier (+20% food & saturation) is native JSON. Golden-apple bonus is scripted.
global.TarotFool.register('food',function(p,e){
  var A=global.TarotFool;
  if(!A.ready(p,3)||!e.item||e.item.id!=='minecraft:golden_apple')return;
  A.effect(p,'speed',100,0);
});
