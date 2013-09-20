"""The shiva command-line tool, the top-level entrypoint for touching off a
deployment"""

from optparse import OptionParser
from os.path import basename, join
import pickle
from subprocess import check_output
import sys
from sys import argv, executable, stderr

from virtualenv import create_environment, path_locations

from shiva_deployer.exceptions import ShouldNotDeploy


def main():
    """Wrap the operative routine to make it more testable.

    This is the entry point for the setuptools entrypoint.

    """
    status, output = inner_main(argv[1:])
    print output
    return status


def inner_main(argv):
    """After creating a virtualenv with the proper requirements, run a
    deployment script to pull down the latest good version of a project, then
    install it using that new version of the deployment script.

    Return a tuple of (status code, stdout output).

    :arg argv: A sys.argv-style list, starting with the first actual argument,
        not the executable

    """
    parser = OptionParser(
        usage='usage: %prog /some/dir/deploy.py [more args and options]',
        description='Deploy a new version of the project using the deploy.py '
                    'script, run in a virtualenv having the packages specified'
                    ' by /some/dir/requirements.txt.\n\nThe given deploy.py on disk is used only to bootstrap; the actual version that is used to do the deployment (and the actual requirements.txt used) is the latest good version, as determined by the local deploy.py.')
    parser.add_option('--shiva-subcommand',
                      dest='subcommand',
                      default='deploy',
                      help='A secret option used internally')
    options, args = parser.parse_args(args=argv)
    if len(args) >= 1:
        deploy_script_path = args[0]

        # Import-ish deploy.py (which saves some sys.path twiddling and
        # collision with other modules named "deploy"):
        deploy = {}  # empty module namespace
        execfile(deploy_script_path, deploy)

        # Instantiate deploy.py's Deployment class, passing it the
        # commandline args:
        deployment = deploy['Deployment'](argv)

        if options.subcommand in ('get_lock_name', 'check_out', 'install'):
            try:
                # Return the result of the subcommand func. We mash the
                # returned value into a string via pickle and print it to
                # stdout so the parent process can pick it up.
                output = pickle.dumps(getattr(deployment,
                                              options.subcommand)())
            except ShouldNotDeploy as exc:
                output = pickle.dumps(exc)
            # If a different exception, explode here, exiting with a non-zero.

            # But if all goes well, be happy:
            return 0, output
        elif options.subcommand == 'deploy':
            # 'deploy' is the only public command. It does not print a pickle.
            deployment.deploy_if_appropriate()
            return 0, ''
    parser.print_usage(stderr)
    return 2, ''


def wake_pickle(value):
    """Unpickle a value and return it. If it is a ShouldNotDeploy exception,
    raise it.

    """
    # We use the default, ASCII pickle format to communicate between private
    # shiva subcommands and the parent process. It saves us reinventing
    # serialization of ShouldNotDeploy instances.
    result = pickle.loads(value)
    if isinstance(result, ShouldNotDeploy):
        raise result
    # Otherwise, the subprocess will exit with a non-zero, and run() will raise
    # a CalledProcessError.
    return result


class VirtualEnv(object):
    def __init__(self, dir):
        """Construct

        :arg dir: The path of the new virtualenv

        """
        create_environment(dir,
                           site_packages=False,
                           clear=False,
                           never_download=True)
        home_dir, lib_dir, inc_dir, bin_dir = path_locations(dir)
        self.python_path = join(bin_dir, basename(sys.executable))

    def run_shiva(self, deploy_script, arg_string):
        """Run a shiva subcommand in a new process, under this virtualenv.

        Translate from the pickle the command returns into native
        representation.

        """
        # Not run(), so we can support spaces in paths
        return wake_pickle(check_output([self.python_path, '-m',
                                        'shiva_deployer', deploy_script,
                                        arg_string]))
