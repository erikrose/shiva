"""The shiva command-line tool, the top-level entrypoint for touching off a
deployment"""

from optparse import OptionParser
from sys import argv, executable


def main():
    """After creating a virtualenv with the proper requirements, run a
    deployment script to pull down the latest good version of a project, then
    install it using that new version of the deployment script."""
    parser = OptionParser(
        usage='usage: %prog /path/to/deployment/dir [args options]',
        description='Deploy a new version of the project using the deploy.py '
                    'script in /path/to/deployment/dir, run in a virtualenv '
                    'having the packages specified by '
                    '/path/to/deployent/dir/requirements.txt.')
    # Makes a venv. If there was one from last time, finds it (to save disk IO).
    # Peep- or pip-installs dxr/deployment/requirements.txt
    # Runs `venv/python dxr/deployment/deploy.py bootstrap`, which checks out the latest good version of the project and outputs project:/path/to/checkout.
    # Makes a new venv.
    # Peep- or pip-installs dxr/deployment/requirements.txt
    # (We can skip the previous 2 steps if the requirements are unchanged. A pip download cache should make none of this matter much.)
    # Runs `venv/python /path/to/checkout/.../deploy.py`, which builds the project as contained in the checkout and installs it

    # Better still, don't call deploy.py directly at all. I don't want to have to implement (or call a routine that implements) dispatching between the bootstrap and deploy modes in every deployment script. Instead, call python -m shiva --some-special-arg /the/deploy.py, and let it twiddle sys.path, import the deploy script, and call bootstrap() or deploy() within it. That way, all a deploy script author has to do is implement those 2 callables.
