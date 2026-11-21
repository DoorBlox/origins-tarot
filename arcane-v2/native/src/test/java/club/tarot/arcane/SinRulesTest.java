package club.tarot.arcane;
import static org.junit.Assert.*;
import org.junit.Test;

public class SinRulesTest {
 @Test public void hangedManAbsorbsQuarterDamageAndCapsAtSixteen() {
   assertEquals(2f,SinRules.absorb(0f,8f,16f,false),0.0001);
   assertEquals(16f,SinRules.absorb(15f,8f,16f,false),0.0001);
   assertEquals(9f,SinRules.absorb(1f,8f,16f,true),0.0001);
 }
 @Test public void resonantCapStartsEightThenRisesTwelve() {
   assertEquals(8f,SinRules.capacity(true,false,false),0.0001);
   assertEquals(12f,SinRules.capacity(true,true,false),0.0001);
   assertEquals(Float.POSITIVE_INFINITY,SinRules.capacity(true,true,true),0.0001);
   assertEquals(16f,SinRules.capacity(false,false,false),0.0001);
 }
 @Test public void burdenBurstReturnsSinForDamageAndHealsItsFraction() {
   assertEquals(8f,SinRules.burstDamage(8f),0.0001);
   assertEquals(4f,SinRules.burstHeal(8f,false),0.0001);
   assertEquals(6f,SinRules.burstHeal(8f,true),0.0001);
   assertEquals(80f,SinRules.explosion(130f),0.0001);
 }
 @Test public void sinNeverGoesNegativeWhenTransferring() {
   assertEquals(0f,SinRules.consume(2f,3f),0.0001);
   assertEquals(4f,SinRules.consume(7f,3f),0.0001);
 }
 @Test public void naturalRegenerationThresholdsFollowRevTwo() {
   assertEquals(16f,SinRules.regenLimit(false,false),0.0001);
   assertEquals(18f,SinRules.regenLimit(true,false),0.0001);
   assertEquals(20f,SinRules.regenLimit(true,true),0.0001);
 }
}
