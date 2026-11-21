/* Node-only simulation: exercises state logic without claiming a Minecraft game test. */
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const ROOT=path.resolve(__dirname,'../kubejs/server_scripts/tarot/slot_system');
const ctx=vm.createContext({global:{},console,Date,JSON,Number,String,Math,Error,Array,Object,RegExp});
for(const name of ['registry.js','slot_data.js','grant_cycle.js','sequence_transitions.js'])
  vm.runInContext(fs.readFileSync(path.join(ROOT,name),'utf8'),ctx,{filename:name});
const S=ctx.global.TarotBatch1Slots,G=ctx.global.TarotBatch1Grants,T=ctx.global.TarotBatch1Transition;
function fakePlayer(){
  const map={},commands=[];
  return {
    username:'TestPlayer',
    name:{string:'TestPlayer'},
    tells:[],
    tell(m){this.tells.push(m);},
    persistentData:{
      getString(k){return map[k]||'';},putString(k,v){map[k]=v;},
      remove(k){delete map[k];}
    },
    server:{runCommandSilent(cmd){commands.push(cmd);return 1;}},
    commands,map
  };
}
const p=fakePlayer();assert.equal(S.get(p),null);
const first=S.initial('tarot:fool');assert(first);S.save(p,first);
assert.equal(S.getMode(p),'single');assert.equal(S.getMaxSlots(p),1);
assert.deepEqual(G.activeIds(S.get(p)).length,4);
assert.equal(G.refreshSlots(p).count,4);
assert(p.commands[0].includes('power revokeall @s tarot_slot'));
assert(p.commands.every(x=>!x.includes('origin set')));
assert(p.commands.every(x=>!x.includes('power clear')));
assert(p.commands.every(x=>!x.includes('identity_spiritual_expenditure')));
for(let n=8;n>=5;n--){
  let before=S.get(p).sequence;
  let result=T.onSequenceChange(p,before,n);
  assert(result.ok,result.error);
  assert.equal(S.get(p).sequence,n);
  assert.equal(S.getSlots(p).length,10-n);
}
let into4=T.onSequenceChange(p,5,4);assert(into4.ok,into4.error);
assert.equal(S.getMode(p),'slot');
assert.equal(S.getMaxSlots(p),6);
assert.equal(S.getSlots(p).filter(s=>s.pathway===null).length,1);
let unimplemented=S.setSlot(p,6,'tarot:hanged_man',4);
assert(!unimplemented.ok);
assert.equal(S.getSlots(p)[5].pathway,null);
let add=S.setSlot(p,6,'tarot:fool',4);assert(add.ok,add.error);
let duplicate=S.setSlot(p,5,'tarot:fool',9);assert(!duplicate.ok);
let invalid=S.setSlot(p,7,'tarot:fool',4);assert(!invalid.ok);
let prior=S.getSlots(p);assert.equal(prior.length,6);
let moved=S.swapSlots(p,1,6);assert(moved.ok);
assert.equal(S.getSlots(p)[0].sequence,4);
assert(S.clearSlot(p,1).ok);
assert.equal(S.getSlots(p)[0].pathway,null);
assert(S.auto(p).ok);
assert.equal(S.getSlots(p).filter(x=>x.pathway).length,6);
assert.equal(S.getSlots(p)[0].sequence,9);
assert.equal(S.getSlots(p)[5].sequence,4);
assert(T.onSequenceChange(p,4,3).ok);
assert.equal(S.getMaxSlots(p),7);
assert.equal(S.getSlots(p)[6].pathway,null);
assert(T.onSequenceChange(p,3,2).ok);
assert.equal(S.getMaxSlots(p),8);
assert.equal(S.getSlots(p)[7].pathway,null);
const before=S.get(p);
const blocked=T.onSequenceChange(p,2,1);
assert(!blocked.ok && blocked.error.includes('Batch 2'));
assert.equal(S.get(p).sequence,2);
assert.equal(S.getMode(p),'slot');
assert.equal(G.activeIds(S.get(p)).length,14);
assert(p.commands.filter(x=>x.includes('power revokeall @s tarot_slot')).length>=10);
console.log('Batch1 slot simulation PASS: identity isolation, Seq9→2, six/eight slots, blocked unfinished resonance');
