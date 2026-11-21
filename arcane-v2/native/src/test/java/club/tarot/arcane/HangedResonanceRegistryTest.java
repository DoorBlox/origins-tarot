package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;
import java.util.HashSet;
public class HangedResonanceRegistryTest {
 @Test public void allHangedAndMartyrKitsHavePhysicalResources() {
   for (String path : new String[]{"hanged_man", "paper_martyr"}) for (int seq=9;seq>=0;seq--) {
      assertTrue("Missing kit "+path+"/"+seq,AbilityRegistry.implemented(path,seq));
      for(String id:AbilityRegistry.forSequence(path,seq)) {
        String file="data/tarot/powers/"+id.substring(6)+".json";
        assertNotNull(file,getClass().getClassLoader().getResource(file));
      }
   }
 }
 @Test public void refreshModelSwapsToTenMartyrKitsAtOne() {
    SlotModel.Profile p=new SlotModel.Profile("hanged_man");
    p.onSequenceChange(4);
    p.setSlot(6,"fool",9);
    assertTrue(p.active("fool",9));
    p.onSequenceChange(1);
    assertTrue(p.slots().isEmpty());
    assertEquals("paper_martyr",p.resonance());
    for(int i=9;i>=0;i--)assertTrue(p.active("paper_martyr",i));
    assertFalse(p.active("fool",9));
    assertFalse(p.active("hanged_man",9));
 }
 @Test public void registrationIsNoDuplicateAndDispatchedByKit() {
     HashSet<String> all=new HashSet<>();
     for(String pathway:new String[]{"hanged_man","paper_martyr"})
       for(int seq=0;seq<=9;seq++) for(String id:AbilityRegistry.forSequence(pathway,seq))
         assertTrue(id,all.add(id));
     assertEquals(24,all.size());
 }
}
