package club.tarot.arcane;
/** Pure-source rules for permanent drawback and target permission. */
public final class StarEmpressRules {
 private StarEmpressRules(){}
 public static float exposedArrowMultiplier(boolean exposedToSun,boolean projectile){
     return exposedToSun&&projectile?1.25f:1f;
 }
}
