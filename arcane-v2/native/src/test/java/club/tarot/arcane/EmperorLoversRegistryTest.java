package club.tarot.arcane;
import static org.junit.Assert.*;
import java.util.HashSet;
import org.junit.Test;

public final class EmperorLoversRegistryTest {
 @Test public void allNamedSequenceResourcesArePackagedExactlyOnce() {
   HashSet<String> found=new HashSet<>();
   for(String pathway:new String[]{"emperor","lovers","benevolent_crown"}) {
     for(int sequence=9;sequence>=0;sequence--) {
       assertTrue("Missing "+pathway+"/"+sequence,AbilityRegistry.implemented(pathway,sequence));
       for(String id:AbilityRegistry.forSequence(pathway,sequence)) {
         assertTrue("Duplicate resource "+id,found.add(id));
         assertNotNull(id,getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
       }
     }
   }
   assertEquals(39,found.size());
 }
 @Test public void secondaryIdentityActivatesAtSequenceFourAndNeverNeedsSlot() {
   for(String first:new String[]{"emperor","lovers"}) {
     SlotModel.Profile p=new SlotModel.Profile(first);
     String second=SlotModel.paired(first);
     assertFalse(p.identityActive(second));
     p.onSequenceChange(4);
     assertEquals("slot",p.mode());
     p.clearSlot(1);
     assertTrue(p.identityActive(second));
     p.onSequenceChange(1);
     assertEquals("resonance",p.mode());
     for(int seq=0;seq<=9;seq++)assertTrue(p.active("benevolent_crown",seq));
     assertFalse(p.active("emperor",9));
     assertFalse(p.active("lovers",9));
   }
 }
 @Test public void movementWhitelistIsScopedAndNeverAllowsUnrelatedPlayers(){
   assertFalse(CrownRules.blockMovement(false,false,false));
   assertFalse(CrownRules.blockMovement(true,true,false));
   assertFalse(CrownRules.blockMovement(true,false,true));
   assertTrue(CrownRules.blockMovement(true,false,false));
 }
 @Test public void shieldAndSeparationRulesRespectSourceThresholds(){
   assertEquals(1f,CrownRules.shieldDamageMultiplier(false,false),.0001f);
   assertEquals(.9f,CrownRules.shieldDamageMultiplier(true,false),.0001f);
   assertEquals(.85f,CrownRules.shieldDamageMultiplier(true,true),.0001f);
   assertFalse(CrownRules.separationActive(600));
   assertTrue(CrownRules.separationActive(620));
 }
}
