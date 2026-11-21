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
  function ensure(p,force){
    var s=global.TarotBatch1Slots.get(p),marker=score(p,'tc_fool_marker'),wasNew=false;
    if(marker===1){
      if(!s){
        var initialized=global.TarotBatch1Slots.initial('tarot:fool');
        global.TarotBatch1Slots.save(p,initialized);
        s=initialized;wasNew=true;
        p.tell('[Tarot] Fool pathway selected: Sequence 9. /tarot slots');
      }
      // Only initial origin choice, login, respawn or dimension change refreshes sources.
      // DO NOT revoke/re-grant on the periodic tick: that resets native cooldowns.
      if(wasNew||force)global.TarotBatch1Grants.refreshSlots(p);
    }else if(marker===0&&s){
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
  onEvent('player.logged_in',function(e){ensure(e.player,true);});
  onEvent('player.respawned',function(e){ensure(e.player,true);});
  // VERIFY HOOK: 1802 player.changed_dimension; if absent, login/20-tick sync is fallback.
  onEvent('player.changed_dimension',function(e){ensure(e.player,true);});
  onEvent('player.tick',function(e){
    var p=e.player, d=p.persistentData;
    var n=d.getInt('tarot_batch1_lifecycle_tick')+1;
    d.putInt('tarot_batch1_lifecycle_tick',n);
    if(n%20!==0)return;
    ensure(p,false);scan(p);
  });
  global.TarotBatch1Lifecycle={score:score,ensure:ensure,scan:scan};
})();
