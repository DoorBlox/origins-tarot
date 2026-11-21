package club.tarot.arcane;
import static org.junit.Assert.*;
import java.util.HashSet;
import org.junit.Test;

public final class DevilJudgementRegistryTest {
 @Test public void everySequenceFromBothPathsAndContractHasNamedPowers() {
   HashSet<String> files=new HashSet<>();
   for(String path:new String[]{"devil","judgement","binding_contract"})for(int seq=0;seq<=9;seq++){
     assertTrue(path+":"+seq,AbilityRegistry.implemented(path,seq));
     for(String id:AbilityRegistry.forSequence(path,seq)){
       assertTrue(id,files.add(id));
       assertNotNull(id,getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
     }
   }
   assertEquals(40,files.size());
 }
 @Test public void allContractSequencesActivateTogetherAtOne(){
   for(String first:new String[]{"devil","judgement"}){
     SlotModel.Profile p=new SlotModel.Profile(first);
     p.onSequenceChange(4);
     assertTrue(p.identityActive(SlotModel.paired(first)));
     p.onSequenceChange(1);
     assertEquals("resonance",p.mode());
     for(int seq=0;seq<=9;seq++)assertTrue(p.active("binding_contract",seq));
     assertFalse(p.active("devil",9));assertFalse(p.active("judgement",9));
   }
 }
 @Test public void unansweredContractNeverTriggersPenalties(){
   assertFalse(ContractRules.penaltyPermitted(null));
   assertFalse(ContractRules.penaltyPermitted("accept"));
   assertTrue(ContractRules.penaltyPermitted("refuse"));
 }
 @Test public void ownerCannotOfferToSelfAndNoLateResponseCanPenalize(){
   assertFalse(ContractRules.validOffer(true,true,100,120));
   assertFalse(ContractRules.validOffer(false,false,100,120));
   assertFalse(ContractRules.validOffer(false,true,101,100));
   assertTrue(ContractRules.validOffer(false,true,100,100));
 }
}
