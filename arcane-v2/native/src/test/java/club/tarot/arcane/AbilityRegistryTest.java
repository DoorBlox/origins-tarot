package club.tarot.arcane;

import static org.junit.Assert.*;
import java.util.HashSet;
import org.junit.Test;

public class AbilityRegistryTest {
    @Test public void powersFollowActualSequenceSlotAssignments() {
        SlotModel.Profile player = new SlotModel.Profile("fool");
        assertTrue(AbilityRegistry.isActive(player,"spirit_vision"));
        assertFalse(AbilityRegistry.isActive(player,"borrowed_face"));
        player.onSequenceChange(6);
        assertTrue(AbilityRegistry.isActive(player,"borrowed_face"));
        player.onSequenceChange(4);
        player.clearSlot(1);
        assertFalse(AbilityRegistry.isActive(player,"spirit_vision"));
        player.onSequenceChange(1);
        assertFalse(AbilityRegistry.isActive(player,"borrowed_face"));
    }
    @Test public void removedSequencesAreNotStillActiveAfterSlotReassignment() {
        SlotModel.Profile p=new SlotModel.Profile("fool");
        p.onSequenceChange(4);
        assertTrue(AbilityRegistry.isActive(p,"spirit_vision"));
        p.clearSlot(1);
        assertFalse(AbilityRegistry.isActive(p,"spirit_vision"));
        p.setSlot(1,"hanged_man",9);
        assertTrue(AbilityRegistry.isActive(p,"sin_bearing"));
        assertFalse(AbilityRegistry.isActive(p,"spirit_vision"));
        p.onSequenceChange(1);
        assertTrue(AbilityRegistry.isActive(p,"burdened_beginning"));
        assertFalse(AbilityRegistry.isActive(p,"sin_bearing"));
    }
    @Test public void primaryAndSecondaryMetaBindingsArePackaged() {
        assertNotNull(getClass().getClassLoader().getResource("data/tarot/powers/meta/primary_key.json"));
        assertNotNull(getClass().getClassLoader().getResource("data/tarot/powers/meta/secondary_key.json"));
    }
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
        assertTrue(AbilityRegistry.implemented("hanged_man",9));
        assertTrue(AbilityRegistry.implemented("paper_martyr",9));
    }
}
