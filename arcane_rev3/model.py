"""Pure, immutable state rules from the Rev3 handbook (not an in-game runtime)."""
from dataclasses import dataclass, replace

PATHWAYS = (
    'fool', 'magician', 'high_priestess', 'empress', 'emperor',
    'hierophant', 'lovers', 'chariot', 'strength', 'hermit',
    'wheel_of_fortune', 'justice', 'hanged_man', 'death', 'temperance',
    'devil', 'tower', 'star', 'moon', 'sun', 'judgement', 'world',
)
# Rev3 Part B: fixed, disjoint pairs. These replace V3's earlier pairings.
PAIRS = (
    ('fool', 'hanged_man', 'paper_martyr'),
    ('world', 'justice', 'marked_verdict'),
    ('hermit', 'chariot', 'burning_archive'),
    ('death', 'tower', 'crumbling_reaper'),
    ('magician', 'strength', 'impossible_fist'),
    ('emperor', 'lovers', 'benevolent_crown'),
    ('devil', 'judgement', 'binding_contract'),
    ('star', 'empress', 'starless_poison'),
    ('sun', 'moon', 'eclipse'),
    ('temperance', 'hierophant', 'walking_sanctuary'),
    ('high_priestess', 'wheel_of_fortune', 'loaded_dice'),
)
PARTNER = {a: b for a, b, _ in PAIRS} | {b: a for a, b, _ in PAIRS}
RESONANCE = {a: r for a, b, r in PAIRS} | {b: r for a, b, r in PAIRS}
assert set(PATHWAYS) == set(PARTNER) and len(PARTNER) == len(PATHWAYS)


class InvalidSlot(ValueError):
    """Rejected player-owned slot or progression operation."""


@dataclass(frozen=True)
class State:
    primary: str
    sequence: int
    slots: tuple[tuple[str, int] | None, ...]
    secondary: str | None = None

    def __post_init__(self):
        if self.primary not in PARTNER or not isinstance(self.sequence, int) or not 0 <= self.sequence <= 9:
            raise InvalidSlot('invalid primary/sequence')
        if self.secondary != (PARTNER[self.primary] if self.sequence <= 4 else None):
            raise InvalidSlot('unregistered or prematurely unlocked second pathway')
        if len(self.slots) != self.maximum:
            raise InvalidSlot('slot count does not match sequence')
        seen = set()
        for item in self.slots:
            if item is None:
                continue
            pathway, seq = item
            if pathway not in self.available_pathways or not self.sequence <= seq <= 9:
                raise InvalidSlot('locked pathway or sequence')
            if item in seen:
                raise InvalidSlot('duplicate sequence kit')
            seen.add(item)
        if self.mode == 'single' and self.slots != self._auto_single():
            raise InvalidSlot('single pathway slots must auto-fill')

    @classmethod
    def start(cls, primary: str) -> 'State':
        return cls(primary=primary, sequence=9, slots=((primary, 9),))

    @property
    def mode(self) -> str:
        return 'single' if self.sequence >= 5 else 'slot' if self.sequence >= 2 else 'resonance'

    @property
    def maximum(self) -> int:
        return 0 if self.sequence <= 1 else 10 - self.sequence

    @property
    def available_pathways(self) -> tuple[str, ...]:
        return (self.primary,) if self.secondary is None else (self.primary, self.secondary)

    def _auto_single(self) -> tuple[tuple[str, int], ...]:
        return tuple((self.primary, seq) for seq in range(9, self.sequence - 1, -1))

    def ascend(self) -> 'State':
        """Pure mode transition; real acting/ritual checks must wrap this call in the runtime."""
        if self.sequence == 0:
            raise InvalidSlot('already Sequence 0')
        next_seq = self.sequence - 1
        if next_seq >= 5:
            slots = self.slots + ((self.primary, next_seq),)
        elif next_seq >= 2:
            slots = self.slots + (None,)
        else:
            slots = ()
        return State(primary=self.primary, secondary=PARTNER[self.primary] if next_seq <= 4 else None,
                     sequence=next_seq, slots=slots)

    def _require_index(self, index: int) -> None:
        if self.mode != 'slot' or not isinstance(index, int) or not 1 <= index <= self.maximum:
            raise InvalidSlot('slot is not editable/unlocked')

    def assign(self, index: int, pathway: str, sequence: int) -> 'State':
        self._require_index(index)
        if pathway not in self.available_pathways or not isinstance(sequence, int) or not self.sequence <= sequence <= 9:
            raise InvalidSlot('unregistered pathway or locked sequence')
        chosen = (pathway, sequence)
        if chosen in (slot for i, slot in enumerate(self.slots, 1) if i != index):
            raise InvalidSlot('already assigned in another slot')
        slots = list(self.slots)
        slots[index - 1] = chosen
        return replace(self, slots=tuple(slots))

    def clear(self, index: int) -> 'State':
        self._require_index(index)
        slots = list(self.slots)
        slots[index - 1] = None
        return replace(self, slots=tuple(slots))

    def swap(self, first: int, second: int) -> 'State':
        self._require_index(first)
        self._require_index(second)
        slots = list(self.slots)
        slots[first - 1], slots[second - 1] = slots[second - 1], slots[first - 1]
        return replace(self, slots=tuple(slots))

    def auto(self) -> 'State':
        if self.mode != 'slot':
            raise InvalidSlot('only slot mode supports customization')
        return replace(self, slots=tuple((self.primary, seq) for seq in range(9, self.sequence - 1, -1)))

    def reset(self) -> 'State':
        if self.mode != 'slot':
            raise InvalidSlot('only slot mode supports customization')
        # Restore the state of the Seq5->4 transition: first five primary kits, new slots empty.
        initial = tuple((self.primary, seq) for seq in (9, 8, 7, 6, 5))
        return replace(self, slots=initial + (None,) * (self.maximum - len(initial)))

    def active_kits(self) -> tuple[tuple[str, int], ...]:
        if self.mode == 'resonance':
            return tuple((RESONANCE[self.primary], seq) for seq in range(9, -1, -1))
        return tuple(slot for slot in self.slots if slot is not None)
