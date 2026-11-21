package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;
import java.util.HashSet;
public final class MagicianStrengthRegistryTest {
 @Test public void allThirtyNineSequenceResourcesArePackaged() {
   HashSet<String> ids=new HashSet<>();
   for(String pathway:new String[]{"magician","strength","impossible_fist"})
     for(int s=9;s>=0;s--) {
       assertTrue(AbilityRegistry.implemented(pathway,s));
       for(String id:AbilityRegistry.forSequence(pathway,s)){
         assertTrue(id,ids.add(id));
         assertNotNull(id,getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
       }
     }
   assertEquals(39,ids.size());
 }
 @Test public void secondPathwayIdentityAndResonanceAreAutomatic(){
   for(String first:new String[]{"magician","strength"}) {
     SlotModel.Profile profile=new SlotModel.Profile(first);
     assertFalse(profile.identityActive(profile.secondary()==null?SlotModel.paired(first):profile.secondary()));
     profile.onSequenceChange(4);
     assertTrue(profile.identityActive(profile.secondary()));
     profile.onSequenceChange(1);
     assertEquals("resonance",profile.mode());
     for(int seq=0;seq<=9;seq++)assertTrue(profile.active("impossible_fist",seq));
     assertFalse(profile.active(first,9));
   }
 }
}
