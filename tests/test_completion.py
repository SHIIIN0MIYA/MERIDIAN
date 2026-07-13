from meridian.completion import WORLD_IDS, combine_completion, global_completion, world_completion
from meridian.persistence import default_data


def test_confirmed_completion_weights():
    assert combine_completion(100, 0, 0) == 40
    assert combine_completion(0, 100, 0) == 35
    assert combine_completion(0, 0, 100) == 25
    assert combine_completion(100, 100, 100) == 100


def test_old_empty_save_is_safe_and_eight_worlds_are_equal():
    data = default_data()
    assert global_completion(data) == 0
    assert len(WORLD_IDS) == 8
    assert all(world_completion(world, data).total == 0 for world in WORLD_IDS)


def test_tank_item_variety_boundary_counts_as_objective():
    data = default_data()
    stats = data["statistics"]["tank"]
    for item in ("repair", "shield", "speed", "mine", "emp", "piercing", "smoke"):
        stats[f"{item}_uses"] = 1
    assert world_completion("tank", data).objectives == 0
    stats["warp_uses"] = 1
    assert world_completion("tank", data).objectives == 25
