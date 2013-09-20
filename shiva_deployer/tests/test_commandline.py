"""Tests for the shiva commandline program"""

from nose.tools import eq_, assert_raises
from nose.util import src

from shiva_deployer.commandline import inner_main, wake_pickle
from shiva_deployer.exceptions import ShouldNotDeploy


def test_subcommand_success():
    """Make sure shiva finds and delegates to a Deployment instance method and
    extracts the result, when all goes well.

    """
    status, output = inner_main([src(__file__),
                                 '--shiva-subcommand',
                                 'get_lock_name'])
    eq_(wake_pickle(output), 'harvey')
    eq_(status, 0)


def test_subcommand_should_not_deploy():
    """If a shiva subcommand raises ShouldNotDeploy, it should get pickled and
    printed.

    """
    status, output = inner_main([src(__file__),
                                 '--shiva-subcommand',
                                 'check_out'])
    assert_raises(ShouldNotDeploy, wake_pickle, output)
    eq_(status, 0)


class Deployment(object):
    def __init__(self, argv):
        pass

    def get_lock_name(self):
        return 'harvey'

    def check_out(self):
        raise ShouldNotDeploy
