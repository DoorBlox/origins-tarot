package club.tarot.arcane;

/** Testable decisions separated from server-only domain/identity event handling. */
public final class CrownRules {
    private CrownRules() {}
    public static boolean blockMovement(boolean inDomain,boolean ownsDomain,boolean allowed){
        return inDomain&&!ownsDomain&&!allowed;
    }
    public static boolean separationActive(int aloneTicks){return aloneTicks>600;}
    public static float shieldDamageMultiplier(boolean shield,boolean improved){
        return !shield?1f:improved?.85f:.90f;
    }
}
