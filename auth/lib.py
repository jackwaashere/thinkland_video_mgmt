from __future__ import print_function
import sys
import signal
from contextlib import contextmanager

@contextmanager
def default_sigint():
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, original_sigint_handler)
        
       
def debug(obj, fd=sys.stderr):
    """Write obj to standard error."""
    print(obj, file=fd)


