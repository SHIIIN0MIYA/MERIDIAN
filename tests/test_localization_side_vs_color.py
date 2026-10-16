"""V-4 / R3.1: ``RED``/``BLUE`` must keep COLOR semantics, sides get ``SIDE_*`` keys.

The ZH table historically defined ``RED``/``BLUE`` twice: once as colours
(``红色``/``蓝色``) and once, later and therefore winning, as tank-duel sides
(``红方``/``蓝方``).  That silently changed the meaning of the shared skin/brick
colour option labels in snake.py and breakout.py.

The fix keeps colour semantics on ``RED``/``BLUE`` and introduces dedicated
``SIDE_RED``/``SIDE_BLUE`` keys for the tank-duel call sites.
"""

from meridian.localization import ZH, set_language, translate


def test_red_blue_keep_color_semantics():
    set_language("zh_hans")

    assert translate("RED") == "红色"
    assert translate("BLUE") == "蓝色"


def test_side_keys_carry_faction_semantics():
    set_language("zh_hans")

    assert translate("SIDE_RED") == "红方"
    assert translate("SIDE_BLUE") == "蓝方"


def test_side_keys_are_real_table_entries():
    """The side keys must live in the ZH table, not be EN fallbacks."""
    assert "SIDE_RED" in ZH
    assert "SIDE_BLUE" in ZH


def test_win_labels_still_use_faction_semantics():
    set_language("zh_hans")

    assert translate("RED WINS") == "红方胜利"
    assert translate("BLUE WINS") == "蓝方胜利"
