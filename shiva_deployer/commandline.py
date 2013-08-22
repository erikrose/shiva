"""The shiva command-line tool, the top-level entrypoint for touching off a
deployment"""

from optparse import OptionParser
import pickle
from sys import argv, executable, stderr

from shiva_deployer import run, ShouldNotDeploy


def run_deploy_script(arg_string):
    """Run a private shiva command in a new process.

    Translate from the packed JSON the command returns into native
    representation.

    """
    # We use the default, ASCII pickle format to communicate between private
    # shiva subcommands and the parent process. It saves us reinventing
    # serialization of ShouldNotDeploy instances.
    result = pickle.loads(run('venv/python -m shiva_the_deployer /path/to/deploy.py %s' % arg_string)
    if isinstance(result, ShouldNotDeploy):
        raise result
    # Otherwise, the subprocess will exit with a non-zero, and run() will raise
    # a CalledProcessError.
    return result


def main():
    """After creating a virtualenv with the proper requirements, run a
    deployment script to pull down the latest good version of a project, then
    install it using that new version of the deployment script."""
    parser = OptionParser(
        usage='usage: %prog /some/dir/deploy.py [args options]',
        description='Deploy a new version of the project using the deploy.py '
                    'script, run in a virtualenv having the packages specified'
                    ' by /some/dir/requirements.txt.\n\nThe given deploy.py on disk is used only to bootstrap; the actual version that is used to do the deployment (and the actual requirements.txt used) is the latest good version, as determined by the local deploy.py.')
    parser.add_option('--shiva-subcommand',
                      dest='subcommand',
                      default='deploy',
                      help='A secret option used internally')
    args, options = parse.parse_args()
    if len(args) >= 1:
        if options.subcommand in ('get_lock_name', 'check_out', 'install'):
            # Subcommands either return a non-zero status code, return a JSON-dict result, or return a JSON-dict representation of ShouldNotDeploy.
            try:
                # Twiddle sys.path, import Deployment from deploy.py, and instantiate it.

                # and return the result of its $subcommand func. We mash the
                # returned value into a string via pickle and print it to stdout so
                # the parent process can pick it up.
                print pickle.dumps(getattr(deployment, options.subcommand)())
            except ShouldNotDeploy as exc:
                print pickle.dumps(exc)
            # Otherwise, explode and exit with a non-zero status.
            return 0
        elif options.subcommand == 'deploy':
            # 'deploy' is the only public command. It does not print a pickle.
            deployment.deploy_if_appropriate()
            return 0
    parser.print_usage()
    return 2
