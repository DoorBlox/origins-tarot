package club.tarot.arcane;

import static org.junit.Assert.*;
import java.util.HashSet;
import org.junit.Test;

public class AbilityRegistryTest {
    @Test public void foolHasAllFourteenNamedUniquePowers() {
        HashSet<String> all = new HashSet<>();
        for(int seq=0;seq<=9;seq++) {
            assertTrue(AbilityRegistry.implemented("fool",seq));
            for(String id:AbilityRegistry.forSequence("fool",seq)) {
                assertTrue(id.startsWith("tarot:fool/"+seq+"_"));
                assertTrue("duplicate: "+id,all.add(id));
                assertTrue(AbilityRegistry.has(id));
            }
        }
        assertEquals(14,all.size());
        assertFalse(AbilityRegistry.has("tarot:fool/8_fabricated_power"));
        assertFalse(AbilityRegistry.implemented("hanged_man",9));
    }
}
