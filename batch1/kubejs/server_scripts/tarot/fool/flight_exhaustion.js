// Rev 2 identity: +25% sprint and Elytra exhaustion. Origins adds the sprint modifier.
// Vanilla Elytra has no intrinsic exhaustion, so we define 0.02/tick flight cost + 25% = 0.025/tick.
// APPROX: This adds a 0.005/tick surcharge to an explicit 0.02/tick baseline, not vanilla Elytra.
global.TarotFool.register('tick',function(p,ticks){
  if(ticks%5!==0)return;
  var s=global.TarotBatch1Slots.get(p);if(!s||s.primary!=='tarot:fool')return;
  try{
    if(p.isFallFlying&&p.isFallFlying()){
      // 5 ticks of the defined baseline and its 25% surcharge, charged together.
      p.causeFoodExhaustion(5*0.025);
    }
  }catch(err){
    // VERIFY METHOD: LivingEntity.causeFoodExhaustion on 1802 Fabric player wrappers.
    try{if(p.fallFlying)p.addExhaustion(5*0.025);}catch(ignore){}
  }
});
