import code
import rlcompleter
import readline

def interact(lock, locals, banner):
    """
    launches an interactive console.

    lock
        a mutex that will be locked whenever locals is accessed.
    locals
        the local variables in the interactive session
    banner
        banner that is displayed on loading
    """

    class LockedInteractiveConsole(code.InteractiveConsole):
        """
        modified code.InteractiveConsole with readline tab completion
        that respects lock.
        """
        def __init__(self, *k, **kw):
            class LockedRLCompleter(rlcompleter.Completer):
                """
                modified version of rlcompleter.Completer that
                respects lock.
                """
                def attr_matches(self, text):
                    with lock:
                        return super().attr_matches(text)
                def global_matches(self, text):
                    with lock:
                        return super().global_matches(text)
            readline.parse_and_bind("tab: complete")
            readline.set_completer(LockedRLCompleter(locals).complete)
            super().__init__(*k, **kw)

        def runsource(self, *k, **kw):
            with lock:
                return super().runsource(*k, **kw)

    LockedInteractiveConsole(locals).interact(banner)
