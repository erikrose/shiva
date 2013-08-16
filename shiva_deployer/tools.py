"""Building blocks to use in your deployment script"""

from contextlib import contextmanager
import os
from os import chdir, O_CREAT, O_EXCL, remove, getcwd
from os.path import join
from pipes import quote
from subprocess import check_output
from tempfile import gettempdir


def run(command, **kwargs):
    """Return the output of a command.

    Pass in any kind of shell-executable line you like, with one or more
    commands, pipes, etc. Any kwargs will be shell-escaped and then subbed into
    the command using ``format()``::

        >>> run('echo hi')
        "hi"
        >>> run('echo {name}', name='Fred')
        "Fred"

    This is optimized for callsite readability. Internalizing ``format()``
    keeps noise off the call. If you use named substitution tokens, individual
    commands are almost as readable as in a raw shell script. The command
    doesn't need to be read out of order, as with anonymous tokens.

    """
    output = check_output(
        command.format(**dict((k, quote(v)) for k, v in kwargs.iteritems())),
        shell=True)
    return output


@contextmanager
def cd(path):
    """Change the working dir on enter, and change it back on exit."""
    old_dir = getcwd()
    chdir(path)
    yield
    chdir(old_dir)


@contextmanager
def nonblocking_lock(lock_name):
    """Context manager that acquires and releases a file-based lock.

    If it cannot immediately acquire it, it falls through and returns False.
    Otherwise, it returns True. I wish we had macros so we could just skip the
    "with" body.

    """
    lock_path = join(gettempdir(), lock_name + '.lock')
    try:
        fd = os.open(lock_path, O_CREAT | O_EXCL, 0644)
    except OSError:
        got = False
    else:
        got = True

    try:
        yield got
    finally:
        if got:
            os.close(fd)
            remove(lock_path)
