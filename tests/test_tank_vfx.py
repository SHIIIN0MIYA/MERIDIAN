from meridian.tank_engine import EngineEvent
from meridian.tank_vfx import ITEM_EFFECT_KINDS, TankVfxState, consume_engine_events, update_vfx


def test_destroy_effect_density_respects_three_levels_but_keeps_score():
    counts = []
    for level in ("full", "reduced", "off"):
        state = TankVfxState()
        consume_engine_events(state, [EngineEvent("tank_destroyed", "blue", {"x": 3, "y": 4})], level, 7)
        counts.append(len(state.particles))
        assert state.score_popups
    assert counts[0] > counts[1] > counts[2]


def test_all_eight_items_have_distinct_effect_kinds_and_expire():
    assert len(ITEM_EFFECT_KINDS) == len(set(ITEM_EFFECT_KINDS.values())) == 8
    state = TankVfxState()
    events = [EngineEvent("item_used", "red", {"item": item, "x": 1, "y": 2}) for item in ITEM_EFFECT_KINDS]
    consume_engine_events(state, events, "off", 2)
    assert {effect["kind"] for effect in state.item_effects} == set(ITEM_EFFECT_KINDS.values())
    update_vfx(state, 1000)
    assert not state.item_effects
