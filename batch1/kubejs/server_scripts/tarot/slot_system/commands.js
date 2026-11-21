// KubeJS 1802.5.5: command.registry uses legacy onEvent, not ServerEvents.
onEvent('command.registry',function(event){
  var C=event.commands,A=event.arguments,S=global.TarotBatch1Slots;
  function player(ctx){return ctx.source.player;}
  function output(p,r){
    if(!p)return 0;
    if(typeof r==='string')p.tell(r);
    else p.tell(r.ok?'[Tarot] Slot configuration updated. /tarot slots':'[Tarot] '+r.error);
    return r.ok===false?0:1;
  }
  function edit(ctx,cb){
    var p=player(ctx);if(!p)return 0;
    return output(p,cb(p));
  }
  var root=C.literal('tarot')
    .then(C.literal('slots').executes(function(ctx){
      var p=player(ctx);if(!p)return 0;return output(p,S.show(p));
    }))
    .then(C.literal('reset').executes(function(ctx){return edit(ctx,S.reset);}))
    .then(C.literal('slot')
      .then(C.literal('auto').executes(function(ctx){return edit(ctx,S.auto);}))
      .then(C.literal('swap')
        .then(C.argument('a',A.INTEGER.create(event))
          .then(C.argument('b',A.INTEGER.create(event))
            .executes(function(ctx){
              var a=A.INTEGER.getResult(ctx,'a'),b=A.INTEGER.getResult(ctx,'b');
              return edit(ctx,function(p){return S.swapSlots(p,a,b);});
            }))))
      )
      .then(C.argument('index',A.INTEGER.create(event))
        .then(C.literal('clear').executes(function(ctx){
          var i=A.INTEGER.getResult(ctx,'index');
          return edit(ctx,function(p){return S.clearSlot(p,i);});
        }))
        .then(C.argument('pathway',A.STRING.create(event))
          .then(C.argument('sequence',A.INTEGER.create(event))
            .executes(function(ctx){
              var i=A.INTEGER.getResult(ctx,'index');
              var path=String(A.STRING.getResult(ctx,'pathway'));
              if(!/^tarot:[a-z0-9_]+$/.test(path))return output(player(ctx),{ok:false,error:'Invalid pathway ID.'});
              var seq=A.INTEGER.getResult(ctx,'sequence');
              return edit(ctx,function(p){return S.setSlot(p,i,path,seq);});
            })))
      )
    )

    .then(C.literal('bind')
      .then(C.literal('primary')
        .then(C.argument('ability',A.STRING.create(event)).executes(function(ctx){
          var p=player(ctx),ability=String(A.STRING.getResult(ctx,'ability'));
          var result=global.TarotFool.bind(p,'primary',ability);
          return output(p,result);
        })))
      .then(C.literal('secondary')
        .then(C.argument('ability',A.STRING.create(event)).executes(function(ctx){
          var p=player(ctx),ability=String(A.STRING.getResult(ctx,'ability'));
          var result=global.TarotFool.bind(p,'secondary',ability);
          return output(p,result);
        })))
    )
    .then(C.literal('cast')
      .then(C.literal('primary').executes(function(ctx){
        var p=player(ctx),name=p.persistentData.getString('tarot_bind_primary')||'full_faceless_disguise';
        return output(p,{ok:global.TarotFool.activate(p,String(name)),error:'Ability did not activate.'});
      }))
      .then(C.literal('secondary').executes(function(ctx){
        var p=player(ctx),name=p.persistentData.getString('tarot_bind_secondary')||'spirit_vision';
        return output(p,{ok:global.TarotFool.activate(p,String(name)),error:'Ability did not activate.'});
      }))
    )
    .then(C.literal('debug').requires(function(src){return src.hasPermission(2);})
      .then(C.literal('sequence')
        .then(C.argument('seq',A.INTEGER.create(event)).executes(function(ctx){
          var p=player(ctx);if(!p)return 0;
          var state=S.get(p);if(!state)return output(p,{ok:false,error:'Choose Fool first.'});
          var seq=A.INTEGER.getResult(ctx,'seq');
          var result=global.TarotBatch1Transition.onSequenceChange(p,state.sequence,seq);
          if(result.ok){
            // Only write the existing V3 objective on successful advancement.
            try{global.TarotBatch1Grants.run(p,'scoreboard players set @s tc_curseq '+seq);}catch(ignore){}
          }
          return output(p,result);
        })))
    );
  event.register(root);
});
