package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;
public final class AscensionRulesTest {
 @Test public void previousV3ActingCostsNowControlOneSharedSequence() {
    int[] costs={0,6,5,4,4,3,3,2,2,1};
    for(int seq=1;seq<=9;seq++)assertEquals(costs[seq],AscensionRules.marksToAscend(seq));
    assertThrows(IllegalArgumentException.class,()->AscensionRules.marksToAscend(0));
 }
 @Test public void noAutomaticFreeAscensionWithoutRealActingAltarAndIngredients() {
    assertFalse(AscensionRules.eligible(1,false,true,true,9));
    assertFalse(AscensionRules.eligible(1,true,false,true,9));
    assertFalse(AscensionRules.eligible(1,true,true,false,9));
    assertFalse(AscensionRules.eligible(0,true,true,true,9));
    assertTrue(AscensionRules.eligible(1,true,true,true,9));
    assertFalse(AscensionRules.eligible(100,true,true,true,0));
 }
}
