from shiva_deployer.commandline import VirtualEnv
from shiva_deployer.exceptions import ShouldNotDeploy
from shiva_deployer.tools import nonblocking_lock


class BasicDeployment(object):
    """Minimal abstract class that must be parametrized to have a successful
    Shiva deployment

    """
    def __init__(self, argv):
        """Squirrel away the commandline args, from which our instance methods
        will derive anything else they need to know.

        :arg argv: A sys.argv-style list, starting with the first actual
            argument not the executable

        """
        self.argv = argv

    # ---------------- Commonly overridden: ----------------

    def get_lock_name(self):
        """Return the name of the lock to take out.

        This Deployment will cause any other Deployments which try to run
        concurrently to quietly abort.

        This default implementation returns the name of the repository: that
        is, the name of the folder containing the "deployment" folder.

        """
        raise NotImplementedError  # TODO: return repo name by default

    def check_out(self):
        """Check out the version of the project we should deploy, and return
        its absolute path on disk."""
        raise NotImplementedError

    def install(self):
        """Build and install the project.

        This is run from the new checkout.

        """
        # This can't work out where the source to install is based on the
        # class's module's location, because what if they imported the class
        # from somewhere else for some odd reason? We need to figure it out
        # based on the path to the deploy.py script in self.argv.
        raise NotImplementedError

    # ---------------- Not commonly overridden: ----------------

    def deploy_if_appropriate(self):
        """Deploy a new build if we should."""
        # Makes a deployment venv. This is the one to get out of the way of
        # project requirments so the deploy script can have its own. If there
        # was already a venv from last time, finds it (to save disk IO).
        deployment_venv = VirtualEnv('/temp/dir/deployment1')
        # Peep- or pip-installs dxr/deployment/requirements.txt (should include shiva).

        # Runs `venv/python -m shiva_the_deployer get_lock_name /path/to/deploy.py`
        lock_name = deployment_venv.run_shiva('get_lock_name')  # TODO: Pass through the argv I received here and at every other invocation of run_shiva.

        # Takes out a nonblocking (fallthrough) lock. Maybe make it blocking optionally for pushbutton deploys. If it changes from one binary call to the next, take out both locks to be safe.
        with nonblocking_lock('shiva-deployer-%s' % lock_name) as got_lock:
            if got_lock:
                try:
                    # Runs `venv/python dxr/deployment/deploy.py check_out`, which checks out the latest good version of the project and outputs project:/path/to/checkout.
                    old_checkout_path = ''
                    # Keep checking things out until they stabilize. This
                    # allows us to follow a moving repo from one location to
                    # another, even if it moved multiple times (and had its
                    # check_out() updated) since the current on-disk repo was
                    # checked out.
                    while checkout_path != old_checkout_path:
                        checkout_path = deployment_venv.run_shiva('check_out')
                        deployment_venv = VirtualEnv('some temp dir')
                        # Peep- or pip-install checkout_path/deployment/requirements.txt
                        # (We can skip the previous 2 steps if the requirements are unchanged. A pip download cache should make none of this matter much.)

                    # Runs `venv/python /path/to/checkout/.../deploy.py`, which builds the project as contained in the checkout and installs it
                    deployment_venv.run_shiva('install')
                except ShouldNotDeploy:
                    pass
                else:
                    # if not self.passes_smoke_test():
                    #     self.rollback()
                    pass


class FancyDeployment(BasicDeployment):
    """A heavier inversion-of-control framework than BasicDeployment which
    saves effort for most projects

    """
    # TODO: How the heck are these args going to get passed in? Shiva doesn't know what to pass in. How about we pass in argv and leave the rest to the subclasser. We can implement parsing of a few common options, or something, in this class.
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

    @classmethod
    def new_from_command_line(cls):
        """Handle command-line munging, and pass off control to the interesting
        stuff.

        """
        # TODO: Replace with a generic UI.
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
        non_none_options = dict((k, getattr(options, k)) for k in
                                (o.dest for o in parser.option_list if o.dest)
                                if getattr(options, k))
        try:
            return cls(*args, **non_none_options).deploy_if_appropriate()
        except TypeError:
            parser.print_usage()  # TODO: return or raise something

    def rev_to_deploy(self):
        """Return the VCS revision identifier of the version we should
        deploy.

        If we shouldn't deploy for some reason (like if we're already at the
        newest revision or nobody has pressed the Deploy button since the last
        deploy), raise ShouldNotDeploy.

        """
        # Raise ShouldNotDeploy if we're already up to date, which means we'll
        # have to be able to find and get the rev of the currently deployed
        # version.

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
