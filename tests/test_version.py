from meridian.version import __version__, version_label


def test_canonical_version_number():
    assert __version__ == "3.2.0"


def test_version_label_includes_product_name():
    assert version_label() == "MERIDIAN 3.2.0"
