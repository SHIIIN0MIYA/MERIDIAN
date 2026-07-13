from meridian.version import DEVELOPMENT_VERSION, __version__, version_label


def test_canonical_version_number():
    assert __version__ == "3.2.0"


def test_version_label_includes_product_name():
    assert DEVELOPMENT_VERSION == "3.3.0"
    assert version_label() == "MERIDIAN 3.3.0 DEV"
