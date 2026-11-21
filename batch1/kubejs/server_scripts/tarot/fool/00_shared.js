// Batch 1 gameplay dispatcher for KubeJS Fabric 1802.5.5, legacy event API.
// All powers are gated again against saved, server-side slot assignments.
(function(){
  var hooks={tick:[],hurt:[],hit:[],death:[],dead:[],food:[]},casts={};
  function ready(p,seq){
    var s=global.TarotBatch1Slots.get(p);
    if(!s||s.mode==='resonance')return false;
    for(var i=0;i<s.slots.length;i++)
      if(s.slots[i].pathway==='tarot:fool'&&s.slots[i].sequence===seq)return true;
    return false;
  }
  function str(e){return String(e&&e.type||'');}
  function player(e){return str(e)==='minecraft:player';}
  function team(e){
    try{var x=e.minecraftPlayer||e;return x.getTeam()?String(x.getTeam().getName()):null;}
    catch(err){return null;}
  }
  function nearby(owner,radius){
    // VERIFY: KubeJS 1802 getEntitiesWithin + AABB.of on Fabric (fallback: area-of-effect mcfunctions).
    try{
      var l=owner.level,box=AABB.of(owner.x-radius,owner.y-radius,owner.z-radius,
                                     owner.x+radius,owner.y+radius,owner.z+radius);
      var all=l.getEntitiesWithin(box),out=[];
      for(var i=0;i<all.length&&out.length<50;i++){
        var e=all[i],dx=e.x-owner.x,dy=e.y-owner.y,dz=e.z-owner.z;
        if(dx*dx+dy*dy+dz*dz<=radius*radius)out.push(e);
      }
      return out;
    }catch(e){return [];}
  }
  function enemy(owner,target){
    if(!target||target===owner)return false;
    if(player(target)){
      var tn=team(target),on=team(owner);
      if(on!==null&&tn!==null&&on===tn)return false;
      return String(target.username||target.name)!==String(owner.username||owner.name);
    }
    return global.TarotBatch1Registry.hostiles.indexOf(str(target).replace(/^minecraft:/,''))!==-1;
  }
  function enemies(owner,radius){
    return nearby(owner,radius).filter(function(e){return enemy(owner,e);});
  }
  function effect(e,name,ticks,amplifier){
    try{e.potionEffects.add('minecraft:'+name,ticks,amplifier||0);return true;}
    catch(err){return false;}
  }
  function key(name){return 'tarot_cd_'+String(name).replace(/[^a-z0-9_]/g,'_');}
  function now(){return Date.now();}
  function offCooldown(p,name){return p.persistentData.getLong(key(name))<=now();}
  function cooldown(p,name,ticks){
    if(!offCooldown(p,name))return false;
    p.persistentData.putLong(key(name),now()+ticks*50);return true;
  }
  function seconds(p,name){return Math.max(0,Math.ceil((p.persistentData.getLong(key(name))-now())/1000));}
  function combat(p){return p.persistentData.getLong('tarot_last_combat');}
  function markCombat(p){p.persistentData.putLong('tarot_last_combat',now());}
  function safe(p){return now()-combat(p)>=10000;}
  function run(p,cmd){return global.TarotBatch1Grants.run(p,cmd);}
  function decoy(p,duration){
    run(p,'summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Invisible:1b,NoGravity:1b,Invulnerable:0b,Tags:["tarot_decoy","tarot_batch1_decoy"]}');
    // VERIFY: server.scheduleInTicks exists in 1802.5.5; fallback is scoreboard age cleanup.
    var uid=String(p.uuid||p.username);
    p.server.scheduleInTicks(duration,function(){
      try{run(p,'kill @e[type=minecraft:armor_stand,tag=tarot_batch1_decoy,distance=..10]');}catch(ignore){}
    });
  }
  function activate(p,name){
    var x=casts[name];if(!x){p.tell('[Tarot] Unknown bound power '+name);return false;}
    if(!ready(p,x.seq)){p.tell('[Tarot] This power is not in your slots.');return false;}
    if(!offCooldown(p,name)){p.tell('[Tarot] '+name+' cooldown: '+seconds(p,name)+'s');return false;}
    return x.action(p)===true;
  }
  function bind(p,key,name){
    var x=casts[name];
    if(!x||x.key!==key)return {ok:false,error:'Unknown '+key+' skill.'};
    if(!ready(p,x.seq))return {ok:false,error:'Slot the required sequence first.'};
    p.persistentData.putString('tarot_bind_'+key,name);
    return {ok:true};
  }
  function dispatch(p,key){
    var d=p.persistentData.getString('tarot_bind_'+key);
    var name=String(d|| (key==='primary'?'full_faceless_disguise':'spirit_vision'));
    return activate(p,name);
  }
  function registerCast(name,seq,key,fn){casts[name]={seq:seq,key:key,action:fn};}
  function register(event,fn){if(!hooks[event])throw Error('Unknown Tarot hook '+event);hooks[event].push(fn);}
  var api={ready:ready,player:player,team:team,nearby:nearby,enemy:enemy,enemies:enemies,
           effect:effect,cooldown:cooldown,offCooldown:offCooldown,combat:combat,
           markCombat:markCombat,safe:safe,run:run,decoy:decoy,activate:activate,
           bind:bind,registerCast:registerCast,register:register,hooks:hooks,casts:casts};
  global.TarotFool=api;
  onEvent('player.tick',function(e){
    var p=e.player,d=p.persistentData,n=d.getInt('tarot_fool_tick')+1;
    d.putInt('tarot_fool_tick',n);
    if(n%2===0){
      var score=global.TarotBatch1Lifecycle&&global.TarotBatch1Lifecycle.score;
      if(score){
        for(var i=0;i<2;i++){
          var keyName=i===0?'g':'v',k='tc_req_'+keyName;
          if(score(p,k)>0){
            run(p,'scoreboard players set @s '+k+' 0');
            dispatch(p,i===0?'primary':'secondary');
          }
        }
      }
    }
    for(var j=0;j<hooks.tick.length;j++)hooks.tick[j](p,n);
  });
  // VERIFY HOOK: entity.hurt; supported in 1.18-era KubeJS, but damage mutation differs by loader.
  onEvent('entity.hurt',function(e){
    var target=e.entity,src=e.source&&e.source.actual;
    if(player(target)&&global.TarotBatch1Slots.get(target)){
      markCombat(target);
      for(var i=0;i<hooks.hurt.length;i++)hooks.hurt[i](target,e,src);
    }
    if(src&&player(src)&&global.TarotBatch1Slots.get(src)){
      markCombat(src);
      for(var j=0;j<hooks.hit.length;j++)hooks.hit[j](src,e,target);
    }
  });
  onEvent('entity.death',function(e){
    var v=e.entity,src=e.source&&e.source.actual;
    if(player(v))for(var i=0;i<hooks.dead.length;i++)hooks.dead[i](v,e);
    if(src&&player(src))
      for(var j=0;j<hooks.death.length;j++)hooks.death[j](src,e,v);
  });
  onEvent('item.food_eaten',function(e){
    if(e.player)for(var i=0;i<hooks.food.length;i++)hooks.food[i](e.player,e);
  });
})();
