// Batch 1: implemented pathways only. Extend on acceptance of each later batch.
// Every entry is a real power file; never put unimplemented abilities in this map.
global.TarotBatch1Registry = {
  source: 'tarot_slot',
  pairs: [
    ['fool','hanged_man','paper_martyr'],['world','justice','marked_verdict'],
    ['hermit','chariot','burning_archive'],['death','tower','crumbling_reaper'],
    ['magician','strength','impossible_fist'],['emperor','lovers','benevolent_crown'],
    ['devil','judgement','binding_contract'],['star','empress','starless_poison'],
    ['sun','moon','eclipse'],['temperance','hierophant','walking_sanctuary'],
    ['high_priestess','wheel_of_fortune','loaded_dice']
  ],
  complete: { fool:true },
  resonanceComplete: {},
  powers: {
    fool: {
      9: ['9_spirit_vision','9_clowns_mischief','9_spiritual_overload','9_full_faceless_disguise'],
      8: ['8_tricksters_favor'],
      7: ['7_stage_magician'],
      6: ['6_borrowed_face'],
      5: ['5_puppet_string'],
      4: ['4_tricksters_escape'],
      3: ['3_fools_bounty'],
      2: ['2_fools_gathering'],
      1: ['1_history_substitution','1_paper_figurine_substitute'],
      0: ['0_legend_of_the_fool']
    }
  },
  hostiles: ['zombie','skeleton','creeper','spider','cave_spider','enderman','witch','slime',
    'magma_cube','blaze','ghast','phantom','pillager','vindicator','evoker','ravager','vex',
    'drowned','husk','stray','wither_skeleton','piglin','piglin_brute','hoglin','zoglin',
    'zombified_piglin','guardian','elder_guardian','shulker','silverfish','endermite',
    'illusioner','wither','ender_dragon']
};
