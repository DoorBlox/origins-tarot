// Minecraft 1.18.2 KubeJS legacy Brigadier command registration.
onEvent('command.registry',function(event){
  var C=event.commands,A=event.arguments,S=global.TarotBatch1Slots;
  function player(ctx){return ctx.source.player;}
  function output(p,r){
    if(!p)return 0;
    if(typeof r==='string'){p.tell(r);return 1;}
    p.tell(r.ok?'[Tarot] Updated. /tarot slots':'[Tarot] '+r.error);
    return r.ok?1:0;
  }
  function edit(ctx,fn){
    var p=player(ctx);if(!p)return 0;
    return output(p,fn(p));
  }
  var root=C.literal('tarot');
  root.then(C.literal('slots').executes(function(ctx){
    var p=player(ctx);return p?output(p,S.show(p)):0;
  }));
  root.then(C.literal('reset').executes(function(ctx){
    return edit(ctx,S.reset);
  }));
  var slot=C.literal('slot');
  slot.then(C.literal('auto').executes(function(ctx){
    return edit(ctx,S.auto);
  }));
  var swap=C.literal('swap');
  var left=C.argument('a',A.INTEGER.create(event));
  left.then(C.argument('b',A.INTEGER.create(event)).executes(function(ctx){
    var a=A.INTEGER.getResult(ctx,'a'),b=A.INTEGER.getResult(ctx,'b');
    return edit(ctx,function(p){return S.swapSlots(p,a,b);});
  }));
  swap.then(left);
  slot.then(swap);
  var index=C.argument('index',A.INTEGER.create(event));
  index.then(C.literal('clear').executes(function(ctx){
    var n=A.INTEGER.getResult(ctx,'index');
    return edit(ctx,function(p){return S.clearSlot(p,n);});
  }));
  var pathway=C.argument('pathway',A.STRING.create(event));
  pathway.then(C.argument('sequence',A.INTEGER.create(event)).executes(function(ctx){
    var n=A.INTEGER.getResult(ctx,'index');
    var id=String(A.STRING.getResult(ctx,'pathway'));
    if(!/^tarot:[a-z0-9_]+$/.test(id))
      return output(player(ctx),{ok:false,error:'Invalid pathway.'});
    var seq=A.INTEGER.getResult(ctx,'sequence');
    return edit(ctx,function(p){return S.setSlot(p,n,id,seq);});
  }));
  index.then(pathway);
  slot.then(index);
  root.then(slot);

  var bind=C.literal('bind'),cast=C.literal('cast');
  function skillCommand(key){
    return C.literal(key).then(C.argument('ability',A.STRING.create(event))
      .executes(function(ctx){
        var p=player(ctx);if(!p)return 0;
        var ability=String(A.STRING.getResult(ctx,'ability'));
        return output(p,global.TarotFool.bind(p,key,ability));
      }));
  }
  bind.then(skillCommand('primary'));
  bind.then(skillCommand('secondary'));
  root.then(bind);

  function castCommand(key){
    return C.literal(key).executes(function(ctx){
      var p=player(ctx);if(!p)return 0;
      var bind=p.persistentData.getString('tarot_bind_'+key);
      var skill=String(bind||(key==='primary'?'full_faceless_disguise':'spirit_vision'));
      return output(p,{ok:global.TarotFool.activate(p,skill),error:'Power did not activate.'});
    });
  }
  cast.then(castCommand('primary'));
  cast.then(castCommand('secondary'));
  root.then(cast);

  var debug=C.literal('debug').requires(function(source){return source.hasPermission(2);});
  var seqNode=C.literal('sequence');
  seqNode.then(C.argument('seq',A.INTEGER.create(event)).executes(function(ctx){
    var p=player(ctx);if(!p)return 0;
    var state=S.get(p);if(!state)return output(p,{ok:false,error:'Choose Fool first.'});
    var seq=A.INTEGER.getResult(ctx,'seq');
    var result=global.TarotBatch1Transition.onSequenceChange(p,state.sequence,seq);
    if(result.ok)try{
      global.TarotBatch1Grants.run(p,'scoreboard players set @s tc_curseq '+seq);
    }catch(ignore){}
    return output(p,result);
  }));
  debug.then(seqNode);
  root.then(debug);
  event.register(root);
});
