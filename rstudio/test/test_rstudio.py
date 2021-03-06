import docker
from docker.errors import ContainerError

import logging

import pytest


LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'cmd,version_output', [('rstudio-server', ['1.2.5001\n',],),],
)
def test_cmd(cmd, version_output):
    """Ensures that rstudio is found in the PATH and that it returns the correct
    version. Other tests verify the correct versions for npm and node.
    """
    LOGGER.info(f'Test that rstudio {cmd} is correctly installed ...')
    client = docker.from_env()
    output = client.containers.run('illumidesk/rstudio', f'{cmd} version')
    output_decoded = output.decode('utf-8').split(' ')
    assert output_decoded[0:3] == version_output
    LOGGER.info(f'Output from command: {output_decoded[0:3]}')


def test_invalid_cmd():
    """Ensure that an invalid command returns a docker.errors.ContainerError
    """
    with pytest.raises(ContainerError):
        LOGGER.info('Test an invalid command ...')
        client = docker.from_env()
        client.containers.run('illumidesk/rstudio', 'foo --version')
