package club.tarot.arcane;

import static org.junit.Assert.*;
import java.util.List;
import org.junit.Test;

public class SlotModelTest {
    @Test public void allPairsAreBijective() {
        assertEquals(22, SlotModel.PAIRS.size());
        assertEquals(11, SlotModel.RESONANCES.values().stream().distinct().count());
        for (String p : SlotModel.PAIRS.keySet())
            assertEquals(p, SlotModel.paired(SlotModel.paired(p)));
    }
    @Test public void secondaryIdentityUnlocksAtFourAndNeverNeedsASlot() {
        for (String first: SlotModel.PAIRS.keySet()) {
            SlotModel.Profile profile=new SlotModel.Profile(first);
            String second=SlotModel.paired(first);
            assertTrue(profile.identityActive(first));
            assertFalse(profile.identityActive(second));
            profile.onSequenceChange(4);
            assertTrue(profile.identityActive(first));
            assertTrue(profile.identityActive(second));
            profile.clearSlot(1);
            assertTrue("Identity is not a slot-managed power",profile.identityActive(first));
            assertTrue("Second identity is never slotted",profile.identityActive(second));
            profile.onSequenceChange(1);
            assertTrue(profile.identityActive(first));
            assertTrue(profile.identityActive(second));
        }
    }
    @Test public void singleSequenceKitsAreAutoFilled() {
        SlotModel.Profile p = new SlotModel.Profile("fool");
        assertEquals("single", p.mode());
        assertTrue(p.active("fool", 9));
        p.onSequenceChange(5);
        assertEquals(5, p.slots().size());
        for (int seq = 5; seq <= 9; seq++) assertTrue(p.active("fool", seq));
        assertFalse(p.active("hanged_man", 9));
    }
    @Test public void secondPathwayAndSlotTransition() {
        SlotModel.Profile p = new SlotModel.Profile("fool");
        p.onSequenceChange(5);
        p.onSequenceChange(4);
        assertEquals("slot", p.mode());
        assertEquals("hanged_man", p.secondary());
        assertEquals(6, p.maxSlots());
        assertNull(p.slots().get(5));
        p.setSlot(6, "hanged_man", 9);
        assertTrue(p.active("hanged_man", 9));
        assertFalse(p.active("hanged_man", 4));
        assertThrows(IllegalArgumentException.class, () -> p.setSlot(2,"hanged_man", 9));
        assertThrows(IllegalArgumentException.class, () -> p.setSlot(2,"sun", 9));
        assertThrows(IllegalArgumentException.class, () -> p.setSlot(2,"hanged_man", 3));
        p.swap(1, 6);
        assertEquals("hanged_man", p.slots().get(0).pathway);
        p.clearSlot(1);
        assertNull(p.slots().get(0));
    }
    @Test public void largerSlotsRemainEmptyUntilAssigned() {
        SlotModel.Profile p = new SlotModel.Profile("fool");
        p.onSequenceChange(4);
        p.setSlot(6, "hanged_man", 9);
        p.onSequenceChange(3);
        assertEquals(7, p.maxSlots()); assertNull(p.slots().get(6));
        p.onSequenceChange(2);
        assertEquals(8, p.maxSlots()); assertNull(p.slots().get(7));
    }
    @Test public void resonanceAtOneReplacesAllIndividualPowers() {
        SlotModel.Profile p = new SlotModel.Profile("fool");
        p.onSequenceChange(4); p.setSlot(6, "hanged_man", 9);
        p.onSequenceChange(1);
        assertEquals("resonance", p.mode());
        assertEquals(0, p.slots().size());
        assertFalse(p.active("fool", 9));
        for (int seq=0; seq<=9; seq++) assertTrue(p.active("paper_martyr", seq));
        p.onSequenceChange(0);
        assertTrue(p.active("paper_martyr", 0));
    }
    @Test public void invalidAndDuplicatePersistedSlotsAreDropped() {
        SlotModel.Profile p = new SlotModel.Profile("fool"); p.onSequenceChange(4);
        p.restoreSlots(List.of(new SlotModel.Choice("sun",9),
            new SlotModel.Choice("fool",9),new SlotModel.Choice("fool",9),
            new SlotModel.Choice("fool",3)));
        assertNull(p.slots().get(0));
        assertNotNull(p.slots().get(1));
        assertNull(p.slots().get(2));
        assertNull(p.slots().get(3));
    }
}
