"""Pure rules reference for state invariants; runtime is generated Minecraft functions."""
from dataclasses import dataclass, replace
from .catalog import ACT_MARKS, SLUG_TO_ID, PAIRS

class RuleError(ValueError):
    pass

@dataclass(frozen=True)
class State:
    primary: str
    secondary: str | None = None
    primary_seq: int = 9
    secondary_seq: int = 9
    active: str | None = None
    primary_marks: int = 0
    secondary_marks: int = 0
    trial: str | None = None
    trial_marks: int = 0
    visited_nether: bool = False
    visited_end: bool = False
    stability: int = 100

    def __post_init__(self):
        if self.primary not in SLUG_TO_ID: raise RuleError('unknown primary')
        if self.secondary is not None and (self.secondary not in SLUG_TO_ID or self.secondary==self.primary):
            raise RuleError('invalid secondary')
        if not 0 <= self.stability <= 100:raise RuleError('invalid stability')
        if not 0 <= self.primary_seq <= 9 or not 0 <= self.secondary_seq <=9:
            raise RuleError('invalid sequence')
        if self.active is None:object.__setattr__(self,'active',self.primary)
        if self.active not in {self.primary,self.secondary}:raise RuleError('active must be unlocked')

    @classmethod
    def new(cls,slug):return cls(primary=slug)

    @property
    def active_seq(self):return self.primary_seq if self.active==self.primary else self.secondary_seq
    @property
    def echo(self):
        if self.secondary is None or self.active_seq>2:return None
        return self.secondary if self.active==self.primary else self.primary
    @property
    def resonance(self):
        if self.secondary is None or self.active_seq>1:return None
        for a,b,name in PAIRS:
            if {a,b}=={self.primary,self.secondary}:return name
        return 'unbound_resonance'
    def add_acting(self,amount=1):
        if amount<0:raise RuleError('negative acting')
        key='primary_marks' if self.active==self.primary else 'secondary_marks'
        return replace(self,stability=min(100,self.stability+4*amount),**{key:min(20,getattr(self,key)+amount)})
    def ascend(self,has_altar,has_ingredients):
        seq=self.active_seq
        if seq==0:raise RuleError('already at seq0')
        if not has_altar or not has_ingredients or self.stability<25:raise RuleError('ritual conditions unmet')
        key='primary_marks' if self.active==self.primary else 'secondary_marks'
        if getattr(self,key)<ACT_MARKS[seq]:raise RuleError('insufficient acting')
        seqkey='primary_seq' if self.active==self.primary else 'secondary_seq'
        return replace(self,stability=max(0,self.stability-12),**{seqkey:seq-1,key:getattr(self,key)-ACT_MARKS[seq]})
    def visit(self,dim):
        if dim=='nether':return replace(self,visited_nether=True)
        if dim=='end':return replace(self,visited_end=True)
        raise RuleError('unknown dimension')
    def begin_trial(self,slug):
        if self.primary_seq>4 or not self.visited_nether or not self.visited_end:
            raise RuleError('no second awakening yet')
        if self.secondary or self.trial:raise RuleError('already unlocked/committed')
        if slug not in SLUG_TO_ID or slug==self.primary:raise RuleError('invalid target')
        return replace(self,trial=slug,trial_marks=0)
    def add_trial_acting(self,n=1):
        if not self.trial:raise RuleError('no trial')
        return replace(self,trial_marks=min(4,self.trial_marks+n))
    def unlock_second(self,has_altar,has_ingredients):
        if not self.trial or self.trial_marks<4 or not has_altar or not has_ingredients:
            raise RuleError('trial incomplete')
        return replace(self,secondary=self.trial,secondary_seq=9,trial=None,trial_marks=0)
    def swap(self,target,at_altar,combat,flying,grounded,cooldown):
        if self.secondary is None or target not in (self.primary,self.secondary) or target==self.active:
            raise RuleError('invalid swap target')
        if self.primary_seq>4:raise RuleError('not attuned')
        if self.primary_seq>3 and not at_altar:raise RuleError('altar required before seq3')
        if combat or flying or not grounded or cooldown>0:raise RuleError('unsafe swap')
        return replace(self,active=target,stability=max(0,self.stability-4))

    def meditate(self,at_altar,has_amethyst,cooldown):
        if not at_altar or not has_amethyst or cooldown>0 or self.stability>=100:
            raise RuleError('meditation unavailable')
        return replace(self,stability=min(100,self.stability+30))
