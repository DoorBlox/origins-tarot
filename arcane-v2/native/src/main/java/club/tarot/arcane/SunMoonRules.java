package club.tarot.arcane;
/** Pure combat rate policy matching the 2400t Sun capstone. */
public final class SunMoonRules {
 private SunMoonRules(){}
 public static float fixedSunPulse(boolean undead,boolean enemyPlayer){
  return undead?6f:enemyPlayer?1f:0f;
 }
}
