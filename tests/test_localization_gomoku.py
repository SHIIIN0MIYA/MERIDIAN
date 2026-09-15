from meridian.localization import set_language, translate


def test_gomoku_status_strings_are_fully_localized():
    set_language("zh_hans")

    assert translate("BLACK'S TURN") == "轮到黑方"
    assert translate("WHITE'S TURN") == "轮到白方"
    assert translate("PLACE A STONE") == "请落子"
    assert translate("ROUND OVER") == "本局结束"
