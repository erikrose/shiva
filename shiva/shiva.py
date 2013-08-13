"""Reasonably generic [continuously] deployment framework"""
# TODO: Update the deployment script first, and use the new version to deploy.
# That way, each version is deployed by the deployment script that ships with
# it.

from contextlib import contextmanager
from optparse import OptionParser
import os
from os import chdir, O_CREAT, O_EXCL, remove, getcwd
from os.path import join
from pipes import quote
from subprocess import check_output
from tempfile import gettempdir


def main():
    """Handle command-line munging, and pass off control to the interesting
    stuff."""
    parser = OptionParser(
        usage='usage: %prog [options] <staging | prod>',
        description='Deploy a new version of DXR.')
    parser.add_option('-b', '--base', dest='base_path',
                      help='Path to the dir containing the builds, instances, '
                           'and deployment links')
    parser.add_option('-p', '--python', dest='python_path',
                      help='Path to the Python executable on which to base the'
                           ' virtualenvs')
    parser.add_option('-e', '--repo', dest='repo',
                      help='URL of the git repo from which to download DXR. '
                           'Use HTTPS if possible to ward off spoofing.')
    parser.add_option('-r', '--rev', dest='manual_rev',
                      help='A hash of the revision to deploy. Defaults to the '
                           'last successful Jenkins build on master.')

    options, args = parser.parse_args()
    if len(args) == 1:
        non_none_options = dict((k, getattr(options, k)) for k in
                                (o.dest for o in parser.option_list if o.dest)
                                if getattr(options, k))
        Deployment(args[0], **non_none_options).deploy_if_appropriate()
    else:
        parser.print_usage()


class Deployment(object):
    """A little inversion-of-control framework for deployments

    Maybe someday we'll plug in methods to handle a different project.

    """
    def __init__(self,
                 kind,
                 manual_rev=None,
                 # The rest of these kwargs might change from subclass to
                 # subclass, but they should stay this way 90% of the time.
                 # This bothers me from a subclass-semantics point of view.
                 base_path='/data',
                 python_path='/usr/bin/python2.7',
                 repo='https://github.com/mozilla/dxr.git'):
        """Construct.

        :arg kind: The type of deployment this is, either "staging" or "prod".
            Affects only some folder names.
        :arg manual_rev: A hash of the revision to deploy. Defaults to
            something reasonable, like the last successful Jenkins build on
            master.
        :arg base_path: Path to the dir containing the builds, deployment
            links, and any other necessities, like DXR indices. As an example,
            DXR's base path contains these items:

            * builds - A folder of builds, including the current production one
            * dxr-prod - A symlink to the current production build
            * instances - A folder of DXR instances organized according to
              format version

        :arg python_path: Path to the Python executable on which to base the
            virtualenvs
        :arg repo: URL of the [git] repo from which to download DXR. Use HTTPS
            if possible to ward off spoofing.

        """
        self.kind = kind
        self.base_path = base_path
        self.python_path = python_path
        self.repo = repo
        self.manual_rev = manual_rev

    def rev_to_deploy(self):
        """Return the VCS revision identifier of the version we should
        deploy.

        If we shouldn't deploy for some reason (like if we're already at the
        newest revision or nobody has pressed the Deploy button since the last
        deploy), raise ShouldNotDeploy.

        """

    def build(self, rev):
        """Create and return the path of a new directory containing a new
        build of the given revision of the source.

        A "build" is probably just a virtualenv named after [some excerpt of]
        its commit hash.

        If it turns out we shouldn't deploy this build after all (perhaps
        because some additional data yielded by an asynchronous build process
        isn't yet available in the new format) but there hasn't been a
        programming error that would warrant a more serious exception, raise
        ShouldNotDeploy.

        """

    def install(self, new_build_path):
        """Install a build at ``self.deployment_path``.

        Avoid race conditions as much as possible. If it turns out we should
        not deploy for some anticipated reason, raise ShouldNotDeploy.

        """

    def _kind_of_deployment(self):
        """Return a string unique across deployments that should not run
        simultaneously.

        This is used as part of the name of a lockfile to prevent concurrent
        runs of (for example) the same deployment process.

        """
        return 'any-deployment'

    def deploy_if_appropriate(self):
        """Deploy a new build if we should."""
        with nonblocking_lock(self._kind_of_deployment()) as got_lock:
            if got_lock:
                try:
                    rev = self.manual_rev or self.rev_to_deploy()
                    new_build_path = self.build(rev)
                    self.install(new_build_path)
                except ShouldNotDeploy:
                    pass
                else:
                    # if not self.passes_smoke_test():
                    #     self.rollback()
                    pass


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


class ShouldNotDeploy(Exception):
    """We should not deploy this build at the moment, though there was no
    programming error."""


if __name__ == '__main__':
    main()
