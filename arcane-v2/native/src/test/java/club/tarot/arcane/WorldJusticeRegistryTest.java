package club.tarot.arcane;
import static org.junit.Assert.*;
import java.util.HashSet;
import org.junit.Test;
public final class WorldJusticeRegistryTest {
 @Test public void uniqueWorldJusticeAndResonanceResources() {
   HashSet<String> found=new HashSet<>();
   for(String pathway:new String[]{"world","justice","marked_verdict"}) {
     for(int seq=0;seq<=9;seq++) {
       assertTrue("Missing sequence "+pathway+"/"+seq,AbilityRegistry.implemented(pathway,seq));
       for(String id:AbilityRegistry.forSequence(pathway,seq)) {
         assertTrue("Duplicate "+id,found.add(id));
         assertNotNull(getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
       }
     }
   }
   assertEquals(40,found.size());
 }
 @Test public void justiceResonanceReplacesIndividualsAtSequenceOne() {
   for(String primary:new String[]{"world","justice"}) {
     SlotModel.Profile player=new SlotModel.Profile(primary);
     player.onSequenceChange(4);
     assertEquals(primary.equals("world")?"justice":"world",player.secondary());
     player.setSlot(6,player.secondary(),9);
     player.onSequenceChange(1);
     assertEquals("resonance",player.mode());
     for(int seq=0;seq<=9;seq++)assertTrue(player.active("marked_verdict",seq));
     assertFalse(player.active("world",9));
     assertFalse(player.active("justice",9));
   }
 }
}
