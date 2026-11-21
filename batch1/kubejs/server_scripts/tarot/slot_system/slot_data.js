// Persistent, independently testable Rev 3 slot model (KubeJS 1802/Rhino ES5-compatible).
// No switching Origins: marker + permanent identity never enter the tarot_slot source.
(function(){
  var KEY='tarot_slots';
  function reg(){return global.TarotBatch1Registry;}
  function empty(){return {pathway:null,sequence:null};}
  function entry(path,seq){return {pathway:path,sequence:seq};}
  function modeFor(seq){return seq>=5?'single':seq>=2?'slot':'resonance';}
  function maxFor(seq){return 10-seq;}
  function copy(s){return JSON.parse(JSON.stringify(s));}
  function pairOf(path){
    var slug=String(path).replace(/^tarot:/,'');
    var pairs=reg().pairs;
    for(var i=0;i<pairs.length;i++){
      if(pairs[i][0]===slug)return {secondary:'tarot:'+pairs[i][1],resonance:'tarot:'+pairs[i][2]};
      if(pairs[i][1]===slug)return {secondary:'tarot:'+pairs[i][0],resonance:'tarot:'+pairs[i][2]};
    }
    return null;
  }
  function initial(primary){
    var match=pairOf(primary);
    if(!match||!reg().complete[String(primary).replace(/^tarot:/,'')])return null;
    return {schema:1,primary:primary,secondary:match.secondary,resonance:match.resonance,
      sequence:9,mode:'single',max_slots:1,slots:[entry(primary,9)]};
  }
  function isValid(s){
    if(!s||s.schema!==1||!Number.isInteger(s.sequence)||s.sequence<0||s.sequence>9)return false;
    if(s.mode!==modeFor(s.sequence)||s.max_slots!==maxFor(s.sequence))return false;
    var pair=pairOf(s.primary);
    if(!pair||pair.secondary!==s.secondary||pair.resonance!==s.resonance)return false;
    if(!Array.isArray(s.slots)||s.slots.length!==(s.mode==='resonance'?0:s.max_slots))return false;
    var used={};
    for(var i=0;i<s.slots.length;i++){
      var x=s.slots[i];
      if(!x||typeof x!=='object')return false;
      if(x.pathway===null&&x.sequence===null){if(s.mode==='single')return false;continue;}
      if(x.pathway!==s.primary&&x.pathway!==s.secondary)return false;
      if(!Number.isInteger(x.sequence)||x.sequence<s.sequence||x.sequence>9)return false;
      if(s.mode==='single'&&(x.pathway!==s.primary||x.sequence!==9-i))return false;
      var key=x.pathway+':'+x.sequence;if(used[key])return false;used[key]=true;
    }
    return true;
  }
  function get(p){
    try{var raw=p.persistentData.getString(KEY);
      if(!raw)return null;var state=JSON.parse(String(raw));return isValid(state)?state:null;
    }catch(e){return null;}
  }
  function save(p,state){
    if(!isValid(state))throw Error('Invalid tarot slot state; refusing to write');
    p.persistentData.putString(KEY,JSON.stringify(state));
    return state;
  }
  function apply(p,fn){
    var current=get(p);if(!current)return {ok:false,error:'Choose the Fool Origin first.'};
    var next=copy(current);var result=fn(next);
    if(result!==true)return {ok:false,error:String(result||'Invalid operation.')};
    if(!isValid(next))return {ok:false,error:'Slot validation failed.'};
    // Save once; the grant engine will reconcile from this saved state.
    save(p,next);
    if(global.TarotBatch1Grants)global.TarotBatch1Grants.refreshSlots(p);
    return {ok:true,state:next};
  }
  function slotChange(p,index,path,sequence){
    return apply(p,function(s){
      if(s.mode!=='slot')return 'Slot editing unlocks at Sequence 4 and ends at Sequence 1.';
      if(index<1||index>s.max_slots)return 'Slot index out of range.';
      if(path!==s.primary&&path!==s.secondary)return 'Pathway not registered for this player.';
      var slug=path.slice(6);
      if(!reg().complete[slug])return 'Pathway '+path+' is not implemented yet (Batch 2+).';
      if(!Number.isInteger(sequence)||sequence<s.sequence||sequence>9)return 'Sequence not unlocked.';
      for(var i=0;i<s.slots.length;i++){
        if(i!==index-1&&s.slots[i].pathway===path&&s.slots[i].sequence===sequence)
          return 'That pathway/sequence is already assigned.';
      }
      s.slots[index-1]=entry(path,sequence);return true;
    });
  }
  function clearSlot(p,index){
    return apply(p,function(s){
      if(s.mode!=='slot')return 'Only slot mode can be edited.';
      if(index<1||index>s.max_slots)return 'Slot index out of range.';
      s.slots[index-1]=empty();return true;
    });
  }
  function swapSlots(p,a,b){
    return apply(p,function(s){
      if(s.mode!=='slot')return 'Only slot mode can be edited.';
      if(a<1||a>s.max_slots||b<1||b>s.max_slots)return 'Slot index out of range.';
      var tmp=s.slots[a-1];s.slots[a-1]=s.slots[b-1];s.slots[b-1]=tmp;return true;
    });
  }
  function auto(p){
    return apply(p,function(s){
      if(s.mode!=='slot')return 'Already auto-filled, or Resonance is active.';
      s.slots=[];
      for(var n=9;n>=s.sequence;n--)s.slots.push(entry(s.primary,n));
      return true;
    });
  }
  function getSlots(p){var s=get(p);return s?copy(s.slots):[];}
  function show(p){
    var s=get(p);if(!s)return '[Tarot] No active registration. Choose Fool to start.';
    var lines=['[Tarot] '+s.mode.toUpperCase()+' | Sequence '+s.sequence+
      ' | slots '+s.slots.filter(function(x){return x.pathway!==null;}).length+'/'+s.max_slots,
      'Primary '+s.primary+' | Secondary '+s.secondary+' | Resonance '+s.resonance];
    for(var i=0;i<s.slots.length;i++){
      var x=s.slots[i];lines.push('['+(i+1)+'] '+(x.pathway===null?'EMPTY':x.pathway+' Seq '+x.sequence));
    }
    return lines.join('\n');
  }
  global.TarotBatch1Slots={
    initial:initial,get:get,save:save,getSlots:getSlots,setSlot:slotChange,clearSlot:clearSlot,
    swapSlots:swapSlots,auto:auto,reset:auto,modeFor:modeFor,maxFor:maxFor,pairOf:pairOf,
    getMode:function(p){var s=get(p);return s?s.mode:null;},
    getMaxSlots:function(p){var s=get(p);return s?s.max_slots:0;},
    show:show,copy:copy,isValid:isValid,empty:empty,entry:entry
  };
})();
