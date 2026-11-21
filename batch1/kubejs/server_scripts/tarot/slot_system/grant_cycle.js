// Grant/revoke source is exclusively tarot_slot. Never revoke the Origin's identity.
(function(){
  var SAFE_NAME=/^[A-Za-z0-9_]{1,16}$/;
  function username(p){return String(p.username||(p.name&&p.name.string)||'');}
  function run(p,cmd){
    var name=username(p);
    if(!SAFE_NAME.test(name))throw Error('Unsafe player name');
    return p.server.runCommandSilent('execute as '+name+' at @s run '+cmd);
  }
  function powersFor(slug,seq){
    var m=global.TarotBatch1Registry.powers[slug];
    return m&&m[seq]?m[seq].map(function(id){return 'tarot:'+slug+'/'+id;}):[];
  }
  function activeIds(s){
    var ids=[],reg=global.TarotBatch1Registry;
    if(s.mode==='resonance'){
      var slug=s.resonance.substring(6);
      if(!reg.resonanceComplete[slug])return null; // fail closed; Batch 2 pending
      for(var n=9;n>=0;n--)ids=ids.concat(powersFor(slug,n));
      return ids;
    }
    for(var i=0;i<s.slots.length;i++){
      var slot=s.slots[i];if(slot.pathway===null)continue;
      var id=slot.pathway.substring(6);
      if(!reg.complete[id])return null;
      ids=ids.concat(powersFor(id,slot.sequence));
    }
    return ids;
  }
  function refreshSlots(p){
    var s=global.TarotBatch1Slots.get(p);
    if(!s)return {ok:false,error:'No slot state'};
    var ids=activeIds(s);
    if(ids===null)return {ok:false,error:'Pathway/Resonance kit not implemented'};
    try{
      run(p,'power revokeall @s tarot_slot');
      for(var i=0;i<ids.length;i++)run(p,'power grant @s '+ids[i]+' tarot_slot');
      return {ok:true,count:ids.length};
    }catch(e){
      // Clear partial grants if an individual command fails. Never corrupt identity.
      try{run(p,'power revokeall @s tarot_slot');}catch(ignore){}
      return {ok:false,error:String(e)};
    }
  }
  function clear(p){return run(p,'power revokeall @s tarot_slot');}
  global.TarotBatch1Grants={
    refreshSlots:refreshSlots,clear:clear,activeIds:activeIds,powersFor:powersFor,run:run
  };
})();
