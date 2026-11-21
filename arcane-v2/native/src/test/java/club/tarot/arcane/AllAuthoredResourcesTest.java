package club.tarot.arcane;

import static org.junit.Assert.*;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.Test;

/** Cross-batch packaging contract; independent of Minecraft client rendering. */
public final class AllAuthoredResourcesTest {
    private JsonObject read(String path) throws Exception {
        InputStream stream=getClass().getClassLoader().getResourceAsStream(path);
        assertNotNull("Resource missing: "+path,stream);
        try(InputStream source=stream;
            InputStreamReader reader=new InputStreamReader(source,StandardCharsets.UTF_8)){
            return JsonParser.parseReader(reader).getAsJsonObject();
        }
    }
    @Test public void everyRegisteredSequenceHasAValidPackagedJson() throws Exception {
        Set<String> keys=new HashSet<>();
        Set<String> profiles=new HashSet<>(SlotModel.PAIRS.keySet());
        profiles.addAll(SlotModel.RESONANCES.values());
        for(String pathway:profiles){
            if(!AbilityRegistry.implemented(pathway,9))continue;
            for(int s=0;s<=9;s++){
                assertTrue("Missing "+pathway+"/"+s,AbilityRegistry.implemented(pathway,s));
                for(String id:AbilityRegistry.forSequence(pathway,s)){
                    assertTrue("Duplicate ID "+id,keys.add(id));
                    JsonObject data=read("data/tarot/powers/"+id.substring(6)+".json");
                    assertTrue("Missing Origins type for "+id,data.has("type"));
                }
            }
        }
        assertEquals("Authored ability count changed; update coverage deliberately",315,keys.size());
    }
    @Test public void noSequenceKitCanBecomeAnUnremovableOriginPower() throws Exception {
        Set<String> names=new HashSet<>(SlotModel.PAIRS.keySet());
        names.addAll(SlotModel.RESONANCES.values());
        for(String pathway:names){
            if(!AbilityRegistry.implemented(pathway,9))continue;
            JsonObject origin=read("data/tarot/origins/"+pathway+".json");
            JsonArray powers=origin.getAsJsonArray("powers");
            assertNotNull(pathway,powers);
            for(int i=0;i<powers.size();i++){
                String id=powers.get(i).getAsString();
                assertTrue("Origin owns slot kit "+id,
                    id.endsWith("/marker")||id.contains("/identity_"));
                assertFalse("Sequence kit statically inherited "+id,
                    id.matches("tarot:[^/]+/[0-9]_.+"));
                read("data/tarot/powers/"+id.substring(6)+".json");
            }
        }
    }
    @Test public void onlyIndividualPathwaysAppearAsCharacterCreationChoices() throws Exception {
        JsonObject originLayer=read("data/origins/origin_layers/origin.json");
        Set<String> choices=new HashSet<>();
        for(var element:originLayer.getAsJsonArray("origins"))
            assertTrue("Duplicate selection",choices.add(element.getAsString()));
        for(String card:SlotModel.PAIRS.keySet())
            if(AbilityRegistry.implemented(card,9))
                assertTrue("Missing choice "+card,choices.contains("tarot:"+card));
        for(String fusion:SlotModel.RESONANCES.values())
            assertFalse("Resonance must activate at Sequence 1",choices.contains("tarot:"+fusion));
    }
}
