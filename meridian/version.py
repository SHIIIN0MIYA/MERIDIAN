__version__ = "3.2.0"


def version_label() -> str:
    """Device label for the status bar, with the running version.

    This used to return the bare constant ``"MERIDIAN"``, so the version --
    which ``tools/check_release.py`` already reads and checks -- never appeared
    anywhere in the UI.
    """
    return f"MERIDIAN {__version__}"
