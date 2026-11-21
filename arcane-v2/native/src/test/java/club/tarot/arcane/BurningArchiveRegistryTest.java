package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;
import java.util.HashSet;
public class BurningArchiveRegistryTest {
 @Test public void allThirtyNineSequenceAbilitiesExist() {
   HashSet<String> all=new HashSet<>();
   for(String path:new String[]{"hermit","chariot","burning_archive"})
     for(int seq=9;seq>=0;seq--) {
       assertTrue(AbilityRegistry.implemented(path,seq));
       for(String id:AbilityRegistry.forSequence(path,seq)) {
         assertTrue("Duplicate "+id,all.add(id));
         assertNotNull(getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
       }
     }
   assertEquals(39,all.size());
 }
 @Test public void resonanceAtOneDiscardBothIndividualKits() {
   for(String first:new String[]{"hermit","chariot"}) {
     SlotModel.Profile p=new SlotModel.Profile(first);
     p.onSequenceChange(4);
     assertEquals("slot",p.mode());
     p.setSlot(6,p.secondary(),9);
     assertTrue(p.identityActive(p.secondary()));
     p.onSequenceChange(1);
     assertTrue(p.slots().isEmpty());
     for(int seq=9;seq>=0;seq--)assertTrue(p.active("burning_archive",seq));
     assertFalse(p.active("hermit",9));
   }
 }
}
