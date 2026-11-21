package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;
import java.util.HashSet;
public final class DeathTowerRegistryTest {
 @Test public void everySequencePowerExistsInJar() {
     int count=0;HashSet<String> ids=new HashSet<>();
     for(String pathway:new String[]{"death","tower","crumbling_reaper"})
       for(int s=9;s>=0;s--) {
         assertTrue("Missing kit "+pathway+"/"+s,AbilityRegistry.implemented(pathway,s));
         for(String id:AbilityRegistry.forSequence(pathway,s)) {
           assertTrue(ids.add(id));
           assertNotNull(getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
           count++;
         }
       }
     assertEquals(40,count);
 }
 @Test public void automaticResonanceIncludesZeroCapstoneAtOne() {
     for(String first:new String[]{"death","tower"}) {
         SlotModel.Profile p=new SlotModel.Profile(first);
         p.onSequenceChange(4);
         assertTrue(p.identityActive(p.secondary()));
         p.setSlot(6,p.secondary(),9);
         p.onSequenceChange(1);
         assertEquals("resonance",p.mode());
         for(int i=0;i<=9;i++)assertTrue(p.active("crumbling_reaper",i));
         assertFalse(p.active("death",9));assertFalse(p.active("tower",9));
     }
 }
}
