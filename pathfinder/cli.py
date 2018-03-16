# -*- coding: utf-8 -*-

"""Console script for pathfinder."""
from gevent import monkey  # isort:skip # noqa
monkey.patch_all()  # isort:skip # noqa

import logging
import os
import sys

import click
from raiden_libs.blockchain import BlockchainListener
from raiden_libs.contracts import ContractManager
from web3 import HTTPProvider, Web3

import pathfinder
from pathfinder.no_ssl_patch import no_ssl_verification
from pathfinder.pathfinding_service import PathfindingService
from pathfinder.transport import MatrixTransport

log = logging.getLogger(__name__)


@click.command()
@click.option(
    '--eth-rpc',
    default='http://localhost:8545',
    type=str,
    help='Ethereum node RPC URI'
)
@click.option(
    '--monitoring-channel',
    default='#monitor_test:transport01.raiden.network',
    help='Location of the monitoring channel to connect to'
)
@click.option(
    '--matrix-homeserver',
    default='https://transport01.raiden.network',
    help='Matrix homeserver'
)
@click.option(
    '--matrix-username',
    default=None,
    required=True,
    help='Matrix username'
)
@click.option(
    '--matrix-password',
    default=None,
    required=True,
    help='Matrix password'
)
def main(
    eth_rpc,
    monitoring_channel,
    matrix_homeserver,
    matrix_username,
    matrix_password
):
    """Console script for pathfinder."""

    # setup logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG)

    log.info("Starting Raiden Pathfinding Service")

    with no_ssl_verification():
        try:
            log.info('Starting Matrix Transport...')
            transport = MatrixTransport(
                matrix_homeserver,
                matrix_username,
                matrix_password,
                monitoring_channel
            )

            log.info('Starting Web3 client...')
            web3 = Web3(HTTPProvider(eth_rpc))

            module_dir = os.path.dirname(pathfinder.__file__)
            contracts_path = os.path.join(module_dir, 'contract', 'contracts_12032018.json')
            contract_manager = ContractManager(contracts_path)

            log.info('Starting Blockchain Monitor...')
            listener = BlockchainListener(
                web3,
                contract_manager,
                'TokenNetwork',
            )

            log.info('Starting Pathfinding Service...')
            service = PathfindingService(transport, listener)

            service.run()
        except (KeyboardInterrupt, SystemExit):
            print('Exiting...')
        finally:
            log.info('Stopping Pathfinding Service...')
            service.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
