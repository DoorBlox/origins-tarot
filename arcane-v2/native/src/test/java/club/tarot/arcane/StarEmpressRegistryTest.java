package club.tarot.arcane;

import static org.junit.Assert.*;
import java.util.HashSet;
import org.junit.Test;

public final class StarEmpressRegistryTest {
 @Test public void everySequenceResourceIsUniqueAndPackaged(){
   HashSet<String> seen=new HashSet<>();
   for(String pathway:new String[]{"star","empress","starless_poison"})for(int sequence=0;sequence<=9;sequence++){
     assertTrue(AbilityRegistry.implemented(pathway,sequence));
     for(String id:AbilityRegistry.forSequence(pathway,sequence)){
       assertTrue(id,seen.add(id));
       assertNotNull(id,getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
     }
   }
   assertEquals(40,seen.size());
 }
 @Test public void pairedIdentityIsIndependentOfSlots(){
   for(String path:new String[]{"star","empress"}){
     SlotModel.Profile p=new SlotModel.Profile(path);
     p.onSequenceChange(4);
     p.clearSlot(1);
     assertTrue(p.identityActive("star"));
     assertTrue(p.identityActive("empress"));
     p.onSequenceChange(1);
     assertEquals("resonance",p.mode());
     for(int s=0;s<=9;s++)assertTrue(p.active("starless_poison",s));
     assertFalse(p.active("star",9));
     assertFalse(p.active("empress",9));
   }
 }
 @Test public void sunExposedReflectiveArrowIsConditionalAndDoesNotTargetTeammate(){
   assertEquals(1f,StarEmpressRules.exposedArrowMultiplier(false,false),.00001);
   assertEquals(1f,StarEmpressRules.exposedArrowMultiplier(true,false),.00001);
   assertEquals(1.25f,StarEmpressRules.exposedArrowMultiplier(true,true),.00001);
 }
}
