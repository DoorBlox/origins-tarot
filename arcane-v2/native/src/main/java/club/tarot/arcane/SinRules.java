package club.tarot.arcane;
/** Pure formula contracts used by the native Sin combat engine. Values are HP (not hearts). */
public final class SinRules {
 private SinRules() {}
 public static float absorb(float stored,float damage,float cap,boolean fullConversion) {
    return Math.min(cap,Math.max(0f,stored)+Math.max(0f,damage)*(fullConversion?1f:.25f));
 }
 public static float capacity(boolean resonance,boolean trickster,boolean unbound) {
    if(unbound) return Float.POSITIVE_INFINITY;
    if(resonance) return trickster?12f:8f;
    return 16f;
 }
 public static float burstDamage(float stored) { return Math.max(0f,stored); }
 public static float burstHeal(float stored,boolean overflow) { return Math.max(0f,stored)*(overflow?.75f:.5f); }
 public static float explosion(float stored) { return Math.min(80f,Math.max(0f,stored)); }
 public static float consume(float stored,float spend) { return Math.max(0f,stored-Math.max(0f,spend)); }
 public static float regenLimit(boolean killUnlock,boolean specialUnlock) {
    return specialUnlock?20f:(killUnlock?18f:16f);
 }
}
