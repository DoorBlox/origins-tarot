package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;
import java.util.HashSet;

public final class SunMoonRegistryTest {
 @Test public void exactSequencesArePackaged(){
   HashSet<String> ids=new HashSet<>();
   for(String pathway:new String[]{"sun","moon","eclipse"})
     for(int s=0;s<=9;s++) {
       assertTrue(pathway+"/"+s,AbilityRegistry.implemented(pathway,s));
       for(String id:AbilityRegistry.forSequence(pathway,s)) {
         assertTrue(id,ids.add(id));
         assertNotNull(id,getClass().getClassLoader().getResource("data/tarot/powers/"+id.substring(6)+".json"));
       }
     }
   assertEquals(40,ids.size());
 }
 @Test public void bothIdentityDrawbacksSurviveUnslottedAndResonance(){
   for(String first:new String[]{"sun","moon"}){
     SlotModel.Profile p=new SlotModel.Profile(first);
     p.onSequenceChange(4);p.clearSlot(1);
     assertTrue(p.identityActive("sun"));assertTrue(p.identityActive("moon"));
     p.onSequenceChange(1);assertEquals("resonance",p.mode());
     for(int i=0;i<=9;i++)assertTrue(p.active("eclipse",i));
   }
 }
 @Test public void celestialDamageNeverConfusesUndeadAndEnemyPlayerAuras(){
   assertEquals(6f,SunMoonRules.fixedSunPulse(true,false),.00001f);
   assertEquals(1f,SunMoonRules.fixedSunPulse(false,true),.00001f);
   assertEquals(0f,SunMoonRules.fixedSunPulse(false,false),.00001f);
 }
}
