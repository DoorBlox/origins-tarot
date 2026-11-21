package club.tarot.arcane;

/**
 * Acting costs inherited from the repository's existing V3 Path of Ascension
 * (progression/catalog.py), not from Rev 2/3's ability definition sheets.
 * The new native engine advances ONE shared Sequence for the registered pair.
 */
public final class AscensionRules {
    private AscensionRules() {}
    private static final int[] MARKS={0,6,5,4,4,3,3,2,2,1};
    public static int marksToAscend(int currentSequence) {
        if(currentSequence<=0 || currentSequence>9)
            throw new IllegalArgumentException("Cannot ascend from Sequence "+currentSequence);
        return MARKS[currentSequence];
    }
    public static boolean eligible(int marks,boolean atAltar,boolean safe,
                                   boolean offerings,int currentSequence) {
        return currentSequence>=1 && currentSequence<=9
            && marks>=MARKS[currentSequence] && atAltar && safe && offerings;
    }
}
