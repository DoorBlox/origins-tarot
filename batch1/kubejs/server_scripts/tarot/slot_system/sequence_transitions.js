// V3 transition rules. Never switches Origin; the active source is recalculated.
(function(){
  function onSequenceChange(p,oldSeq,newSeq){
    var api=global.TarotBatch1Slots,reg=global.TarotBatch1Registry,s=api.get(p);
    if(!s||s.sequence!==oldSeq||newSeq!==oldSeq-1||newSeq<0)
      return {ok:false,error:'Sequence transition must advance exactly one level.'};
    var n=api.copy(s);
    if(newSeq===1&&!reg.resonanceComplete[n.resonance.substring(6)])
      return {ok:false,error:'Resonance kit not implemented until Batch 2. Advancement safely blocked.'};
    n.sequence=newSeq;n.max_slots=10-newSeq;
    if(newSeq===4){
      n.mode='slot';n.slots=[];
      for(var q=9;q>=5;q--)n.slots.push(api.entry(n.primary,q));
      n.slots.push(api.empty());
    }else if(newSeq===3||newSeq===2){
      n.slots.push(api.empty()); // No automatic fill: choose one sequence.
    }else if(newSeq===1){
      n.mode='resonance';n.slots=[]; // All 10 Resonance kits are granted by source.
    }else if(newSeq>=5){
      n.mode='single';n.slots.push(api.entry(n.primary,newSeq));
    }else if(newSeq===0){
      n.mode='resonance';n.slots=[];
    }
    if(!api.isValid(n))return {ok:false,error:'Transition validation failed.'};
    api.save(p,n);
    var sync=global.TarotBatch1Grants.refreshSlots(p);
    if(!sync.ok){api.save(p,s);global.TarotBatch1Grants.refreshSlots(p);return sync;}
    if(newSeq===4)p.tell('[Tarot] Second pathway registered. Six slots, slot 6 empty. /tarot slots');
    else if(newSeq===1)p.tell('[Tarot] Resonance achieved. Individual powers revoked; full merged kit activated.');
    else p.tell('[Tarot] Advanced to Sequence '+newSeq+'. '+n.max_slots+' slots.');
    return {ok:true,state:n};
  }
  global.TarotBatch1Transition={onSequenceChange:onSequenceChange};
})();
