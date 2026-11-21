package club.tarot.arcane;
/** Explicit contract consent: no response is never interpreted as refusal. */
public final class ContractRules {
    private ContractRules() {}
    public static boolean penaltyPermitted(String decision){
        return "refuse".equals(decision);
    }
    public static boolean validOffer(boolean self,boolean online,long now,long expires){
        return !self && online && now<=expires;
    }
}
