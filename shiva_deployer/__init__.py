"""A reasonably generic [continuous] deployment framework"""

from shiva_deployer.deployment import AbstractDeployment
from shiva_deployer.exceptions import ShouldNotDeploy
from shiva_deployer.tools import cd, run, nonblocking_lock
