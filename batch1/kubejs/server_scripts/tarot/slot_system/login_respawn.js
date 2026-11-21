// Real origin choice is signaled by origins:action_on_callback on tarot:meta/origin_marker_fool.
// onEvent handlers intentionally use KubeJS 1.18.2 names.
(function(){
  function score(p,obj){
    try{
      var n=p.minecraftPlayer||p,b=n.getScoreboard(),o=b.getObjective(obj);
      if(!o)return null;
      return Number(b.getOrCreatePlayerScore(n.getScoreboardName(),o).getScore());
    }catch(e){return null;}
  }
  function ensure(p){
    var s=global.TarotBatch1Slots.get(p),marker=score(p,'tc_fool_marker');
    if(marker===1){
      if(!s){
        var initialized=global.TarotBatch1Slots.initial('tarot:fool');
        global.TarotBatch1Slots.save(p,initialized);
        s=initialized;p.tell('[Tarot] Fool pathway selected: Sequence 9. /tarot slots');
      }
      global.TarotBatch1Grants.refreshSlots(p);
    }else if(marker===0 && s){
      global.TarotBatch1Grants.clear(p);
      p.persistentData.remove('tarot_slots');
      p.tell('[Tarot] Fool origin removed. Slot-managed abilities cleared.');
    }
  }
  function scan(p){
    var state=global.TarotBatch1Slots.get(p);
    if(!state)return;
    var seq=score(p,'tc_curseq');
    if(seq!==null&&seq===state.sequence-1)
      global.TarotBatch1Transition.onSequenceChange(p,state.sequence,seq);
    // Failed/bypassed transitions are never extrapolated or repeated on arbitrary values.
  }
  onEvent('player.logged_in',function(e){ensure(e.player);});
  onEvent('player.respawned',function(e){ensure(e.player);});
  // VERIFY HOOK: 1802 player.changed_dimension; if absent, login/20-tick sync is fallback.
  onEvent('player.changed_dimension',function(e){ensure(e.player);});
  onEvent('player.tick',function(e){
    var p=e.player, d=p.persistentData;
    var n=d.getInt('tarot_batch1_lifecycle_tick')+1;
    d.putInt('tarot_batch1_lifecycle_tick',n);
    if(n%20!==0)return;
    ensure(p);scan(p);
  });
  global.TarotBatch1Lifecycle={score:score,ensure:ensure,scan:scan};
})();
