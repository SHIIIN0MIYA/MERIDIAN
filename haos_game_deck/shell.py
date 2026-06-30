from .shell_boot import BootMixin
from .shell_desktop import DesktopMixin
from .shell_password import PasswordMixin
from .shell_transitions import TransitionMixin


class ShellMixin(BootMixin, DesktopMixin, PasswordMixin, TransitionMixin):
    pass
